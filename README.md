Till web service
================

Minimal infrastructure needed to bring up a read-only instance of
quicktill.tillweb as a uwsgi service.

Setup
-----

To configure, create the following files in the same directory as this README:

 * a random secret in the file `secret_key`

 * the name of the till database in the file `database_name`

 * the name of the site served by the till in the file `till_name`

 * the currency symbol used by the till in the file `currency_symbol`

Create a python3 virtualenv called `venv` and install all the
requirements from `requirements.txt` in it:

```virtalenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

You may need to `export PYTHONPATH=/path/to/quicktill` if you haven't
installed quicktill in the virtualenv.

Run `./manage.py migrate` to create the Django database, and
`./manage.py createsuperuser` to create an initial admin user.

At this point you should be able to run `./start-testserver` to start
a webserver on localhost:8000 to test the installation.

Installation
------------

As root, copy `tillweb-nginx-configuration` to
`/etc/nginx/sites-available/tillweb` and edit it as appropriate.

Delete /etc/nginx/sites-enabled/default and symlink
/etc/nginx/sites-available/tillweb to /etc/nginx/sites-enabled/tillweb

Arrange for `./start-daemon` to be run at boot to start uwsgi serving
the website.  You may need to arrange for quicktill to be on the
PYTHONPATH if it isn't in the virtualenv.
