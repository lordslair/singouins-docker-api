# -*- coding: utf8 -*-

import copy

from loguru                     import logger

from nosql.connector            import r


class RedisInstance:
    def __init__(self, creature, instanceid=None):
        self.creature = creature
        self.hkey     = f'highscores:{creature.id}'
        if creature:
            self.logh = f'[Creature.id:{self.creature.id}]'
        else:
            # creature can be None if RedisInstance is called to check
            # if an Instance exists without knowing who is inside
            self.logh = '[Creature.id:None]'
        logger.trace(f'{self.logh} Method >> '
                     f'Initialization Instance({instanceid})')
        try:
            self.creator  = None
            self.fast     = False
            self.hardcore = False
            self.id       = None
            self.map      = None
            self.public   = False
            self.tick     = 3600
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            pass

        if creature and creature.instance:
            # We are hear if invoked to get the instance where is a creature
            self.creator = creature.id
            self.id      = creature.instance
            logger.trace(f'{self.logh} Method >> '
                         f'Already in Instance({self.id})')
        elif instanceid:
            # We are here to just get an existing instance
            self.id   = instanceid
            logger.trace(f'{self.logh} Method >> Fetching Instance({self.id})')

        # We do the queries and object update
        if self.id and r.exists(f'instances:{self.id}'):
            # The Instance does already exist in Redis
            try:
                hash = r.hgetall(f'instances:{self.id}')
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                self.creator  = int(hash['creator'])
                self.fast     = bool(hash['fast'])
                self.hardcore = bool(hash['hardcore'])
                self.map      = int(hash['map'])
                self.public   = bool(hash['public'])
                self.tick     = int(hash['tick'])

                logger.trace(f'{self.logh} Method >> (HASH Loaded)')
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')

    def new(self, instance):
        # We need to define the new instance.id
        try:
            syskey = 'system:instance_max_id'
            if r.exists(syskey):
                instance_max_id = int(r.get(syskey))
                self.id         = instance_max_id + 1
        except Exception as e:
            logger.error(f'{self.logh} Method KO >> (Loading {syskey}) [{e}]')
            return None
        else:
            pass

        try:
            logger.trace(f'{self.logh} Method >> (Creating dict)')
            # We push data in final dict

            if instance['fast'] is True:
                self.tick = 5
            else:
                self.tick = 3600

            self.creator  = instance['creator']
            self.fast     = instance['fast']
            self.hardcore = instance['hardcore']
            self.map      = instance['map']
            self.public   = instance['public']

            hashdict = {
                "creator": self.creator,
                "fast": str(self.fast),
                "hardcore": str(self.hardcore),
                "id": self.id,
                "map": self.map,
                "public": str(self.public),
                "tick": self.tick
            }
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(f'instances:{self.id}', mapping=hashdict)
            r.incr(syskey)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def store(self):
        try:
            # We push data in final dict
            hashdict = {
                "creator": self.creator,
                "fast": str(self.fast),
                "hardcore": str(self.hardcore),
                "id": self.id,
                "map": self.map,
                "public": str(self.public),
                "tick": self.tick
            }
            logger.success(hashdict)
            logger.trace(f'{self.logh} Method >> (Creating dict)')
            r.hset(f'instances:{self.id}', mapping=hashdict)
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy(self):
        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(f'instances:{self.id}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def _asdict(self):
        clone = copy.deepcopy(self)
        if clone.hkey:
            del clone.hkey
        if clone.creature:
            del clone.creature
        if clone.logh:
            del clone.logh
        return clone.__dict__
