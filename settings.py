import os

API_KEY = os.environ.get('API_KEY', None)
REDIS_URL = os.environ.get('REDISTOGO_URL', None)

try:
    from local_settings import *
except ImportError:
    pass
