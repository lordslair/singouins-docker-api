# -*- coding: utf8 -*-

import json
import time
import uuid

from datetime                    import datetime
from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisEvent:
    def __init__(self, eventuuid=None):
        self.hkey = 'events'
        self.logh = '[Event.id:None]'

        try:
            if eventuuid:
                self.id = eventuuid
                if r.exists(f'{self.hkey}:{self.id}'):
                    logger.trace(f'{self.logh} Method >> (HASH Loading)')
                    for k, v in r.hgetall(f'{self.hkey}:{self.id}').items():
                        setattr(self, k, str2typed(v))
                else:
                    logger.trace(f'{self.logh} Method KO (HASH NotFound)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Loaded)')

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
            "dst": self.dst,
            "src": self.src,
            "action": self.action,
            "type": self.type,
            "id": self.id,
            "date": self.date,
            "timestamp": self.timestamp,
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

    def new(
        self,
        action_src,
        action_dst,
        action_type,
        action_text,
        action_ttl=None,
    ):
        ts  = time.time_ns() // 1000000  # Time in milliseconds
        eventuuid = str(uuid.uuid4())
        self.logh = f'[Event.id:{eventuuid}]'

        self.action = action_text
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.dst = action_dst
        self.id = eventuuid
        self.src = action_src
        self.timestamp = ts
        self.type = action_type

        logger.trace(f'{self.logh} Method >> (Dict Creating)')
        try:
            fullkey = f'{self.hkey}:{self.id}'
            # We push data in final dict
            hashdict = {}

            # We loop over object properties to create it
            for property, value in self.as_dict().items():
                hashdict[property] = typed2str(value)

            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(fullkey, mapping=hashdict)
            if action_ttl is not None:
                r.expire(fullkey, action_ttl)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self
