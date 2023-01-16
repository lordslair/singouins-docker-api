# -*- coding: utf8 -*-

import json
import uuid

from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisEffect:
    def __init__(self, creature=None):
        self.creature = creature
        self.type = 'effect'

    def new(
        self,
        duration_base,
        extra,
        name,
        source,
    ):
        # We check if self.creature exists before continuing
        if self.creature is None:
            logger.warning('[Effect.id:None] Use RedisEffect(Creature) before')
            return False

        # We need to define the new instance.id
        self.id = str(uuid.uuid4())
        self.logh = f'[Effect.id:{self.id}]'

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
            r.hset(f'effects:{self.bearer}:{self.name}', mapping=hashdict)
            r.expire(f'effects:{self.bearer}:{self.name}', self.duration_base)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy(self, name, creatureuuid=None):
        self.logh = '[Effect.id:None]'
        # We check if self.creature exists before continuing
        if self.creature is None and creatureuuid is None:
            logger.warning(f'{self.logh} Method KO (Missing parameter')
            return False

        if creatureuuid is None and self.creature:
            # The RedisEffect was called before, lets set creatureuuid
            creatureuuid = self.creature.id

        if r.exists(f'effects:{creatureuuid}:{name}'):
            pass
        else:
            logger.warning(f'{self.logh} Method KO (KEY NotFound)')
            return True

        try:
            logger.trace(f'{self.logh} Method >> (HASH Destroying)')
            r.delete(f'effects:{creatureuuid}:{name}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def search(self, query, maxpaging=25):
        self.logh = '[Effect.id:None]'
        index = 'effect_idx'
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
            result.id = result.id.removeprefix('effects:')
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
    FT.CREATE effect_idx PREFIX 1 "effects:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "effect_score"
        SCHEMA
            bearer TEXT
            duration_base NUMERIC
            extra TEXT
            id TEXT
            name TEXT
            source TEXT
            type TEXT

    FT.SEARCH effect_idx "" LIMIT 0 10

    FT.DROPINDEX effect_idx
"""

if __name__ == '__main__':
    from nosql.models.RedisCreature import RedisCreature
    creatureuuid = '20671520-85fb-35ad-861a-e8ccebe1ebb9'

    Creature = RedisCreature().get(creatureuuid)
    Effect = RedisEffect(Creature)
    logger.success(Effect.creature)
    logger.success(Effect.creature.id)
    Effect.new(
        duration_base=180,
        extra=None,
        name='Tested',
        source=Creature.id,
    )
    bearer = creatureuuid.replace('-', ' ')
    Effects = RedisEffect().search(query=f'@bearer:{bearer}')
    logger.success(Effects)
    logger.success(Effects.results)
    logger.success(Effects.results[0].id)
    logger.success(Effects._asdict)
    logger.success(Effects._asdict)
    logger.success(RedisEffect(Creature).destroy(name='Tested'))
    Effect.new(
        duration_base=180,
        extra=None,
        name='Tested',
        source=Creature.id,
    )
    logger.success(
        RedisEffect().destroy(creatureuuid=creatureuuid, name='Tested')
        )
