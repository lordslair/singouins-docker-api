# -*- coding: utf8 -*-

import os
import urllib.parse

from mongoengine import connect

MONGO_BASE = os.environ.get("MONGO_BASE", 'singouins')
MONGO_HOST = os.environ.get("MONGO_HOST", '127.0.0.1')
MONGO_PASS = os.environ.get("MONGO_PASS")
MONGO_USER = os.environ.get("MONGO_USER", 'singouins')

username = urllib.parse.quote_plus(MONGO_USER)
password = urllib.parse.quote_plus(MONGO_PASS)
MONGO_URI = 'mongodb+srv://%s:%s@%s/%s?authSource=admin&replicaSet=replicaset&tls=true' % (
    username,
    password,
    MONGO_HOST,
    MONGO_BASE,
    )

connect(host=MONGO_URI)
