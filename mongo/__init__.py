# -*- coding: utf8 -*-

import os
import urllib.parse

from mongoengine import connect

from mongo._initialize import initialize_mongodb_meta

MONGO_BASE = os.environ.get("MONGO_BASE", 'singouins')
MONGO_HOST = os.environ.get("MONGO_HOST", '127.0.0.1')
MONGO_PASS = os.environ.get("MONGO_PASS")
MONGO_USER = os.environ.get("MONGO_USER", 'singouins')

username = urllib.parse.quote_plus(MONGO_USER)
password = urllib.parse.quote_plus(MONGO_PASS)

if os.environ.get("CI"):
    # Here we are inside GitHub CI process
    # And we don't use replicas
    MONGO_CONN = 'mongodb'
    MONGO_REPL = ''
    MONGO_STLS = ''
else:
    MONGO_CONN = 'mongodb+srv'
    MONGO_REPL = '&replicaSet=replicaset'
    MONGO_STLS = '&tls=true'

MONGO_URI = '%s://%s:%s@%s/%s?authSource=admin%s%s' % (
    MONGO_CONN,
    username,
    password,
    MONGO_HOST,
    MONGO_BASE,
    MONGO_REPL,
    MONGO_STLS,
    )

connect(host=MONGO_URI)

# Load all Meta in DB
initialize_mongodb_meta()
