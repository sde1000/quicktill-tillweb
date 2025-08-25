"""Django settings for emftill project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

from django.urls import reverse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# This is the base settings file.  In production use, this file is
# imported by settings_production.py and some settings are added
# and/or changed.

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
with open(BASE_DIR / 'config' / 'secret_key') as f:
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
        'DIRS': [
            BASE_DIR / "templates",
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
        'NAME': BASE_DIR / 'database' / 'db.sqlite3',
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

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static-dist",
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / "media"

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

# Currency symbol
with open(BASE_DIR / "config" / "currency_symbol") as f:
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

# Access to till database

# We read the files 'database_name' and 'till_name' in the config
# directory and set up tillweb in single-till mode.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

with open(BASE_DIR / "config" / "database_name") as f:
    TILLWEB_DATABASE_NAME = f.readline().strip()

TILLWEB_SINGLE_SITE = True
TILLWEB_DATABASE = sessionmaker(
    bind=create_engine(
        'postgresql+psycopg2:///{}'.format(TILLWEB_DATABASE_NAME),
        pool_size=32, pool_recycle=600, future=True),
    info={'pubname': 'detail', 'reverse': reverse}, future=True)
with open(BASE_DIR / "config" / "till_name") as f:
    TILLWEB_PUBNAME = f.readline().strip()
TILLWEB_LOGIN_REQUIRED = True
TILLWEB_DEFAULT_ACCESS = "M"
