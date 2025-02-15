"""Django settings for emftill project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# This is the base settings file.  In production use, this file is
# imported by settings_production.py and some settings are added
# and/or changed.

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

# BASE_DIR is the root of the whole project, i.e. the directory where
# the manage.py script is
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
with open(os.path.join(BASE_DIR, "secret_key")) as f:
    SECRET_KEY = f.readline().strip()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admindocs',
    'django_bootstrap_breadcrumbs',
    'widget_tweaks',
    'quicktill.tillweb',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'tillweb_infra.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tillweb_infra.context_processors.pubname_setting',
            ],
        },
    },
]

WSGI_APPLICATION = 'tillweb_infra.wsgi.application'

# The stock-take data entry page can have LOTS of small fields.  We
# need to raise this parameter from the default of 1000 for large stock-takes.
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Type for auto-created primary keys (new in django-3.2)

# In previous releases of Django this was implicitly
# 'django.db.models.AutoField'; the new default is explicitly
# 'django.db.models.BigAutoField'.

# If this default is changed, migrations are currently NOT generated
# automatically.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-GB'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static-dist"),
]

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: "/accounts/users/%d/" % o.id,
}

# Messages system: set Bootstrap theme tags for message tags
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-primary',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Till database access

from .settings_database import *

# Feature flags
FOOD_MENU_EDITOR = True

# Currency symbol
with open(os.path.join(BASE_DIR, "currency_symbol")) as f:
    TILLWEB_MONEY_SYMBOL = f.readline().strip()

# Logging - when running testserver, output SQL queries and responses
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
#    'loggers': {
#        'sqlalchemy.engine': {
#            'handlers': ['console'],
#            'level': 'DEBUG',
#        },
#    },
}
