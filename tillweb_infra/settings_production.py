# Django settings for production use

from .settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

STATIC_ROOT = os.path.join(BASE_DIR, "static")

ALLOWED_HOSTS = ['*']
