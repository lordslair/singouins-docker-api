# -*- coding: utf8 -*-

from loguru                     import logger

from .engine                    import engine
from .base                      import Base

def initialize_db():
    try:
        logger.info('MySQL init: start')
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.error(f'MySQL init: KO [{e}]')
    else:
        logger.info('MySQL init: OK')
    finally:
        logger.info('MySQL init: end')
