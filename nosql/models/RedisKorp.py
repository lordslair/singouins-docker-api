# -*- coding: utf8 -*-

import json
import uuid

from datetime import datetime
from loguru import logger

from nosql.connector import r
from nosql.variables import str2typed, typed2str


class RedisKorp:
    def __init__(self, korpuuid=None):
        self.hkey = 'korps'
        self.logh = f'[Korp.id:{korpuuid}]'
        fullkey = f'{self.hkey}:{korpuuid}'

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

    def exists(self, korpuuid):
        if r.exists(f'{self.hkey}:{korpuuid}'):
            logger.trace(f'{self.logh} Method >> (HASH Found)')
            return True
        else:
            logger.warning(f'{self.logh} Method KO (HASH NotFound)')
            return False

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

    def new(self, creatureuuid, korpname):
        self.logh = '[Korp.id:None]'
        # Checking if it exists
        logger.trace(f'{self.logh} Method >> (Checking uniqueness)')
        try:
            possible_uuid = str(
                uuid.uuid3(uuid.NAMESPACE_DNS, korpname)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            self.logh = f'[Korp.id:{possible_uuid}]'
            if r.exists(f'{self.hkey}:{possible_uuid}'):
                logger.error(f'{self.logh} Method KO - Already Exists')
                return False

        logger.trace(f'{self.logh} Method >> (Dict Creating)')
        try:
            self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.id = possible_uuid
            self.leader = creatureuuid
            self.name = korpname
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (HASH Storing)')
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
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self
