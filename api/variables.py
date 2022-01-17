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

# LDP credentials for log forwarding
LDP_HOST      = os.environ['SEP_LDP_HOST']
LDP_TOKEN     = os.environ['SEP_LDP_TOKEN']

# Token used for /internal routes
API_ADMIN_TOKEN    = os.environ['SEP_ADMIN_TOKEN']
API_INTERNAL_TOKEN = os.environ['SEP_INTERNAL_TOKEN']
