# -*- coding: utf8 -*-

from nosql.connector            import *

from mysql.methods.fn_creature  import fn_creature_get

class RedisStatus:
    def __init__(self,creature):
        self.hkey     = f'statuses:{creature.instance}:{creature.id}'
        self.logh     = f'[creature.id:{creature.id}]'

        # The pre-generated statuses does not already exist in redis
        logger.trace(f'{self.logh} Method >> (Object Creating)')

        try:
            self.bearer        = creature.id
            self.duration_base = None
            self.duration_left = None
            self.name          = None
            self.source        = None
            self.type          = 'status'
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method >> (Object Creating)')
            logger.trace(f'{self.logh} Method OK')

        # Whatever the scenarion, We push data in the object
        try:
            logger.trace(f'{self.logh} Method >> (dict Creating)')
            self.dict = {
                            "bearer":        self.bearer,
                            "duration_base": self.duration_base,
                            "duration_left": self.duration_left,
                            "name":          self.name,
                            "source":        self.source,
                            "type":          self.type
                        }
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method >> (dict Created)')
            logger.trace(f'{self.logh} Method OK')

    def store(self):
        try:
            # We push data in final dict
            logger.trace(f'{self.logh} Method >> (Creating dict)')
            hashdict =  {
                            "bearer":        self.bearer,
                            "duration_base": self.duration_base,
                            "name":          self.name,
                            "source":        self.source,
                            "type":          self.type
                        }
            logger.trace(f'{self.logh} Method >> (hashdict:{hashdict})')

            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(f'{self.hkey}:{self.name}', mapping=hashdict)
            r.expire(f'{self.hkey}:{self.name}', self.duration_base)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self,name):
        try:
            if r.exists(f'{self.hkey}:{name}'):
                # The status does already exist in Redis
                hash = r.hgetall(f'{self.hkey}:{name}')
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                self.bearer        = int(hash['bearer'])
                self.duration_base = int(hash['duration_base'])
                self.duration_left = int(r.ttl(f'{self.hkey}:{name}'))
                self.name          = hash['name']
                self.source        = int(hash['source'])
                self.type          = hash['type']

                self.dict = {
                                "bearer":        self.bearer,
                                "duration_base": self.duration_base,
                                "duration_left": self.duration_left,
                                "name":          self.name,
                                "source":        self.source,
                                "type":          self.type
                            }
            else:
                logger.trace(f'{self.logh} Method KO - HASH not found')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def get_all(self):
        path      = f'{self.hkey}:*'
        #                         └────> Wildcard for {statusmetaname}
        statuses  = []

        try:
            # We get the list of keys for all the statuses
            keys        = r.keys(path)
            logger.debug(f'keys:{keys}')
            sorted_keys = sorted(keys)
            logger.debug(f'sorted_keys:{sorted_keys}')
            # We initialize indexes used during iterations
            index       = 0
            # We create a pipeline to query the keys TTL
            p = r.pipeline()
            for key in sorted_keys:
                p.hgetall(key)
                p.ttl(key)
            pipeline = p.execute()

            # We loop over the status keys to build the data
            for key in sorted_keys:
                logger.debug(f'key:{key}')
                status = {
                            "bearer":        self.bearer,
                            "duration_base": int(pipeline[index]['duration_base']),
                            "duration_left": int(pipeline[index+1]),
                            "id":            int(1 + index/2),
                            "name":          pipeline[index]['name'],
                            "source":        int(pipeline[index]['source']),
                            "type":          pipeline[index]['duration_base']
                         }
                # We update the index for next iteration
                index += 2
                # We add the status into statuses list
                statuses.append(status)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return statuses

    def destroy(self,name):
        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(f'{self.hkey}:{name}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True
