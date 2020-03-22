===============
SSL certificate
===============

Support for Letsencrypt certbot auto:

.. code-block:: bash

    ./certbot-auto certonly \
        --nginx \
        -d geralt.modelbrouwers.nl \
        -d mail.pi-modelling.nl \
        -n
