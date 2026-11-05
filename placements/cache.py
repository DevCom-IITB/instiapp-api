import json
from django.conf import settings
from redis import Redis
from placements.models import BlogEntry
from placements.serializers import BlogEntrySerializer

# Connect to Redis (uses localhost:6379, DB 1 or configured URL)
REDIS_URL = getattr(settings, "REDIS_CACHE_URL", "redis://127.0.0.1:6379/1")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

CACHE_TTL = 600  # 10 minutes TTL


def get_top_100_blogs(blog_type: str, blog_url: str):
    """Fetch top 100 blogs from Redis, falling back to DB on cache miss."""
    cache_key = f"blogs_top100_{blog_type}"

    # 1. Try fetching from Redis
    try:
        raw_data = redis_client.get(cache_key)
        if raw_data:
            return json.loads(raw_data)
    except Exception as e:
        print(f"[Redis Cache Error] {e}")

    # 2. Cache Miss: Query Database for the latest 100 posts
    queryset = BlogEntry.objects.filter(blog_url=blog_url).order_by("-published")[:100]
    posts = BlogEntrySerializer(queryset, many=True).data

    # 3. Store in Redis with TTL
    try:
        redis_client.set(cache_key, json.dumps(posts), ex=CACHE_TTL)
    except Exception as e:
        print(f"[Redis Set Error] {e}")

    return posts


def invalidate_blog_cache(blog_type: str = None):
    """Delete Redis cache key when a new blog is scraped."""
    try:
        if blog_type:
            redis_client.delete(f"blogs_top100_{blog_type}")
        else:
            redis_client.delete("blogs_top100_placement", "blogs_top100_training")
    except Exception as e:
        print(f"[Redis Delete Error] {e}")

