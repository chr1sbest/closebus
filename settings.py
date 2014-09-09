import os

CTA_KEY = os.environ.get('CTA_KEY', None)

try:
    from local_settings import *
except ImportError:
    pass
