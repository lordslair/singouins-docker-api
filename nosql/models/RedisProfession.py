# -*- coding: utf8 -*-

import json

from loguru import logger

from nosql.connector import r
from nosql.variables import str2typed

OBJECT = 'profession'
BASEKEY = f'{OBJECT}s'
HEAD = f'{OBJECT.capitalize()}.id'


class RedisProfession:
    def __init__(self, creatureuuid=None):
        if creatureuuid:
            self.id = creatureuuid
        else:
            self.id = None

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
        return self.__dict__

    def destroy(self):
        """
        Destroys an Object and DEL it from Redis DB.

        Parameters: None

        Returns: bool()
        """
        LOGH = f'[{HEAD}:{self.id}]'

        if hasattr(self, 'id') is False:
            logger.warning(f'{LOGH} Method KO - ID NotSet')
            return False
        if self.id is None:
            logger.warning(f'{LOGH} Method KO - ID NotFound')
            return False

        try:
            KEY = f'{BASEKEY}:{self.id}'
            if r.exists(KEY):
                logger.trace(f'{LOGH} Method >> (HASH Destroying)')
                r.delete(KEY)
            else:
                logger.warning(f'{LOGH} Method KO (HASH NotFound)')
                return False
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{LOGH} Method >> (HASH Destroyed)')
            return True

    def exists(self):
        """
        Checks existence of Object in Redis DB.

        Parameters: None

        Returns: bool()
        """
        KEY = f'{BASEKEY}:{self.id}'
        LOGH = f'[{HEAD}:{self.id}]'
        if r.exists(KEY):
            logger.trace(f'{LOGH} Method >> (KEY Found)')
            return True
        else:
            logger.warning(f'{LOGH} Method KO (KEY NotFound)')
            return False

    def incr(self, field, count=1):
        """
        Increment an Object field in Redis DB.

        Parameters:
        - field (str): HKEY field to INCR
        - count (int): value to INCR by (default: 1)

        Returns: bool()
        """
        KEY = f'{BASEKEY}:{self.id}'
        LOGH = f'[{HEAD}:{self.id}]'
        try:
            if hasattr(self, field):
                setattr(self, field, getattr(self, field) + count)
                # We increment the hash key
                logger.trace(f'{LOGH} Method >> (HINCRBY {OBJECT.capitalize()}.{field})')
                r.hincrby(KEY, field, count)
            else:
                setattr(self, field, count)
                # We create the hash key
                logger.trace(f'{LOGH} Method >> (HSET {OBJECT.capitalize()}.{field})')
                r.hset(KEY, field, count)
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{LOGH} Method OK')
            return True

    def load(self):
        """
        Loads an Object from Redis DB.

        Parameters: None

        Returns: Object
        """
        KEY = f'{BASEKEY}:{self.id}'
        LOGH = f'[{HEAD}:{self.id}]'
        try:
            if self.exists():
                logger.trace(f'{LOGH} Method >> (HKEY Loading)')
                for k, v in r.hgetall(KEY).items():
                    setattr(self, k, str2typed(v))
            else:
                return None
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
        else:
            logger.trace(f'{LOGH} Method OK (HKEY Loaded)')
            return self

    def new(self, creatureuuid):
        """
        Creates an Object into Redis DB.

        Parameters:
        - creatureuuid: CreatureUUID to attach Professions to

        Returns: RedisProfession
        """
        try:
            self.id = creatureuuid
            KEY = f'{BASEKEY}:{self.id}'
            LOGH = f'[{HEAD}:{self.id}]'
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None

        try:
            logger.trace(f'{LOGH} Method >> (Dict Creating)')
            # We push data in final dict
            hashdict = {
                "id": self.id,
            }

            logger.trace(f'{LOGH} Method >> (HASH Storing)')
            r.hset(KEY, mapping=hashdict)
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{LOGH} Method OK (HASH Stored)')
            return self
