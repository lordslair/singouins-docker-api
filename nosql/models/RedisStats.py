# -*- coding: utf8 -*-

import json

from loguru                     import logger

from nosql.connector            import r

from nosql.metas                import metaNames
from nosql.variables            import str2typed


class RedisStats:
    def __init__(self, creatureuuid=None):
        self.hkey = 'stats'
        self.logh = f'[Stats.id:{creatureuuid}]'

        if creatureuuid:
            fullkey = f'{self.hkey}:{creatureuuid}'
            try:
                if r.exists(fullkey):
                    logger.trace(f'{self.logh} Method >> (HASH Loading)')
                    for k, v in r.hgetall(fullkey).items():
                        if any([
                            k == 'hp',
                        ]):
                            setattr(self, f'_{k}', str2typed(v))
                        else:
                            setattr(self, k, str2typed(v))
                    logger.trace(f'{self.logh} Method OK (HASH Loaded)')

                    # We add the ID for later use
                    self.id = creatureuuid
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
            "base": {
                "m": self.m,
                "r": self.r,
                "g": self.g,
                "v": self.v,
                "p": self.p,
                "b": self.b
            },
            "def": {
                "hpmax": self.hpmax,
                "hp": self.hp,
            }
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
        Creature,
        classid,
    ):
        logger.trace(f'{self.logh} Method >> (HASH Creating)')
        self.id = Creature.id

        try:
            metaRace = metaNames['race'][Creature.race]

            # This is base stats
            self.m_race = metaRace['min_m']
            self.r_race = metaRace['min_r']
            self.g_race = metaRace['min_g']
            self.v_race = metaRace['min_v']
            self.p_race = metaRace['min_p']
            self.b_race = metaRace['min_b']

            # This is bonus given by Class
            self.m_class = 0
            self.r_class = 0
            self.g_class = 0
            self.v_class = 0
            self.p_class = 0
            self.b_class = 0

            if classid == 1:
                self.m_class = 10
            if classid == 2:
                self.r_class = 10
            if classid == 3:
                self.g_class = 10
            if classid == 4:
                self.v_class = 10
            if classid == 5:
                self.p_class = 10
            if classid == 6:
                self.b_class = 10

            # We got Creature base stats - Just consolidate
            self.m = self.m_race + self.m_class
            self.r = self.r_race + self.r_class
            self.g = self.g_race + self.g_class
            self.v = self.v_race + self.v_class
            self.p = self.p_race + self.p_class
            self.b = self.b_race + self.b_class

            self.hpmax = 100 + self.m + round(Creature.level / 2)
            self._hp   = self.hpmax
        except Exception as e:
            logger.error(f'{self.logh} Method KO (Building from Caracs) [{e}]')
        else:
            logger.trace(f'{self.logh} Method >> (Building from Caracs)')

        try:
            # We push data in final dict
            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            hashdict = {
                "b": self.b,
                "b_race": self.b_race,
                "b_class": self.b_class,
                "g": self.g,
                "g_race": self.g_race,
                "g_class": self.g_class,
                "m": self.m,
                "m_race": self.m_race,
                "m_class": self.m_class,
                "p": self.p,
                "p_race": self.p_race,
                "p_class": self.p_class,
                "r": self.r,
                "r_race": self.r_race,
                "r_class": self.r_class,
                "v": self.v,
                "v_race": self.v_race,
                "v_class": self.v_class,
                "hpmax": self.hpmax,
                "hp": self.hp,
                }

            r.hset(f'{self.hkey}:{self.id}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self

    """
    Getter/Setter block for HP management
    It is done that way to r.hset() every time API code manipulates Creature HP
    And avoid to build a store() method just for that purpose
    As it is the only value that can be directly modified in the RedisStats
    """
    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, hp):
        self._hp = hp
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Stats.hp')
            r.hset(f'{self.hkey}:{self.id}', 'hp', self._hp)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')
