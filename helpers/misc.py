"""Misc helpers."""
from django.db.models import Q

def get_url_friendly(name):
    """Converts the name to a url friendly string for use in `str_id`"""
    temp = "-".join(name.lower().split())
    return "".join(c for c in temp if c.isalnum() or c == "-")

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

    return queryset[from_i : from_i + num]

def query_search(request, min_length, queryset, fields):
    """Returns queryset with search filter."""
    search = request.GET.get('query')
    if search is not None and len(search) >= min_length:
        all_queries = Q()
        for field in fields:
            all_queries = all_queries | Q(**{field + '__icontains' : search})
        return queryset.filter(all_queries)

    return queryset
