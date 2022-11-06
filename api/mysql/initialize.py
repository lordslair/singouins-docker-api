# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.engine               import engine
from mysql.base                 import Base

from mysql.models               import (Creature,
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
    'Creature',
    'CreatureStats',
    'Squad',
    'Korp',
    'MP',
    'User',
]

"""
# NOTA BENE
the __all__ just above NEEDS to be commented once during first app init
Or the DB schema won't be created
# Gruik
"""


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
