# -*- coding: utf8 -*-

import json
import uuid

from datetime                    import datetime
from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisSquad:
    def __init__(self, squaduuid=None):
        self.hkey = 'squads'
        self.logh = f'[Squad.id:{squaduuid}]'
        fullkey = f'{self.hkey}:{squaduuid}'

        try:
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
                "created": self.created,
                "date": self.date,
                "id": self.id,
                "name": self.name,
                "leader": self.leader,
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
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            if r.exists(f'{self.hkey}:{self.id}'):
                r.delete(f'{self.hkey}:{self.id}')
            else:
                logger.warning(f'{self.logh} Method KO - NotFound')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def new(self, creatureuuid):
        self.logh = '[Squad.id:None]'
        # Checking if it exists
        logger.trace(f'{self.logh} Method >> (Checking uniqueness)')
        try:
            possible_uuid = str(
                uuid.uuid3(uuid.NAMESPACE_DNS, creatureuuid)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            self.logh = f'[Squad.id:{possible_uuid}]'
            if r.exists(f'{self.hkey}:{possible_uuid}'):
                logger.error(f'{self.logh} Method KO - Already Exists')
                return False

        logger.trace(f'{self.logh} Method >> (Creating dict)')
        try:
            self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.id = possible_uuid
            self.leader = creatureuuid
            self.name = None
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (Storing HASH)')
        try:
            hashdict = {
                "created": self.created,
                "date": self.date,
                "id": self.id,
                "name": typed2str(self.name),
                "leader": self.leader,
            }
            r.hset(f'{self.hkey}:{self.id}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self
