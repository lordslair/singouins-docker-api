# -*- coding: utf8 -*-

import json
import uuid

from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed


class RedisEffect:
    def __init__(self, creatureuuid=None, name=None):
        self.type = 'effect'
        self.hkey = 'effects'
        self.logh = f'[Creature.id:{creatureuuid}]'

        if creatureuuid:
            self.creatureuuid = creatureuuid
            if name:
                logger.trace(f'{self.logh} Method >> Initialization')
                fullkey = f'{self.hkey}:{self.creatureuuid}:{name}'
                try:
                    logger.trace(f'{self.logh} Method >> (HASH Loading)')
                    if r.exists(fullkey):
                        hashdict = r.hgetall(fullkey)
                        for k, v in hashdict.items():
                            # We need to convert extra to JSON
                            if any([
                                k == 'extra',
                            ]):
                                setattr(self, k, json.loads(v))
                            else:
                                setattr(self, k, str2typed(v))
                        self.duration_left = r.ttl(fullkey)
                        logger.trace(f'{self.logh} Method >> (HASH Loaded)')
                    else:
                        logger.trace(f'{self.logh} Method KO (HASH NotFound)')
                except Exception as e:
                    logger.error(f'{self.logh} Method KO [{e}]')

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
            "bearer": self.bearer,
            "duration_base": self.duration_base,
            "duration_left": self.duration_left,
            "extra": self.extra,
            "id": self.id,
            "instance": self.instance,
            "name": self.name,
            "source": self.source,
            "type": self.type
            }

    def destroy(self, name):
        """
        Destroys an Object and DEL it from Redis DB.

        Parameters: None

        Returns: bool()
        """
        if hasattr(self, 'creatureuuid') is False:
            logger.warning(f'{self.logh} Method KO - ID NotSet')
            return False
        if self.creatureuuid is None:
            logger.warning(f'{self.logh} Method KO - ID NotFound')
            return False

        try:
            if r.exists(f'{self.hkey}:{self.creatureuuid}:{name}'):
                logger.trace(f'{self.logh} Method >> (HASH Destroying)')
                r.delete(f'{self.hkey}:{self.creatureuuid}:{name}')
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
        duration_base,
        extra,
        instance,
        name,
        source,
    ):
        # We check if self.id exists before continuing
        if self.creatureuuid is None:
            logger.warning(f'{self.logh} Method KO (Missing parameter)')
            return False

        try:
            # We push data in final dict
            logger.trace(f'{self.logh} Method >> (HASH Creating)')

            self.bearer        = self.creatureuuid
            self.duration_base = duration_base
            self.duration_left = duration_base
            self.extra         = json.dumps(extra)
            self.id            = str(uuid.uuid4())
            self.name          = name
            self.instance      = instance
            self.source        = source

            hashdict = {
                "bearer": self.bearer,
                "duration_base": self.duration_base,
                "id": self.id,
                "instance": self.instance,
                "extra": self.extra,
                "name": self.name,
                "source": self.source,
                "type": self.type
            }

            fullkey = f'{self.hkey}:{self.bearer}:{self.name}'
            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(fullkey, mapping=hashdict)
            r.expire(fullkey, self.duration_base)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self
