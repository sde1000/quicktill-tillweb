Till web service
================

Minimal infrastructure needed to bring up a read-only instance of
quicktill.tillweb as a uwsgi service.

Ensure python3-django, nginx, uwsgi-plugin-python3 and quicktill3 are
installed.

If tillweb is still using matplotlib to draw pie charts,
python3-matplotlib may be required as well.

To configure, put a random secret in the file "secret_key", the name
of the till database in the file "database_name" and the title for the
till pages in the file "till_name" in the same directory as this
README.md file.

Run ./manage.py migrate to create the Django database.

As root, copy tillweb-nginx-configuration to
/etc/nginx/sites-available/tillweb

Delete /etc/nginx/sites-enabled/default and symlink
/etc/nginx/sites-available/tillweb to /etc/nginx/sites-enabled/tillweb
