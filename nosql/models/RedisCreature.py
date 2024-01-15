# -*- coding: utf8 -*-

import json
import uuid

from datetime                    import datetime
from loguru                      import logger
from random                      import randint

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisCreature:
    def __init__(self, creatureuuid=None):
        self.hkey = 'creatures'
        self.logh = f'[Creature.id:{creatureuuid}]'
        self.id = creatureuuid
        logger.trace(f'{self.logh} Method >> Initialization')

        if creatureuuid:
            creaturekey = f'{self.hkey}:{creatureuuid}'
            aggrokey = f'aggros:{creatureuuid}'
            try:
                logger.trace(f'{self.logh} Method >> (HASH Loading)')
                if r.exists(creaturekey):
                    hashdict = r.hgetall(creaturekey)
                    for k, v in hashdict.items():
                        # We create the object attribute with converted types
                        # But we skip some of them as they have @setters
                        # Note: any is like many 'or', all is like many 'and'.
                        if any([
                            k == 'instance',
                            k == 'korp',
                            k == 'korp_rank',
                            k == 'squad',
                            k == 'squad_rank',
                            k == 'x',
                            k == 'xp',
                            k == 'y',
                        ]):
                            setattr(self, f'_{k}', str2typed(v))
                        else:
                            setattr(self, k, str2typed(v))
                    logger.trace(f'{self.logh} Method >> (HASH Loaded)')

                    logger.trace(f'{self.logh} Method >> (Getting aggro)')
                    self.aggro = 0
                    if r.exists(aggrokey):
                        self.aggro = int(r.get(aggrokey))
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

    def exists(self, creatureuuid):
        logger.debug(f'{self.hkey}:{creatureuuid}')
        if r.exists(f'{self.hkey}:{creatureuuid}'):
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
            "account": self.account,
            "aggro": self.aggro,
            "created": self.created,
            "date": self.date,
            "gender": self.gender,
            "id": self.id,
            "instance": self.instance,
            "korp": self.korp,
            "korp_rank": self.korp_rank,
            "level": self.level,
            "name": self.name,
            "race": self.race,
            "rarity": self.rarity,
            "squad": self.squad,
            "squad_rank": self.squad_rank,
            "targeted_by": self.targeted_by,
            "x": self.x,
            "xp": self.xp,
            "y": self.y,
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
        name,
        raceid,
        gender,
        accountuuid,
        rarity='Medium',
        x=randint(2, 4),
        y=randint(2, 5),
        instanceuuid=None,
    ):
        """
        Creates a new Creature and stores it into Redis DB.

        Parameters:
        name (str): Creature name
        raceid (int): Creature raceid
        gender (bool): Creature gender
        accountuuid (str): Creature account for Playable Creatures
        rarity (str): Creature rarity [Default:25]
        x (int): Creature Position:x [Default:randint(2, 4)]
        y (int): Creature Position:y [Default:randint(2, 5)]
        instanceuuid (str): Creature instance [Default:None]

        Returns: RedisCreature object
        """
        # Checking if Creature exists with the same name
        # FOR A PLAYABLE CREATURE ONLY
        self.logh = '[Creature.id:None]'

        if raceid < 11:
            # Checking if it exists
            logger.trace(
                f'{self.logh} Method >> (Checking uniqueness name:{name})')
            try:
                possible_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, name))
                if r.exists(f'{self.hkey}:{possible_uuid}'):
                    logger.error(f'{self.logh} Method KO - Already Exists')
                    return False
            except Exception as e:
                logger.error(f'[Creature.id:None] Method KO [{e}]')
                return None
            else:
                self.id = possible_uuid
        else:
            self.id = str(uuid.uuid4())

        self.logh = f'[Creature.id:{self.id}]'

        logger.trace(f'{self.logh} Method >> (Creating object)')
        try:
            self.aggro = 0
            self.account = accountuuid
            self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.gender = gender
            self._instance = instanceuuid
            self._korp = None
            self._korp_rank = None
            self.level = 1
            self.name = name
            self.race = raceid
            self.rarity = rarity
            self._squad = None
            self._squad_rank = None
            self.targeted_by = None
            self._x = x
            self._xp = 0
            self._y = y
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (Dict Creating)')
        try:
            creaturekey = f'{self.hkey}:{self.id}'
            # We push data in final dict
            hashdict = {}
            # We loop over object properties to create it

            for property, value in self.as_dict().items():
                if any([
                    property == 'aggro',
                ]):
                    pass
                else:
                    hashdict[property] = typed2str(value)

            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(creaturekey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self

    """
    Getter/Setter block for User management
    It is done that way to r.hset() every time API code manipulates a User
    And avoid to build a store() method just for that purpose
    """
    @property
    def instance(self):
        return self._instance

    @instance.setter
    def instance(self, instance):
        self._instance = instance
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.instance'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'instance',
                typed2str(self._instance)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def korp(self):
        return self._korp

    @korp.setter
    def korp(self, korp):
        self._korp = korp
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.korp'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'korp',
                typed2str(self._korp)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def korp_rank(self):
        return self._korp_rank

    @korp_rank.setter
    def korp_rank(self, korp_rank):
        self._korp_rank = korp_rank
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.korp_rank'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'korp_rank',
                typed2str(self._korp_rank)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def squad(self):
        return self._squad

    @squad.setter
    def squad(self, squad):
        self._squad = squad
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.squad'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'squad',
                typed2str(self._squad)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def squad_rank(self):
        return self._squad_rank

    @squad_rank.setter
    def squad_rank(self, squad_rank):
        self._squad_rank = squad_rank
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.squad_rank'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'squad_rank',
                typed2str(self._squad_rank)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, xp):
        self._xp = xp
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.xp'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'xp',
                typed2str(self._xp)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.x'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'x',
                typed2str(self._x)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(HASH Setting) Creature.y'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'y',
                typed2str(self._y)
                )
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')
