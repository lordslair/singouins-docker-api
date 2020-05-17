# -*- coding: utf8 -*-

import os

# SMTP variables
SMTP_FROM     = os.environ['SEP_SMTP_FROM']
SMTP_SERVER   = os.environ['SEP_SMTP_SERVER']
SMTP_USER     = os.environ['SEP_SMTP_USER']
SMTP_PASS     = os.environ['SEP_SMTP_PASS']
SMTP_HOSTNAME = os.environ['SEP_SMTP_HOSTNAME']

# Redis variables
REDIS_HOST    = os.environ['SEP_REDIS_HOST']
REDIS_PORT    = 6379
REDIS_DB_NAME = 0
