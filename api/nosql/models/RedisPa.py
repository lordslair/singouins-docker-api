# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector            import r

redpaduration  = 3600
redpamax       = 16
redmaxttl      = redpaduration * redpamax

bluepaduration = 3600
bluepamax      = 8
bluemaxttl     = bluepaduration * bluepamax


class RedisPa:
    def __init__(self, creature):
        self.creature = creature
        self.hkey     = f'pa:{creature.id}'
        self.logh     = f'[Creature.id:{self.creature.id}]'
        logger.trace(f'{self.logh} Method >> Initialization')

        self.redttl    = None
        self.redpa     = None
        self.redttnpa  = None
        self.bluettl   = None
        self.bluepa    = None
        self.bluettnpa = None
        self.refresh()

    def consume(self, redpa=0, bluepa=0):
        try:
            if bluepa > 0:
                logger.trace(f'{self.logh} Method >> (KEY Update) BLUE')
                # An action consumed a blue PA, we need to update
                key    = f'{self.hkey}:blue'
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
                        r.set(key, '', ex=newttl)
            if redpa > 0:
                logger.trace(f'{self.logh} Method >> (KEY Update) RED')
                # An action consumed a red PA, we need to update
                key    = f'{self.hkey}:red'
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
                        r.set(key, '', ex=newttl)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy(self):
        self.reset()

    def refresh(self):
        try:
            logger.trace(f'{self.logh} Method >> (KEY Loading)')
            self.redttl   = r.ttl(f'{self.hkey}:red')
            redpa_temp    = redmaxttl - abs(self.redttl)
            self.redpa    = int(round(redpa_temp / redpaduration))
            self.redttnpa = self.redttl % redpaduration
            logger.trace(f'{self.logh} Method >> (KEY Loaded)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

        try:
            logger.trace(f'{self.logh} Method >> (KEY Loading)')
            self.bluettl   = r.ttl(f'{self.hkey}:blue')
            bluepa_temp    = bluemaxttl - abs(self.bluettl)
            self.bluepa    = int(round(bluepa_temp / bluepaduration))
            self.bluettnpa = self.bluettl % bluepaduration
            logger.trace(f'{self.logh} Method >> (KEY Loaded)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    def reset(self):
        try:
            logger.trace(f'{self.logh} Method >> (Expiring KEY)')
            r.set(f'{self.hkey}:red', '', ex=1)
            r.set(f'{self.hkey}:blue', '', ex=1)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def _asdict(self):
        # self.refresh()
        hashdict = {
            "blue":
                {
                    "pa": self.bluepa,
                    "ttnpa": self.bluettnpa,
                    "ttl": self.bluettl,
                },
            "red":
                {
                    "pa": self.redpa,
                    "ttnpa": self.redttnpa,
                    "ttl": self.redttl,
                },
        }
        return hashdict


if __name__ == '__main__':
    pass
