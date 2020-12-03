# -*- coding: utf8 -*-

from sqlalchemy     import create_engine

from variables      import SQL_DSN

engine = create_engine('mysql+pymysql://' + SQL_DSN,
                       pool_recycle=3600,
                       pool_pre_ping=True)
