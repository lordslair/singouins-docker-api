#!/bin/sh
certbot certonly --logs-dir /var/www/certbot \
                 --webroot --webroot-path /var/www/certbot \
                 -d <CERTBOT_DOMAINS> \
                 --email <CERTBOT_EMAIL> \
                 --agree-tos \
                 --no-eff-email
