# Access to till database

# By default we read the files 'database_name' and 'till_name' in the
# project root directory and set up tillweb in single-till read-only
# access mode.  If you want to do something different, replace the
# contents of this file.

import os

from django.urls import reverse

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
    info={'pubname': 'detail', 'reverse': reverse})
with open(os.path.join(base_dir, "till_name")) as f:
    TILLWEB_PUBNAME = f.readline().strip()
TILLWEB_LOGIN_REQUIRED = True
TILLWEB_DEFAULT_ACCESS = "R"

from datetime import datetime
# start, end, weight
EVENT_TIMES = [
    (datetime(2018, 8, 31, 11, 0), datetime(2018, 9, 1, 1, 30), 2.0),
    (datetime(2018, 9, 1, 11, 0), datetime(2018, 9, 2, 1, 30), 2.0),
    (datetime(2018, 9, 2, 11, 0), datetime(2018, 9, 3, 0, 30), 1.0),
]
