# -*- coding: utf8 -*-

from loguru         import logger
from sqlalchemy.orm import sessionmaker,scoped_session

from .engine        import engine

try:
    Session = scoped_session(sessionmaker(bind=engine))
except Exception as e:
    logger.error(f'Session start KO [{e}]')
else:
    logger.trace('Session start OK')
