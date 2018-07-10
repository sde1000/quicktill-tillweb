# Access to till database

# By default we read the files 'database_name' and 'till_name' in the
# project root directory and set up tillweb in single-till read-only
# access mode.  If you want to do something different, replace the
# contents of this file.

import os

# They moved it again!  As of django-1.10 reverse is found in
# django.urls, but we need to retain compatibility with django-1.8
# while we are still targetting Ubuntu-16.04 LTS.
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

with open(os.path.join(base_dir, "database_name")) as f:
    TILLWEB_DATABASE_NAME = f.readline().strip()

TILLWEB_SINGLE_SITE = True
TILLWEB_DATABASE = sessionmaker(
    bind=create_engine(
        'postgresql+psycopg2:///{}'.format(TILLWEB_DATABASE_NAME),
        pool_size=32, pool_recycle=600),
    info={'pubname': '', 'reverse': reverse})
with open(os.path.join(base_dir, "till_name")) as f:
    TILLWEB_PUBNAME = f.readline().strip()
TILLWEB_LOGIN_REQUIRED = True
TILLWEB_DEFAULT_ACCESS = "R"

