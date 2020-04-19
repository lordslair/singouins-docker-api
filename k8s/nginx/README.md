# nginx - SSL configuration details

Using this instructions ended up with an A+ rating on sslabs.com

Useful informations:  
It supposes considering the paths, that letsencrypt.org is the SSL certificates supplier.  
Certbot generates certificates in /etc/letsencrypt
Certbot working dir is /var/www/certbot
These directories are volumes shared by nginx and the certbot container

nginx conf regarding SSL :  
(These lines have to be placed inside a server{} block, on port 443)

```
# https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_certificate
ssl_certificate     /etc/letsencrypt/live/<URL>/fullchain.pem; # public key
ssl_certificate_key /etc/letsencrypt/live/<URL>/privkey.pem;   # private key

# https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_session_cache
# 1M ~ 4000 sessions - validity: 24hours
ssl_session_cache   shared:SSL:10m;
ssl_session_timeout 1440m;
ssl_session_tickets off;

# https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_protocols
# We use only recent and secure protocols. no TLS1.0/1.1, no SSLv2/3
ssl_protocols TLSv1.2 TLSv1.3;

# https://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_ciphers
# https://wiki.mozilla.org/Security/Server_Side_TLS
# Moderate/Strong cipher suite served in server-preferred order      
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;

# https://www.nginx.com/blog/http-strict-transport-security-hsts-and-nginx/
# Forces the browser to strictly upgrade the connection to HTTPS
# For testing purposes, use a short max-age, or it will not be possible to back out to HTTP
add_header Strict-Transport-Security 'max-age=63072000; includeSubDomains; preload;' always;
```

nginx conf regarding the challenge
(These lines have to be placed inside a server{} block, on port 80)

```
location /.well-known/acme-challenge/ {
    root /var/www/certbot;
}
```

For the first certificate initialization:  
- Fill the CERTBOT_DOMAINS and CERTBOT_EMAIL in certbot-init.sh  
- Add the location in nginx for the certbot to do his challenge  
- Execute certbot-init.sh inside certbot/certbot container to issue the certs  

And it should work:  
```
/opt/certbot # certbot-init.sh
Saving debug log to /var/www/certbot/letsencrypt.log
Plugins selected: Authenticator webroot, Installer None
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for URL
Using the webroot path /var/www/certbot for all unmatched domains.
Waiting for verification...
Cleaning up challenges

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
 /etc/letsencrypt/live/URL/fullchain.pem
Your key file has been saved at:
/etc/letsencrypt/live/URL/privkey.pem
 ```
