# -*- coding: utf8 -*-

import json

from loguru                     import logger

from nosql.connector            import r

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax


class RedisPa:
    def __init__(self, creatureuuid):
        self.hkey     = 'pa'
        self.logh     = f'[Creature.id:{creatureuuid}]'

        if creatureuuid:
            logger.trace(f'{self.logh} Method >> Initialization')
            self.id = creatureuuid
            if r.exists(f'{self.hkey}:{self.id}:red'):
                logger.trace(f'{self.logh} Method >> (HASH Loading) RED')
                try:
                    self.redttl   = r.ttl(f'{self.hkey}:{self.id}:red')
                    redpa_temp    = redmaxttl - abs(self.redttl)
                    self.redpa    = int(round(redpa_temp / redpaduration))
                    self.redttnpa = self.redttl % redpaduration
                except Exception as e:
                    logger.error(f'{self.logh} Method KO [{e}]')
            else:
                self.redttl = 0
                self.redpa = redpamax
                self.redttnpa = redpaduration

            if r.exists(f'{self.hkey}:{self.id}:blue'):
                logger.trace(f'{self.logh} Method >> (HASH Loading) BLUE')
                try:
                    self.bluettl   = r.ttl(f'{self.hkey}:{self.id}:blue')
                    bluepa_temp    = bluemaxttl - abs(self.bluettl)
                    self.bluepa    = int(round(bluepa_temp / bluepaduration))
                    self.bluettnpa = self.bluettl % bluepaduration
                except Exception as e:
                    logger.error(f'{self.logh} Method KO [{e}]')
            else:
                self.bluettl = 0
                self.bluepa = bluepamax
                self.bluettnpa = bluepaduration

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
            "blue": {
                "pa": self.bluepa,
                "ttnpa": self.bluettnpa,
                "ttl": self.bluettl,
                },
            "red": {
                "pa": self.redpa,
                "ttnpa": self.redttnpa,
                "ttl": self.redttl,
                },
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
            logger.trace(f'{self.logh} Method >> (HASH Destroying)')
            if r.exists(f'{self.hkey}:{self.id}:blue'):
                r.delete(f'{self.hkey}:{self.id}:blue')
            if r.exists(f'{self.hkey}:{self.id}:red'):
                r.delete(f'{self.hkey}:{self.id}:red')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method >> (HASH Destroyed)')
            return True

    def consume(self, redpa=0, bluepa=0):
        try:
            if bluepa > 0:
                logger.trace(f'{self.logh} Method >> (KEY Updating) BLUE')
                # An action consumed a blue PA, we need to update
                key    = f'{self.hkey}:{self.id}:blue'
                ttl    = r.ttl(key)
                newttl = ttl + (bluepa * bluepaduration)

                if newttl < bluepaduration * bluepamax:
                    # We update the object
                    self.bluepa = bluepa
                    self.bluettl = newttl
                    self.bluettnpa = self.bluettl % bluepaduration

                    if ttl > 0:
                        # Key still exists (PA count < PA max)
                        r.expire(key, newttl)
                    else:
                        # Key does not exist anymore (PA count = PA max)
                        r.set(key, 'None', ex=newttl)
            if redpa > 0:
                logger.trace(f'{self.logh} Method >> (KEY Updating) RED')
                # An action consumed a red PA, we need to update
                key    = f'{self.hkey}:{self.id}:red'
                ttl    = r.ttl(key)
                newttl = ttl + (redpa * redpaduration)

                if newttl < redpaduration * redpamax:
                    # We update the object
                    self.redpa = redpa
                    self.redttl = newttl
                    self.redttnpa = self.redttl % redpaduration

                    if ttl > 0:
                        # Key still exists (PA count < PA max)
                        r.expire(key, newttl)
                    else:
                        # Key does not exist anymore (PA count = PA max)
                        r.set(key, 'None', ex=newttl)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (KEY Updated)')
            return True
