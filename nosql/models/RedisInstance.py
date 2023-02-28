# -*- coding: utf8 -*-

import json
import uuid

from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisInstance:
    def __init__(self, instanceuuid=None):
        self.hkey = 'instances'
        self.logh = f'[Instance.id:{instanceuuid}]'

        try:
            if instanceuuid:
                self.id = instanceuuid
                fullkey = f'{self.hkey}:{self.id}'
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
        return {
            "creator": self.creator,
            "fast": self.fast,
            "hardcore": self.hardcore,
            "id": self.id,
            "map": self.map,
            "public": self.public,
            "tick": self.tick
            }

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

    def new(self, instance):
        # We need to define the new instance.id
        self.id = str(uuid.uuid4())
        self.logh = f'[Instance.id:{self.id}]'

        try:
            logger.trace(f'{self.logh} Method >> (Dict Creating)')
            # We push data in final dict

            if instance['fast'] is True:
                self.tick = 5
            else:
                self.tick = 3600

            self.creator  = instance['creator']
            self.fast     = instance['fast']
            self.hardcore = instance['hardcore']
            self.map      = instance['map']
            self.public   = instance['public']

            hashdict = {
                "creator": self.creator,
                "fast": typed2str(self.fast),
                "hardcore": typed2str(self.hardcore),
                "id": self.id,
                "map": self.map,
                "public": typed2str(self.public),
                "tick": self.tick
            }
            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(f'instances:{self.id}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self
