# -*- coding: utf8 -*-

import json
import uuid

from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisStatus:
    def __init__(self, creature=None):
        self.creature = creature
        self.type = 'status'

    def new(
        self,
        duration_base,
        extra,
        name,
        source,
    ):
        # We check if self.creature exists before continuing
        if self.creature is None:
            logger.warning('[Status.id:None] Use RedisStatus(Creature) before')
            return False

        # We need to define the new instance.id
        self.id = str(uuid.uuid4())
        self.logh = f'[Status.id:{self.id}]'

        try:
            # We push data in final dict
            logger.trace(f'{self.logh} Method >> (HASH Creating)')
            # We convert dict > JSON
            if isinstance(extra, dict):
                self.extra = json.dumps(extra)
            if extra is None:
                self.extra = None

            self.bearer        = self.creature.id
            self.duration_base = duration_base
            self.duration_left = duration_base
            self.name          = name
            self.source        = source

            hashdict = {
                "bearer": self.bearer,
                "duration_base": self.duration_base,
                "extra": typed2str(self.extra),
                "name": self.name,
                "source": self.source,
                "type": self.type
            }

            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(f'statuses:{self.bearer}:{self.name}', mapping=hashdict)
            r.expire(f'statuses:{self.bearer}:{self.name}', self.duration_base)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy(self, name, creatureuuid=None):
        self.logh = '[Status.id:None]'
        # We check if self.creature exists before continuing
        if self.creature is None and creatureuuid is None:
            logger.warning(f'{self.logh} Method KO (Missing parameter')
            return False

        if creatureuuid is None and self.creature:
            # The RedisStatus was called before, lets set creatureuuid
            creatureuuid = self.creature.id

        if r.exists(f'statuses:{creatureuuid}:{name}'):
            pass
        else:
            logger.warning(f'{self.logh} Method KO (KEY NotFound)')
            return True

        try:
            logger.trace(f'{self.logh} Method >> (HASH Destroying)')
            r.delete(f'statuses:{creatureuuid}:{name}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def search(self, query, maxpaging=25):
        self.logh = '[Status.id:None]'
        index = 'status_idx'
        try:
            r.ft(index).info()
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(r.ft(index).info())
            pass

        try:
            logger.trace(f'{self.logh} Method >> (Searching {query})')
            results = r.ft(index).search(Query(query).paging(0, maxpaging))
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(results)
            pass

        # If we are here, we got results
        self._asdict = []
        for result in results.docs:
            result_dict = {}
            # We remove from the final result an internal result attr
            del result.payload
            # We fetch the key TTL
            result.ttl = r.ttl(result.id)
            # We remove the prexix added by RediSearch
            result.id = result.id.removeprefix('statuses:')
            # We remove the suffix of the key
            result.id = result.id.removesuffix(f':{result.name}')
            for attr, value in result.__dict__.items():
                setattr(result, attr, str2typed(value))
                result_dict[attr] = getattr(result, attr)
            self._asdict.append(result_dict)

        self.results = results.docs

        logger.trace(f'{self.logh} Method OK')
        return self


"""
    FT.CREATE status_idx PREFIX 1 "statuses:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "status_score"
        SCHEMA
            bearer TEXT
            duration_base NUMERIC
            extra TEXT
            id TEXT
            name TEXT
            source TEXT
            type TEXT

    FT.SEARCH status_idx "" LIMIT 0 10

    FT.DROPINDEX status_idx
"""

if __name__ == '__main__':
    from nosql.models.RedisCreature import RedisCreature
    creatureuuid = '20671520-85fb-35ad-861a-e8ccebe1ebb9'

    Creature = RedisCreature().get(creatureuuid)
    Status = RedisStatus(Creature)
    logger.success(Status.creature)
    logger.success(Status.creature.id)
    Status.new(
        duration_base=180,
        extra=None,
        name='Tested',
        source=Creature.id,
    )
    bearer = creatureuuid.replace('-', ' ')
    Statuses = RedisStatus().search(query=f'@bearer:{bearer}')
    logger.success(Statuses)
    logger.success(Statuses.results)
    logger.success(Statuses.results[0].id)
    logger.success(Statuses._asdict)
    logger.success(Statuses._asdict)
    logger.success(RedisStatus(Creature).destroy(name='Tested'))
    Status.new(
        duration_base=180,
        extra=None,
        name='Tested',
        source=Creature.id,
    )
    logger.success(
        RedisStatus().destroy(creatureuuid=creatureuuid, name='Tested')
        )
