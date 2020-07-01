# -*- coding: utf8 -*-

import pymysql.cursors
import os

# MySQL variables
MYSQL_USER     = os.environ['METRICS_MYSQL_USER']
MYSQL_PASSWORD = os.environ['METRICS_MYSQL_PASSWORD']
MYSQL_DB       = os.environ['METRICS_MYSQL_DB']
MYSQL_HOST     = os.environ['METRICS_MYSQL_HOST']

def get_count_table(table):
    connection = pymysql.connect(host       = MYSQL_HOST,
                                 user       = MYSQL_USER,
                                 password   = MYSQL_PASSWORD,
                                 db         = MYSQL_DB,
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM {}".format(table)
            cursor.execute(sql)
            result = cursor.fetchone()
    finally:
        connection.close()

    if result: return result['COUNT(*)']
    else: return None
