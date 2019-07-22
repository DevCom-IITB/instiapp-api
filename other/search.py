import re
from asonic import Client as SonicClient
from asonic.enums import Channels as SonicChannels

from django.conf import settings
from other.asyncio_run import run_sync

DEFAULT_BUCKET = 'bucket'

async def push(pairs):
    c = SonicClient(**settings.SONIC_CONFIG)
    await c.channel(SonicChannels.INGEST.value)
    for pair in pairs:
        try:
            await c.push(*pair)
        except Exception as e:  # pylint: disable=broad-except
            print('Failed to push %s to %s, %s' % (pair[2], pair[0], e))
            continue

async def consolidate():
    c = SonicClient(**settings.SONIC_CONFIG)
    await c.channel(SonicChannels.CONTROL.value)
    await c.trigger('consolidate')

async def run_query(collection: str, query: str, bucket=DEFAULT_BUCKET):
    def remove_small(string):
        return ' '.join(x for x in string.split(' ') if len(x) > 3)

    # Run basic query
    c = SonicClient(**settings.SONIC_CONFIG)
    await c.channel(SonicChannels.SEARCH.value)
    res = await c.query(collection, bucket, query)
    res += [x for x in await c.query(
        collection, bucket, remove_small(query)) if x not in res]

    # Run suggestions for last word
    lw = query.split(' ')[-1]
    if len(lw) >= 3:
        # Get word suggestions
        suggestions = await c.suggest(collection, bucket, lw, 4)

        # Query after adding each word
        for s in suggestions:
            q = '%s %s' % (query, s.decode('utf-8'))
            res += [x for x in await c.query(
                collection, bucket, remove_small(q)) if x not in res]

    return [x.decode("utf-8") for x in res]

def index_pair(obj):  # pylint: disable=too-many-return-statements
    def space(*args):
        return re.sub(r'\W+', ' ', ' '.join(str(x) for x in args))

    typ = type(obj).__name__
    bucket = DEFAULT_BUCKET

    if typ == 'Body':
        return ('bodies', bucket, str(obj.id), space(obj.name, obj.description, obj.short_description))

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
    return run_sync(push([index_pair(obj)]))

def run_query_sync(collection: str, query: str, bucket=DEFAULT_BUCKET):
    return run_sync(run_query(collection, query, bucket))
