# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.engine               import engine
from mysql.base                 import Base

from mysql.models               import (Cosmetic,
                                        Item,
                                        Creature,
                                        CreatureStats,
                                        Squad,
                                        Korp,
                                        MP,
                                        User
                                        )

"""
https://stackoverflow.com
/questions/31079047/python-pep8-class-in-init-imported-but-not-used
"""

__all__ = [
    'Cosmetic',
    'Item',
    'Creature',
    'CreatureStats',
    'Squad',
    'Korp',
    'MP',
    'User',
]


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
