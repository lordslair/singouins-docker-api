# -*- coding: utf8 -*-

import os

# Discord variables
token   = os.environ['TOKEN']

# MySQL variables
MYSQL_USER     = os.environ['SEP_MYSQL_USER']
MYSQL_PASSWORD = os.environ['SEP_MYSQL_PASSWORD']
MYSQL_DB       = os.environ['SEP_MYSQL_DB']
MYSQL_HOST     = os.environ['SEP_MYSQL_HOST']

# SQLAlchemy variables
SQL_DSN        = MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOST + ':3306/' + MYSQL_DB

# Redis variables
REDIS_HOST    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_HOST']
REDIS_PORT    = os.environ['SEP_BACKEND_REDIS_SVC_SERVICE_PORT']
REDIS_DB_NAME = 0
