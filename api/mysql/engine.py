# -*- coding: utf8 -*-

from loguru         import logger
from sqlalchemy     import create_engine

from variables      import SQL_DSN

try:
    engine = create_engine('mysql+pymysql://' + SQL_DSN,
                           pool_recycle=3600,
                           pool_pre_ping=True)
except Exception as e:
    logger.error(f'Engine start KO [{e}]')
else:
    logger.trace('Engine start OK')
