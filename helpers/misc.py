"""Misc helpers."""
import operator
from collections import defaultdict
from functools import reduce
from django.conf import settings
from django.db.models import Q
from django.db.models import Count
from django.db.models import Case, When
from bs4 import BeautifulSoup
from users.models import UserProfile
from other.search import run_query_sync

def get_url_friendly(name):
    """Converts the name to a url friendly string for use in `str_id`"""
    # Return blank in case None is passed
    if not name:
        return ''

    # Strip whitespaces and replace with dashes
    temp = '-'.join(name.lower().split())

    # Remove special characters except dashes
    return ''.join(c for c in temp if c.isalnum() or c == '-')

def query_from_num(request, default_num, queryset):
    """Returns queryset with from and num if the query parameters are valid."""
    # Initialize defaults
    from_i = 0
    num = default_num

    # Set values from query paramters if available and valid
    from_q = request.GET.get('from')
    num_q = request.GET.get('num')
    if from_q is not None and str.isdigit(from_q):
        from_i = int(from_q)
    if num_q is not None and str.isdigit(num_q) and int(num_q) <= 100:
        num = int(num_q)

    return queryset[from_i: from_i + num]

def query_search(  # pylint: disable=too-many-arguments
        request, min_length, queryset, fields, collection, order_relevance=False):
    """Returns queryset with search filter."""
    search = request.GET.get('query')
    if search is not None and len(search) >= min_length:
        # Use a FTS backend if we have one
        if settings.USE_SONIC:
            ids = run_query_sync(collection, search)
            queryset = queryset.filter(id__in=ids)

            # Preserve order of returned results
            if order_relevance:
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
                queryset = queryset.order_by(preserved)

            return queryset

        # Fallback if we are so quiet ;)
        return query_search_fallback(queryset, fields, search)  # pragma: no cover

    return queryset

def query_search_fallback(queryset, fields, search):  # pragma: no cover
    """Perform query search by falling back to icontains."""
    all_queries = Q()
    for field in fields:
        all_queries = all_queries | Q(**{field + '__icontains': search})
    return queryset.filter(all_queries)

def sort_by_field(queryset, field, reverse=False, filt=None):
    """Return a queryset ordered by a field"""
    queryset = queryset.annotate(field_count=Count(field, filter=filt))
    return queryset.order_by(('-' if reverse else '') + 'field_count')

def table_to_markdown(html):
    # Initialize
    md = ''
    MAX_COLS = 0
    HEADER_SEPARATOR = 'HEADER_SEPARATOR'

    # Parse
    SOUP = BeautifulSoup(html, features='html.parser')

    # Count maximum columns
    for row in SOUP.find_all('tr'):
        cols = row.find_all(['td', 'th'])
        MAX_COLS = max(MAX_COLS, len(cols))

    if MAX_COLS == 0:
        return md

    if MAX_COLS == 1:
        for row in SOUP.find_all('tr'):
            md += row.find(['td', 'th']).text.replace('\n', '') + '\n'
        return md

    # Iterate all rows and columns
    for i, row in enumerate(SOUP.find_all('tr')):
        # Iterate all columns
        cols = row.find_all(['td', 'th'])
        for col in cols:
            txt = col.text.replace('\n', '')
            md += txt + '&zwnj; | '

        if len(cols) < MAX_COLS:
            md += '&zwnj; | ' * (MAX_COLS - len(cols))

        # Insert newline after each row
        md += '\n'

        # Insert header and separator placeholder
        if i == 0:
            md += HEADER_SEPARATOR + '\n'

    # Replace header separator
    md = md.replace(HEADER_SEPARATOR, '---|' * MAX_COLS)

    return md

def users_from_tags(tags):
    """Get a queryset of UserProfile from list of tags."""

    # Check if no tags are passed
    if not tags:
        return UserProfile.objects.all()

    # Divide AND and OR categories
    categories = defaultdict(list)
    for tag in tags:
        categories[tag.category_id].append(tag)

    # Helper to get Q object from tag
    def get_query(tag):
        query = Q(**{"%s__regex" % tag.target: tag.regex})
        if tag.secondary_target and tag.secondary_regex:
            t_null_q = Q(**{"%s__isnull" % tag.target: True}) | Q(**{"%s__exact" % tag.target: ''})
            secondary_q = Q(**{"%s__regex" % tag.secondary_target: tag.secondary_regex})
            query = query | (t_null_q & secondary_q)
        return query

    # Construct the query
    clauses = []
    for c in categories:
        queries = (get_query(t) for t in categories[c])
        clauses.append(reduce(operator.or_, queries))
    query = reduce(operator.and_, clauses)

    return UserProfile.objects.filter(query)
