Apache + mod-wsgi configuration
===============================

An example Apache2 vhost configuration follows::

    WSGIDaemonProcess postfixer-<target> threads=5 maximum-requests=1000 user=<user> group=staff
    WSGIRestrictStdout Off

    <VirtualHost *:80>
        ServerName my.domain.name

        ErrorLog "/srv/sites/postfixer/log/apache2/error.log"
        CustomLog "/srv/sites/postfixer/log/apache2/access.log" common

        WSGIProcessGroup postfixer-<target>

        Alias /media "/srv/sites/postfixer/media/"
        Alias /static "/srv/sites/postfixer/static/"

        WSGIScriptAlias / "/srv/sites/postfixer/src/postfixer/wsgi/wsgi_<target>.py"
    </VirtualHost>


Nginx + uwsgi + supervisor configuration
========================================

Supervisor/uwsgi:
-----------------

.. code::

    [program:uwsgi-postfixer-<target>]
    user = <user>
    command = /srv/sites/postfixer/env/bin/uwsgi --socket 127.0.0.1:8001 --wsgi-file /srv/sites/postfixer/src/postfixer/wsgi/wsgi_<target>.py
    home = /srv/sites/postfixer/env
    master = true
    processes = 8
    harakiri = 600
    autostart = true
    autorestart = true
    stderr_logfile = /srv/sites/postfixer/log/uwsgi_err.log
    stdout_logfile = /srv/sites/postfixer/log/uwsgi_out.log
    stopsignal = QUIT

Nginx
-----

.. code::

    upstream django_postfixer_<target> {
      ip_hash;
      server 127.0.0.1:8001;
    }

    server {
      listen :80;
      server_name  my.domain.name;

      access_log /srv/sites/postfixer/log/nginx-access.log;
      error_log /srv/sites/postfixer/log/nginx-error.log;

      location /500.html {
        root /srv/sites/postfixer/src/postfixer/templates/;
      }
      error_page 500 502 503 504 /500.html;

      location /static/ {
        alias /srv/sites/postfixer/static/;
        expires 30d;
      }

      location /media/ {
        alias /srv/sites/postfixer/media/;
        expires 30d;
      }

      location / {
        uwsgi_pass django_postfixer_<target>;
      }
    }
