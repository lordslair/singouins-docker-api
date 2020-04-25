# -*- coding: utf8 -*-

import mysql.connector

from variables import MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_HOST

db = mysql.connector.connect(
     host=MYSQL_HOST,
     port=3306,
     user=MYSQL_USER,
     database=MYSQL_DB,
     password=MYSQL_PASSWORD)

def query_get_user_exists(username):
    SQL = """SELECT name FROM pjsAuth WHERE name = %s"""
    cursor = db.cursor()
    cursor.execute(SQL, (username,))
    row = cursor.fetchone()
    if row:
        return True

def query_get_password(username):
    SQL = """SELECT pass FROM pjsAuth WHERE name = %s"""
    cursor = db.cursor()
    cursor.execute(SQL, (username,))
    row = cursor.fetchone()
    if row:
        return row[0]

#db.close()
