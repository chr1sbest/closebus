import os
import urlparse

API_KEY = os.environ.get('API_KEY', None)

try:
    from local_settings import *
except ImportError:
    pass
