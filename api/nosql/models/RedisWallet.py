# -*- coding: utf8 -*-

from nosql.connector            import *

class RedisWallet:
    def __init__(self,creature):
        self.creature = creature
        self.hkey     = f'wallet:{creature.id}'
        self.logh     = f'[Creature.id:{self.creature.id}]'
        logger.trace(f'{self.logh} Method >> Initialization')

        if r.exists(self.hkey):
            # The pre-generated stats does already exist in redis
            try:
                hashdict = r.hgetall(self.hkey)
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                for k, v in hashdict.items():
                    # We create the object attribute with converted INT
                    setattr(self, k, int(v))

                logger.trace(f'{self.logh} Method >> (HASH Loaded)')
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')
        else:
            # The pre-generated stats does not already exist in redis
            logger.trace(f'{self.logh} Method >> (HASH Creating)')
            try:
                hashdict = {
                    "cal22":     0,
                    "cal223":    0,
                    "cal311":    0,
                    "cal50":     0,
                    "cal55":     0,
                    "shell":     0,
                    "bolt":      0,
                    "arrow":     0,
                    "legendary": 0,
                    "epic":      0,
                    "rare":      0,
                    "uncommon":  0,
                    "common":    0,
                    "broken":    0,
                    "bananas":   0,
                    "sausages":  0,
                    }
                for k, v in hashdict.items():
                    setattr(self, k, v)
                r.hset(self.hkey, mapping=hashdict)
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')

    def incr(self,key,count=1):
        try:
            logger.trace(f'{self.logh} Method >> (HASH Incrementing)')
            # We increment the object attribute
            setattr(self,key,getattr(self,key)+count)
            # We increment the hash key
            r.hincrby(self.hkey,key,count)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy(self):
        try:
            if r.exists(self.hkey):
                logger.trace(f'{self.logh} Method >> (Destroying HASH)')
                r.delete(self.hkey)
            else:
                logger.warning(f'{self.logh} Method >> (HASH not found)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def _asdict(self):
        hashdict = {
            "ammo":
                {
                    "cal22":  self.cal22,
                    "cal223": self.cal223,
                    "cal311": self.cal311,
                    "cal50":  self.cal50,
                    "cal55":  self.cal55,
                    "shell":  self.shell,
                    "bolt":   self.bolt,
                    "arrow":  self.arrow,
                },
            "currency":
                {
                    "bananas":  self.bananas,
                    "sausages": self.sausages,
                },
            "shards":
                {
                    "broken":    self.broken,
                    "common":    self.common,
                    "uncommon":  self.uncommon,
                    "rare":      self.rare,
                    "epic":      self.epic,
                    "legendary": self.legendary,
                }
             }

        return hashdict
