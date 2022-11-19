# -*- coding: utf8 -*-

import uuid

from datetime                    import datetime
from loguru                      import logger
from random                      import randint
from redis.commands.search.query import Query

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisCreature:
    def __init__(self):
        self.hkey = 'creatures'

    def destroy(self, cuuid):
        try:
            self.logh = f'[Creature.id:{cuuid}]'
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            if r.exists(f'{self.hkey}:{cuuid}'):
                r.delete(f'{self.hkey}:{cuuid}')
            else:
                logger.trace(f'{self.logh} Method KO - NotFound')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self, cuuid):
        self.logh = f'[Creature.id:{cuuid}]'
        fullkey = f'{self.hkey}:{cuuid}'
        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            if r.exists(fullkey):
                hashdict = r.hgetall(fullkey)
            else:
                logger.trace(f'{self.logh} Method KO (HASH NotFound)')
                return False

            for k, v in hashdict.items():
                # We create the object attribute with converted types
                # But we skip some of them as they have @setters
                # Note: any is like many 'or', all is like many 'and'.
                if any([
                    k == 'instance',
                    k == 'x',
                    k == 'xp',
                    k == 'y',
                ]):
                    setattr(self, f'_{k}', str2typed(v))
                else:
                    setattr(self, k, str2typed(v))
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def new(
            self,
            name,
            race,
            gender,
            accountid,
            rarity='Medium',
            x=randint(2, 4),
            y=randint(2, 5),
            instanceid=None):

        # Checking if Creature exists with the same name
        # FOR A PLAYABLE CREATURE ONLY
        self.logh = '[Creature.id:None]'
        try:
            if race < 11:
                # Checking if it exists
                logger.trace(
                    f'{self.logh} Method >> '
                    f'(Checking uniqueness name:{name})'
                    )
                try:
                    possible_uuid = str(
                        uuid.uuid3(uuid.NAMESPACE_DNS, name)
                        )
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
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (Creating object)')
        try:
            self.account = accountid
            self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.gender = gender
            self._instance = instanceid
            self._korp = None
            self._korp_rank = None
            self.level = 1
            self.name = name
            self.race = race
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

        logger.trace(f'{self.logh} Method >> (Creating dict)')
        try:
            fullkey = f'{self.hkey}:{self.id}'
            # We push data in final dict
            hashdict = {}
            # We loop over object properties to create it
            for property, value in self._asdict().items():
                hashdict[property] = typed2str(value)

            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(fullkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def search(self, query, maxpaging=25):
        self.logh = '[Creature.id:None]'
        index = 'creature_idx'
        try:
            r.ft(index).info()
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(r.ft(index).info())
            pass

        try:
            logger.trace(f'{self.logh} Method >> (Searching {query})')
            # Query("search engine").paging(0, 10)
            # f"@bearer:[{bearerid} {bearerid}]"
            results = r.ft(index).search(
                Query(query).paging(0, maxpaging)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(results)
            pass

        # If we are here, we got results
        creatures = []
        for result in results.docs:
            user = {
                "account": str2typed(result.account),
                "created": result.created,
                "date": result.date,
                "gender": str2typed(result.gender),
                "id": result.id.removeprefix('creatures:'),
                "instance": str2typed(result.instance),
                "korp": str2typed(result.korp),
                "korp_rank": str2typed(result.korp_rank),
                "level": str2typed(result.level),
                "name": result.name,
                "race": str2typed(result.race),
                "rarity": result.rarity,
                "squad": str2typed(result.squad),
                "squad_rank": str2typed(result.squad_rank),
                "targeted_by": str2typed(result.targeted_by),
                "x": str2typed(result.x),
                "xp": str2typed(result.xp),
                "y": str2typed(result.y),
                }
            creatures.append(user)

        logger.trace(f'{self.logh} Method OK')
        return creatures

    def _asdict(self):
        hashdict = {
            "account": self.account,
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
        return hashdict

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
                '(Setting HASH) Creature.instance'
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
            logger.trace(f'{self.logh} Method OK')

    @property
    def korp(self):
        return self._korp

    @korp.setter
    def korp(self, korp):
        self._korp = korp
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(Setting HASH) Creature.korp'
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
            logger.trace(f'{self.logh} Method OK')

    @property
    def korp_rank(self):
        return self._korp_rank

    @korp_rank.setter
    def korp_rank(self, korp_rank):
        self._korp_rank = korp_rank
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(Setting HASH) Creature.korp_rank'
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
            logger.trace(f'{self.logh} Method OK')

    @property
    def squad(self):
        return self._squad

    @squad.setter
    def squad(self, squad):
        self._squad = squad
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(Setting HASH) Creature.squad'
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
            logger.trace(f'{self.logh} Method OK')

    @property
    def squad_rank(self):
        return self._squad_rank

    @squad_rank.setter
    def squad_rank(self, squad_rank):
        self._squad_rank = squad_rank
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(Setting HASH) Creature.squad_rank'
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
            logger.trace(f'{self.logh} Method OK')

    @property
    def xp(self):
        return self._xp

    @xp.setter
    def xp(self, xp):
        self._xp = xp
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(Setting HASH) Creature.xp'
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
            logger.trace(f'{self.logh} Method OK')

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, x):
        self._x = x
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(Setting HASH) Creature.x'
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
            logger.trace(f'{self.logh} Method OK')

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, y):
        self._y = y
        try:
            logger.trace(
                f'{self.logh} Method >> '
                '(Setting HASH) Creature.y'
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
            logger.trace(f'{self.logh} Method OK')


if __name__ == '__main__':
    Creature = RedisCreature().new(
        'Turlututu',
        4,
        True,
        'c884affd-21f6-32ec-9128-73016b53bfd7'
    )

    logger.success(RedisCreature().get(Creature.id)._asdict())
    logger.success(RedisCreature().search(field='name', query='Turlututu'))
    logger.success(RedisCreature().destroy(Creature.id))

    """
    FT.CREATE creature_idx PREFIX 1 "creatures:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "creature_score"
        SCHEMA
            account TEXT
            id TEXT
            instance TEXT
            korp TEXT
            korp_rank TEXT
            name TEXT
            squad TEXT
            squad_rank TEXT
            x NUMERIC
            y NUMERIC

    FT.SEARCH creature_idx "" LIMIT 0 10

    FT.DROPINDEX creature_idx
    """
