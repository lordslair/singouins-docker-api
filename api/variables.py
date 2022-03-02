# -*- coding: utf8 -*-

import os

# JWT variables
SEP_SECRET_KEY = os.environ['SEP_SECRET_KEY']

# MySQL variables
MYSQL_USER     = os.environ['SEP_MYSQL_USER']
MYSQL_PASSWORD = os.environ['SEP_MYSQL_PASSWORD']
MYSQL_DB       = os.environ['SEP_MYSQL_DB']
MYSQL_HOST     = os.environ['SEP_MYSQL_HOST']
MYSQL_PORT     = os.environ['SEP_MYSQL_PORT']

# SQLAlchemy variables
SQL_DSN        = MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + ':' + MYSQL_PORT + '/' + MYSQL_DB

# External URL
API_URL        = os.environ['SEP_API_URL']

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB_NAME = os.environ['SEP_REDIS_DB']

# PCS variables for remote storage
PCS_URL       = os.environ['SEP_PCS_URL']

# Discord permanent invite link
DISCORD_URL   = os.environ['SEP_DISCORD_URL']

# Token used for /internal routes
API_INTERNAL_TOKEN = os.environ['SEP_INTERNAL_TOKEN']

# Resolver variables
RESOLVER_HOST    = os.environ['SEP_BACKEND_RESOLVER_SVC_SERVICE_HOST']
RESOLVER_PORT    = os.environ['SEP_BACKEND_RESOLVER_SVC_SERVICE_PORT']

# Gunicorn variables
GUNICORN_CHDIR   = os.environ.get("GUNICORN_CHDIR", '/code')
GUNICORN_HOST    = os.environ.get("GUNICORN_HOST", "0.0.0.0")
GUNICORN_PORT    = os.environ.get("GUNICORN_PORT", 5000)
GUNICORN_BIND    = f'{GUNICORN_HOST}:{GUNICORN_PORT}'
GUNICORN_WORKERS = os.environ.get("GUNICORN_WORKERS", 1)
GUNICORN_THREADS = os.environ.get("GUNICORN_THREADS", 2)
GUNICORN_RELOAD  = os.environ.get("GUNICORN_RELOAD", True)
