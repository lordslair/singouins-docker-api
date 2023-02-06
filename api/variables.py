# -*- coding: utf8 -*-

import os

# JWT variables
SEP_SECRET_KEY = os.environ['SEP_SECRET_KEY']

# MySQL variables
MYSQL_USER     = os.environ.get("SEP_MYSQL_USER")
MYSQL_PASSWORD = os.environ.get("SEP_MYSQL_PASSWORD")
MYSQL_DB       = os.environ.get("SEP_MYSQL_DB")
MYSQL_HOST     = os.environ.get("SEP_MYSQL_HOST", '127.0.0.1')
MYSQL_PORT     = os.environ.get("SEP_MYSQL_PORT", 3306)

# SQLAlchemy variables
SQL_DSN        = (f'{MYSQL_USER}:{MYSQL_PASSWORD}@'
                  f'{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}')

# External URL
API_URL        = os.environ.get("SEP_API_URL", 'http://127.0.0.1:5000')

# Redis variables
REDIS_HOST    = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_HOST",
                               '127.0.0.1')
REDIS_PORT    = os.environ.get("SEP_BACKEND_REDIS_SVC_SERVICE_PORT", 6379)
REDIS_DB_NAME = os.environ.get("SEP_REDIS_DB", 0)

# PCS variables for remote storage
PCS_URL       = os.environ.get("SEP_PCS_URL", 'http://127.0.0.1')

# Discord permanent invite link
DISCORD_URL   = os.environ.get("SEP_DISCORD_URL", 'http://127.0.0.1')
# Resolver variables
RESOLVER_HOST    = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_HOST",
                                  '127.0.0.1')
RESOLVER_PORT    = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_PORT",
                                  5000)
RESOLVER_URL     = f'http://{RESOLVER_HOST}:{RESOLVER_PORT}'

# Gunicorn variables
GUNICORN_CHDIR   = os.environ.get("GUNICORN_CHDIR", '/code')
GUNICORN_HOST    = os.environ.get("GUNICORN_HOST", "0.0.0.0")
GUNICORN_PORT    = os.environ.get("GUNICORN_PORT", 5000)
GUNICORN_BIND    = f'{GUNICORN_HOST}:{GUNICORN_PORT}'
GUNICORN_WORKERS = os.environ.get("GUNICORN_WORKERS", 1)
GUNICORN_THREADS = os.environ.get("GUNICORN_THREADS", 2)
GUNICORN_RELOAD  = os.environ.get("GUNICORN_RELOAD", True)

# YarQueue variables
YQ_BROADCAST = os.environ.get("SEP_YQ_BROADCAST", 'yarqueue:broadcast')
YQ_DISCORD   = os.environ.get("SEP_YQ_DISCORD", 'yarqueue:discord')

# GitHub check to position relative paths correctly
if os.environ.get("CI"):
    # Here we are inside GitHub CI process
    DATA_PATH   = 'api/data'
else:
    DATA_PATH   = 'data'
