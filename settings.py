import os

try:
    from local_settings import API_KEY
except ImportError:
    API_KEY = os.environ.get('API_KEY')
