import os
import json
import unittest
import redis
import time
from json import loads
from functools import wraps
from redis_cache import cache_decorator

url = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379')
redis_cache = redis.from_url(url + ':6379')

class RedisTest(unittest.TestCase):
    def test_set(self):
        redis_cache.set('testing', 'hello')
        self.assertEqual(redis_cache.get('testing'), 'hello')

    def test_setex(self):
        redis_cache.setex('testing2', 'hi again', 10)
        time.sleep(1)
        self.assertEqual(redis_cache.get('testing2'), 'hi again')
        self.assertEqual(redis_cache.ttl('testing2') < 10, True)

    def test_decorator_expiration(self):
        class Temp(object):
            @cache_decorator(expire=True, ttl_seconds=1)
            def some_func(self, x=None):
                return json.dumps('hello')
        a = Temp()
        a.some_func(x='testing')
        self.assertEqual(redis_cache.get("{'x': 'testing'}"), '"hello"')
        time.sleep(2)
        self.assertEqual(redis_cache.get("{'x': 'testing'}"), None)

    def tearDown(self):
        redis_cache.delete('testing')
        redis_cache.delete('testing2')
