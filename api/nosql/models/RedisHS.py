# -*- coding: utf8 -*-

import copy

from nosql.connector            import *

class RedisHS:
    def __init__(self,creature):
        self.creature = creature
        self.hkey     = f'highscores:{creature.id}'
        self.logh     = f'[Creature.id:{self.creature.id}]'
        logger.trace(f'{self.logh} Method >> Initialization')

        try:
            hashdict = {
                "action_load": 0,
                "action_unload": 0,
                "action_dismantle": 0,
                "action_move": 0,
                }

            for k, v in hashdict.items():
                setattr(self, k, v)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            pass

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

    def get(self):
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

    def destroy(self):
        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(self.hkey)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def _asdict(self):
        clone = copy.deepcopy(self)
        if clone.hkey: del clone.hkey
        if clone.creature: del clone.creature
        if clone.logh: del clone.logh
        return clone.__dict__
