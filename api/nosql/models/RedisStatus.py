# -*- coding: utf8 -*-

import json

from loguru                     import logger

from nosql.connector            import r


class RedisStatus:
    def __init__(self, creature):
        self.hkey     = f'statuses:{creature.instance}:{creature.id}'
        self.instance = creature.instance
        self.logh     = f'[Creature.id:{creature.id}]'

        # The pre-generated statuses does not already exist in redis
        logger.trace(f'{self.logh} Method >> Initialization')

        try:
            self.bearer        = creature.id
            self.duration_base = None
            self.duration_left = None
            self.extra         = None
            self.name          = None
            self.source        = None
            self.type          = 'status'
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    def add(self,
            duration_base,
            extra,
            name,
            source):
        try:
            # We push data in final dict
            logger.trace(f'{self.logh} Method >> (HASH Creating)')
            # We convert dict > JSON
            if isinstance(extra, dict):
                self.extra = json.dumps(extra)
            if extra is None:
                self.extra = ''

            self.duration_base = duration_base
            self.duration_left = duration_base
            self.name          = name
            self.source        = source

            hashdict = {
                "bearer": self.bearer,
                "duration_base": self.duration_base,
                "extra": self.extra,
                "name": self.name,
                "source": self.source,
                "type": self.type
            }

            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(f'{self.hkey}:{self.name}', mapping=hashdict)
            r.expire(f'{self.hkey}:{self.name}', self.duration_base)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self, name):
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

                # We convert JSON > dict
                if hash['extra'] == '':
                    self.extra = None
                elif isinstance(hash['extra'], str):
                    self.extra = json.loads(hash['extra'])
            else:
                logger.warning(f'{self.logh} Method KO - HASH not found')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')

            return {
                "bearer": self.bearer,
                "duration_base": self.duration_base,
                "duration_left": self.duration_left,
                "extra": self.extra,
                "id": 1,
                "name": self.name,
                "source": self.source,
                "type": self.type
            }

    def get_all(self):
        path      = f'{self.hkey}:*'
        #                         └────> Wildcard for {status_name}
        statuses  = []

        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            # We get the list of keys for all the statuses
            keys        = r.keys(path)
            sorted_keys = sorted(keys)
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
                logger.trace(f'key:{key}')
                # We convert JSON > dict
                if pipeline[index]['extra'] == '':
                    extra = None
                elif isinstance(pipeline[index]['extra'], str):
                    extra = json.loads(pipeline[index]['extra'])
                status = {
                    "bearer": self.bearer,
                    "duration_base": int(pipeline[index]['duration_base']),
                    "duration_left": int(pipeline[index + 1]),
                    "extra": extra,
                    "id": int(1 + index / 2),
                    "name": pipeline[index]['name'],
                    "source": int(pipeline[index]['source']),
                    "type": pipeline[index]['type']
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

    def get_all_instance(self):
        path      = f'statuses:{self.instance}:*:*'
        #                                      │ └─> Wildcard for {status_name}
        #                                      └───> Wildcard for {creatureid}
        statuses  = []

        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            # We get the list of keys for all the statuses
            keys        = r.keys(path)
            sorted_keys = sorted(keys)
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
                logger.trace(f'key:{key}')
                # We convert JSON > dict
                if pipeline[index]['extra'] == '':
                    extra = None
                elif isinstance(pipeline[index]['extra'], str):
                    extra = json.loads(pipeline[index]['extra'])
                status = {
                    "bearer": int(pipeline[index]['bearer']),
                    "duration_base": int(pipeline[index]['duration_base']),
                    "duration_left": int(pipeline[index + 1]),
                    "extra": extra,
                    "id": int(1 + index / 2),
                    "name": pipeline[index]['name'],
                    "source": int(pipeline[index]['source']),
                    "type": pipeline[index]['type']
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

    def destroy(self, name):
        try:
            logger.trace(f'{self.logh} Method >> (HASH Destroying)')
            r.delete(f'{self.hkey}:{name}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True
