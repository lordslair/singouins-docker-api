# -*- coding: utf8 -*-

import json

from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed


class RedisHS:
    def __init__(self, creatureuuid=None):
        self.hkey = 'highscores'
        self.logh = f'[HighScores.id:{creatureuuid}]'
        fullkey = f'{self.hkey}:{creatureuuid}'

        try:
            if creatureuuid:
                self.id = creatureuuid
                if r.exists(fullkey):
                    logger.trace(f'{self.logh} Method >> (HASH Loading)')
                    hashdict = r.hgetall(fullkey)

                    for k, v in hashdict.items():
                        setattr(self, k, str2typed(v))

                    logger.trace(f'{self.logh} Method >> (HASH Loaded)')
                else:
                    logger.trace(f'{self.logh} Method KO (HASH NotFound)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    def __iter__(self):
        yield from self.as_dict().items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        """
        Converts Object into a JSON

        Parameters: None

        Returns: str()
        """
        return self.__str__()

    def as_dict(self):
        """
        Converts Object into a Python dict

        Parameters: None

        Returns: dict()
        """
        highscores = {}
        for key, val in self.__dict__.items():
            if any([
                key == 'hkey',
                key == 'logh',
            ]):
                pass
            else:
                highscores[key] = val
        return highscores

    def destroy(self):
        """
        Destroys an Object and DEL it from Redis DB.

        Parameters: None

        Returns: bool()
        """
        if hasattr(self, 'id') is False:
            logger.warning(f'{self.logh} Method KO - ID NotSet')
            return False
        if self.id is None:
            logger.warning(f'{self.logh} Method KO - ID NotFound')
            return False

        try:
            if r.exists(f'{self.hkey}:{self.id}'):
                logger.trace(f'{self.logh} Method >> (HASH Destroying)')
                r.delete(f'{self.hkey}:{self.id}')
            else:
                logger.warning(f'{self.logh} Method KO (HASH NotFound)')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method >> (HASH Destroyed)')
            return True

    def incr(self, key, count=1):
        fullkey = f'{self.hkey}:{self.id}'
        try:
            logger.trace(f'{self.logh} Method >> (HASH Incrementing)')
            # We increment the object attribute
            if hasattr(self, key):
                setattr(self, key, getattr(self, key) + count)
                # We increment the hash key
                r.hincrby(fullkey, key, count)
            else:
                setattr(self, key, count)
                # We create the hash key
                r.hset(fullkey, key, count)

        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            for k, v in r.hgetall(fullkey).items():
                setattr(self, k, str2typed(v))
            logger.trace(f'{self.logh} Method OK (HASH Incremented)')
            return True
