import redis
import os
import urlparse
from json import loads
from functools import wraps

url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost'))
redis_cache = redis.Redis(url)

def cache_decorator(expire=True, ttl_seconds=300):
    """
    Retrieve values from Redis if available. Otherwise, execute the
    function and store arguments -> result (and TTL) in the redis cache.

    Cache entries expire after 300 seconds by default.
    """
    def request_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cached = redis_cache.get(kwargs)
            if cached:
                return loads(cached)
            else:
                result = func(self, *args, **kwargs)
                if expire == True:
                    redis_cache.setex(kwargs, result, ttl_seconds)
                else:
                    redis_cache.set(kwargs, result)
            return loads(result)
        return wrapper
    return request_decorator
