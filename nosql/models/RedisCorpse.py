# -*- coding: utf8 -*-

import json

from datetime import datetime
from loguru import logger

from nosql.connector import r
from nosql.variables import str2typed, typed2str

OBJECT = 'corpse'
BASEKEY = f'{OBJECT}s'
HEAD = f'{OBJECT.capitalize()}.id'


class RedisCorpse:
    def __init__(self, corpseuuid=None):
        if corpseuuid:
            self.id = corpseuuid
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

    def new(self, Creature, killer=None):
        """
        Creates a new Corpse from a Creature and stores it into Redis DB.

        Parameters:
        Creature (RedisCreature): Creature Object
        killer (RedisCreature): Creature Object

        Returns: RedisCorpse object
        """
        try:
            self.id = Creature.id
            KEY = f'{BASEKEY}:{self.id}'
            LOGH = f'[{HEAD}:{self.id}]'
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None

        logger.trace(f'{LOGH} Method >> (Creating object)')
        try:
            self.account = Creature.account
            self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.gender = Creature.gender
            self.id = Creature.id
            self.instance = Creature.instance
            self.level = Creature.level
            self.name = Creature.name
            self.race = Creature.race
            self.rarity = Creature.rarity
            self.x = Creature.x
            self.y = Creature.y

            # Setting killer details:
            if killer:
                self.killer = killer.id
                self.killer_squad = killer.squad
            else:
                self.killer = None
                self.killer_squad = None
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None

        logger.trace(f'{LOGH} Method >> (Dict Creating)')
        try:
            # We loop over object properties to create it
            hashdict = {}
            for property, value in self.as_dict().items():
                hashdict[property] = typed2str(value)

            logger.trace(f'{LOGH} Method >> (HASH Storing)')
            r.hset(f'{KEY}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{LOGH} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{LOGH} Method OK (HASH Stored)')
            return self
