# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector            import r


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
                    # We create the object attribute with converted INT
                    if v == 'false' or v == 'False':
                        newv = False
                    elif v == 'true' or v == 'True':
                        newv = True
                    elif v == '' or v == 'none' or v == 'null':
                        newv = None
                    elif v.isdigit():
                        newv = int(v)
                    else:
                        newv = v
                    setattr(self, k, newv)
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')
