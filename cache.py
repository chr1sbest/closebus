import redis
from json import loads
from datetime import datetime
from functools import wraps

redis_cache = redis.StrictRedis()

def request_cache(ttl_seconds=300):
    """
    Retrieve values from Redis if available. Otherwise, execute the
    function and store arguments -> result (and TTL) in the redis cache.

    Cache entries expire after 300 seconds by default.
    """
    def request_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            cached = redis_cache.get(kwargs)
            #remaining_time = redis_cache.ttl(kwargs)
            if cached:
                return loads(cached)
            else:
                result = func(self, *args, **kwargs)
                redis_cache.setex(kwargs, ttl_seconds, result)
            return result
        return wrapper
    return request_decorator

