# -*- coding: utf8 -*-

import os

# JWT variables
SEP_SECRET_KEY = os.environ['SEP_SECRET_KEY']

# MySQL variables
MYSQL_USER     = os.environ['SEP_MYSQL_USER']
MYSQL_PASSWORD = os.environ['SEP_MYSQL_PASSWORD']
MYSQL_DB       = os.environ['SEP_MYSQL_DB']
MYSQL_HOST     = os.environ['SEP_MYSQL_HOST']

# SQLAlchemy variables
SQL_DSN        = MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + ':3306/' + MYSQL_DB

# External URL
API_URL        = os.environ['SEP_API_URL']

# Latest commit used in this apps
SEP_SHA        = open('/code/.git', 'r').read().rstrip()

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB_NAME = 0

# PCS variables for remote storage
PCS_URL       = os.environ['SEP_PCS_URL']

# Discord permanent invite link
DISCORD_URL   = os.environ['SEP_DISCORD_URL']

# LDP credentials for log forwarding
LDP_HOST      = os.environ['SEP_LDP_HOST']
LDP_TOKEN     = os.environ['SEP_LDP_TOKEN']
