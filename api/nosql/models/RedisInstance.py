# -*- coding: utf8 -*-

from nosql.connector            import *

class RedisInstance:
    def __init__(self,creature,instanceid = None):
        if creature:
            h = f'[Creature.id:{creature.id}]' # Header for logging
        else:
            h = f'[Creature.id:None]' # Header for logging
        logger.trace(f'{h} Method >> Initialization (instance.id:{instanceid})')
        try:
            self.creator  = None
            self.fast     = False
            self.hardcore = False
            self.id       = None
            self.map      = None
            self.public   = False
            self.tick     = 3600
        except Exception as e:
            logger.error(f'{h} Method KO [{e}]')
        else:
            pass

        if creature and creature.instance:
            # We are hear if invoked to get the instance where is a creature
            self.creator = creature.id
            self.id      = creature.instance
            logger.trace(f'{h} Method >> Already in an Instance (instance.id:{self.id})')
        elif instanceid:
            # We are here to just get an existing instance
            self.id   = instanceid
            logger.trace(f'{h} Method >> Fetching an Instance (instance.id:{self.id})')

        # We do the queries and object update
        if self.id and r.exists(f'instances:{self.id}'):
            # The Instance does already exist in Redis
            try:
                hash = r.hgetall(f'instances:{self.id}')
                logger.trace(f'Method >> (HASH Loading)')

                self.creator  = int(hash['creator'])
                self.fast     = bool(hash['fast'])
                self.hardcore = bool(hash['hardcore'])
                self.map      = int(hash['map'])
                self.public   = bool(hash['public'])
                self.tick     = int(hash['tick'])

                logger.trace(f'{h} Method >> (HASH Loaded)')
            except Exception as e:
                logger.error(f'{h} Method KO [{e}]')
            else:
                logger.trace(f'{h} Method OK')

    def new(self,instance):
        # We need to define the new instance.id
        try:
            syskey = 'system:instance_max_id'
            if r.exists(syskey):
                instance_max_id = int(r.get(syskey))
                self.id         = instance_max_id + 1
        except Exception as e:
            logger.error(f'Method KO - Unable to get system:instance_max_id [{e}]')
            return None
        else:
            pass

        try:
            logger.trace(f'Method >> (Creating dict)')
            # We push data in final dict

            if instance['fast'] == True:
                self.tick = 5
            else:
                self.tick = 3600

            self.creator  = instance['creator']
            self.fast     = instance['fast']
            self.hardcore = instance['hardcore']
            self.map      = instance['map']
            self.public   = instance['public']

            hashdict =  {
                            "creator":  self.creator,
                            "fast":     str(self.fast),
                            "hardcore": str(self.hardcore),
                            "id":       self.id,
                            "map":      self.map,
                            "public":   str(self.public),
                            "tick":     self.tick
                        }
            logger.trace(f'Method >> (Storing HASH)')
            r.hset(f'instances:{self.id}', mapping=hashdict)
            r.incr(syskey)
        except Exception as e:
            logger.error(f'Method KO [{e}]')
            return None
        else:
            logger.trace(f'Method OK')
            return True

    def store(self):
        try:
            # We push data in final dict
            hashdict =  {
                            "creator":  self.creator,
                            "fast":     str(self.fast),
                            "hardcore": str(self.hardcore),
                            "id":       self.id,
                            "map":      self.map,
                            "public":   str(self.public),
                            "tick":     self.tick
                        }
            logger.success(hashdict)
            logger.trace(f'Method >> (Creating dict)')
            r.hset(f'instances:{self.id}', mapping=hashdict)
            logger.trace(f'Method >> (Storing HASH)')
        except Exception as e:
            logger.error(f'Method KO [{e}]')
            return None
        else:
            logger.trace(f'Method OK')
            return True

    def destroy(self):
        try:
            logger.trace(f'Method >> (Destroying HASH)')
            r.delete(f'instances:{self.id}')
        except Exception as e:
            logger.error(f'Method KO [{e}]')
            return None
        else:
            logger.trace(f'Method OK')
            return True

    def _asdict(self):
        return self.__dict__

if __name__ == '__main__':
    from mysql.methods.fn_creature  import fn_creature_get

    creature = fn_creature_get(None,1)[3]
    instance = RedisInstance(creature = creature, instanceid = None)
    logger.trace(vars(instance))

    instance_dict = {
                        "creator":  creature.id,
                        "fast":     True,
                        "hardcore": True,
                        "map":      1,
                        "public":   True
                    }

    instance.new(instance_dict)
    logger.trace(vars(instance))

    instance.tick = 3600
    instance.store()
    logger.trace(vars(instance))

    logger.info(instance._asdict())
    logger.trace(vars(instance))

    #instance.destroy()

    #instance2 = RedisInstance(creature   = None,instanceid = 1)
    #logger.info(instance2._asdict())
    #logger.info(vars(instance2))
    #instance2.destroy()

#    instance.destroy()
