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
