import re
from contextlib import suppress

from asonic import Client as SonicClient
from asonic.enums import Channel as SonicChannel
from asonic.enums import Action as SonicAction

from bs4 import BeautifulSoup
from markdown import markdown

from django.conf import settings
from other.asyncio_run import run_sync

DEFAULT_BUCKET = 'bucket'

async def push(pair, client=None):
    if not client:
        client = SonicClient(**settings.SONIC_CONFIG)
        await client.channel(SonicChannel.INGEST)
    try:
        await client.push(*pair)
    except Exception as e:  # pylint: disable=broad-except
        print('Failed to push %s, %s' % (pair, e))

async def consolidate():
    c = SonicClient(**settings.SONIC_CONFIG)
    await c.channel(SonicChannel.CONTROL)
    await c.trigger(SonicAction.CONSOLIDATE)

async def run_query(collection: str, query: str, bucket=DEFAULT_BUCKET):
    async def query_small(string):
        f = [x for x in string.split(' ') if len(x) > 3]
        return await c.query(collection, bucket, ' '.join(f)) if f else []

    # Run basic query
    c = SonicClient(**settings.SONIC_CONFIG)
    await c.channel(SonicChannel.SEARCH)
    res = await c.query(collection, bucket, query)
    res += [x for x in await query_small(query) if x not in res]

    # Run suggestions for last word
    lw = query.split(' ')[-1]
    if len(lw) >= 3:
        # Get word suggestions
        suggestions = await c.suggest(collection, bucket, lw, 4)

        # Query after adding each word
        for s in suggestions:
            q = '%s %s' % (query.rsplit(' ', 1)[0], s.decode('utf-8'))
            res += [x for x in await query_small(q) if x not in res]

    return [x.decode("utf-8") for x in res]

def index_pair(obj):  # pylint: disable=too-many-return-statements
    # Remove non-alphanumeric
    safe_re = re.compile(r'\W+')
    # Remove short words
    short_re = re.compile(r'\W*\b\w{1,2}\b')

    def space(*args):
        # Get joined text
        text = ' '.join(str(x) for x in args)

        # Render markdown to HTML
        with suppress(Exception):
            soup = BeautifulSoup(markdown(text), features='html.parser')

            # Remove script and styles
            for s in soup(['script', 'style', 'meta', 'noscript']):
                s.decompose()

            # Get text
            text = soup.get_text()

        # Remove unsafe stuff
        safe = safe_re.sub(' ', text)
        return short_re.sub('', safe)[:settings.SONIC_MAX_LEN]

    typ = type(obj).__name__
    bucket = DEFAULT_BUCKET

    if typ == 'Body':
        return ('bodies', bucket, str(obj.id), space(obj.name, obj.short_description, obj.description))

    if typ == 'Event':
        return ('events', bucket, str(obj.id), space(obj.name, obj.description))

    if typ == 'UserProfile':
        return ('profiles', bucket, str(obj.id), space(obj.name, obj.ldap_id, obj.roll_no))

    if typ == 'BlogEntry':
        val = space(obj.title, obj.content)
        if obj.blog_url == settings.TRAINING_BLOG_URL:
            return ('training', bucket, str(obj.id), val)
        if obj.blog_url == settings.PLACEMENTS_URL:
            return ('placement', bucket, str(obj.id), val)
        return ('blogs', bucket, str(obj.id), val)

    if typ == 'NewsEntry':
        return ('news', bucket, str(obj.id), space(obj.title, obj.content))

def push_obj_sync(obj):
    return run_sync(push(index_pair(obj)))

def run_query_sync(collection: str, query: str, bucket=DEFAULT_BUCKET):
    return run_sync(run_query(collection, query, bucket))
