import redis
import os
import mockredis
from json import loads
from functools import wraps

# Attempt to connect to remote Redis instance if available. Otherwise
# connect to a local Redis instance if available, or mock for tests.
try:
    url = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379')
    redis_cache = redis.from_url(url + ':6379')
    redis_cache.ping()
except redis.ConnectionError:
    redis_cache = mockredis.mock_redis_client()

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
