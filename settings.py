import os
import urlparse

API_KEY = os.environ.get('API_KEY', None)
REDIS_URL = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost'))

try:
    from local_settings import *
except ImportError:
    pass
