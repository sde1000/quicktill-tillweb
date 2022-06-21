Till web service
================

Minimal infrastructure needed to bring up an instance of
`quicktill.tillweb` as a uwsgi service.

Setup
-----

Ensure you have [poetry](https://python-poetry.org/)
installed. Installation instructions are on
[this page](https://python-poetry.org/docs/master/).

You should have a copy of `quicktill` unpacked in the directory above
the one containing this file. If you don't, you can get one as
follows:

```
git clone https://github.com/sde1000/quicktill.git ../quicktill
```

Install the project dependencies:

```
poetry install
```

To configure, create the following files in the same directory as this README:

 * a random secret in the file `secret_key`

 * the name of the till database in the file `database_name`

 * the name of the site served by the till in the file `till_name`

 * the currency symbol used by the till in the file `currency_symbol`

Create the Django database and an initial admin user:

```
poetry run ./manage.py migrate
poetry run ./manage.py createsuperuser
```

To start a web server on http://localhost:8000/ to test the service:
```
poetry run ./manage.py runserver
```

Installation
------------

As root:

* copy `tillweb-nginx-configuration` to `/etc/nginx/sites-available/tillweb`
and edit it as appropriate.
* delete `/etc/nginx/sites-enabled/default` and symlink
`/etc/nginx/sites-available/tillweb` to `/etc/nginx/sites-enabled/tillweb`
* run `loginctl enable-linger your-username` to enable the service to run
while you are not logged in

As the user that will run the service:

Copy `systemd/tillweb.service` to `~/.config/systemd/user/` and enable it:

```
mkdir -p ~/.config/systemd/user
cp systemd/tillweb.service ~/.config/systemd/user/
systemctl --user enable tillweb.service
systemctl --user start tillweb.service
```

Outside of the scope of these instructions: set up DNS entries and
letsencrypt so you can access the service over https.
