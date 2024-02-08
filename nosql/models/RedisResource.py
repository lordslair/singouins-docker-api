# -*- coding: utf8 -*-

import json
import uuid

from loguru import logger

from nosql.connector import r
from nosql.variables import str2typed, typed2str

OBJECT = 'resource'
BASEKEY = f'{OBJECT}s'
HEAD = f'{OBJECT.capitalize()}.id'


class RedisResource:
    def __init__(self, resourceuuid=None):
        if resourceuuid:
            self.id = resourceuuid
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
        return {
            "instance": self.instance,
            "tile_id": self.tile_id,
            "material": self.material,
            "rarity": self.rarity,
            "visible": self.visible,
            "x": self.x,
            "y": self.y,
            }

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
            if r.exists(f'{self.hkey}:{self.id}'):
                logger.trace(f'{LOGH} Method >> (HASH Destroying)')
                r.delete(f'{self.hkey}:{self.id}')
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

    def new(
        self,
        instanceuuid,
        tile_id,
        material,
        rarity,
        visible,
        x,
        y,
    ):
        try:
            self.id = str(uuid.uuid4())
            KEY = f'{BASEKEY}:{self.id}'
            LOGH = f'[{HEAD}:{self.id}]'

            self.instance = instanceuuid
            self.tile_id = tile_id
            self.material = material
            self.rarity = rarity
            self.visible = visible
            self.x = x
            self.y = y
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None

        try:
            logger.trace(f'{LOGH} Method >> (Dict Creating)')
            # We push data in final dict
            hashdict = {}
            # We loop over object properties to create it
            for property, value in self.as_dict().items():
                hashdict[property] = typed2str(value)

            logger.trace(f'{LOGH} Method >> (HASH Storing)')
            r.hset(KEY, mapping=hashdict)
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{LOGH} Method OK (HASH Stored)')
            return self

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
                hashdict = r.hgetall(KEY)

                for k, v in hashdict.items():
                    setattr(self, k, str2typed(v))
            else:
                return None
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
        else:
            logger.trace(f'{LOGH} Method OK (HKEY Loaded)')
            return self
