# -*- coding: utf8 -*-

import os

# JWT variables
SEP_SECRET_KEY = eval(os.environ['SEP_SECRET_KEY'])

# MySQL variables
MYSQL_USER     = eval(os.environ['SEP_MYSQL_USERY'])
MYSQL_PASSWORD = eval(os.environ['SEP_MYSQL_PASSWORDY'])
MYSQL_DB       = eval(os.environ['SEP_MYSQL_DBY'])
MYSQL_HOST     = eval(os.environ['SEP_MYSQL_HOSTY'])
