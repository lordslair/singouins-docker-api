# -*- coding: utf8 -*-

import json

from loguru                     import logger

from nosql.connector            import r


class RedisCd:
    def __init__(self, creature):
        self.hkey     = f'cds:{creature.instance}:{creature.id}'
        self.instance = creature.instance
        self.logh     = f'[Creature.id:{creature.id}]'

        # The pre-generated cds does not already exist in redis
        logger.trace(f'{self.logh} Method >> Initialization')

        try:
            self.bearer        = creature.id
            self.duration_base = None
            self.duration_left = None
            self.extra         = None
            self.name          = None
            self.source        = None
            self.type          = 'cd'
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
                # The cd does already exist in Redis
                hash = r.hgetall(f'{self.hkey}:{name}')
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                self.bearer        = hash['bearer']
                self.duration_base = int(hash['duration_base'])
                self.duration_left = int(r.ttl(f'{self.hkey}:{name}'))
                self.name          = hash['name']
                self.source        = hash['source']
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
        #                         └────> Wildcard for {skill_name}
        cds  = []

        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            # We get the list of keys for all the cds
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

            # We loop over the cd keys to build the data
            for key in sorted_keys:
                logger.trace(f'key:{key}')
                # We convert JSON > dict
                if pipeline[index]['extra'] == '':
                    extra = None
                elif isinstance(pipeline[index]['extra'], str):
                    extra = json.loads(pipeline[index]['extra'])
                cd = {
                    "bearer": self.bearer,
                    "duration_base": int(pipeline[index]['duration_base']),
                    "duration_left": int(pipeline[index + 1]),
                    "extra": extra,
                    "id": int(1 + index / 2),
                    "name": pipeline[index]['name'],
                    "source": pipeline[index]['source'],
                    "type": pipeline[index]['type']
                }
                # We update the index for next iteration
                index += 2
                # We add the cd into cds list
                cds.append(cd)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return cds

    def get_all_instance(self):
        path      = f'cds:{self.instance}:*:*'
        #                                      │ └─> Wildcard for {skill_name}
        #                                      └───> Wildcard for {creatureid}
        cds  = []

        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            # We get the list of keys for all the cds
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

            # We loop over the cd keys to build the data
            for key in sorted_keys:
                logger.trace(f'key:{key}')
                # We convert JSON > dict
                if pipeline[index]['extra'] == '':
                    extra = None
                elif isinstance(pipeline[index]['extra'], str):
                    extra = json.loads(pipeline[index]['extra'])
                cd = {
                    "bearer": pipeline[index]['bearer'],
                    "duration_base": int(pipeline[index]['duration_base']),
                    "duration_left": int(pipeline[index + 1]),
                    "extra": extra,
                    "id": int(1 + index / 2),
                    "name": pipeline[index]['name'],
                    "source": pipeline[index]['source'],
                    "type": pipeline[index]['type']
                }
                # We update the index for next iteration
                index += 2
                # We add the cd into cds list
                cds.append(cd)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return cds

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
