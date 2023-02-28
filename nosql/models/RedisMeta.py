# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector import r
from nosql.variables import str2typed


class RedisMeta:
    def __init__(self, metaid, metatype):
        self.hkey     = f'metas:{metatype}:{metaid}'
        self.logh = f'[Meta.id:{metaid}]'

        logger.trace(f'{self.logh} Method >> Initialization')
        if r.exists(f'{self.hkey}'):
            logger.trace(f'{self.logh} Method >> (KEY Loading)')
            hashdict = r.hgetall(f'{self.hkey}')

            try:
                for k, v in hashdict.items():
                    setattr(self, k, str2typed(v))
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')
