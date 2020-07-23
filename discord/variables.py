# -*- coding: utf8 -*-

import os

# Discord variables
token   = os.environ['TOKEN']

# MySQL variables
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
DB_NAME = os.environ['DB_NAME']
DB_HOST = os.environ['DB_HOST']

# SQLAlchemy variables
SQL_DSN = DB_USER + ':' + DB_PASS + '@' + DB_HOST + ':3306/' + DB_NAME
