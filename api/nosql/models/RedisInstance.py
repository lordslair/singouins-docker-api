# -*- coding: utf8 -*-

import copy
import uuid

from loguru                     import logger

from nosql.connector            import r
from nosql.variables             import str2typed, typed2str


class RedisInstance:
    def __init__(self):
        self.hkey     = 'instances'

    def get(self, instanceuuid):
        self.logh = f'[Instance.id:{instanceuuid}]'
        fullkey = f'{self.hkey}:{instanceuuid}'

        try:
            if r.exists(fullkey):
                logger.trace(f'{self.logh} Method >> (HASH Loading)')
                hashdict = r.hgetall(fullkey)
            else:
                logger.trace(f'{self.logh} Method KO (HASH NotFound)')
                return False

            for k, v in hashdict.items():
                setattr(self, k, str2typed(v))
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def new(self, instance):
        # We need to define the new instance.id
        self.id = str(uuid.uuid4())
        self.logh = f'[Instance.id:{self.id}]'

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
                "fast": typed2str(self.fast),
                "hardcore": typed2str(self.hardcore),
                "id": self.id,
                "map": self.map,
                "public": typed2str(self.public),
                "tick": self.tick
            }
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(f'instances:{self.id}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def destroy(self, instanceuuid):
        try:
            self.logh = f'[Instance.id:{instanceuuid}]'
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(f'{self.hkey}:{instanceuuid}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def _asdict(self):
        clone = copy.deepcopy(self)
        if clone.logh:
            del clone.logh
        if clone.hkey:
            del clone.hkey
        return clone.__dict__


if __name__ == '__main__':
    Instance = RedisInstance().new({
        "creator": 'ac6d31f3-58b6-4d0b-a6a1-3725c4cb177a',
        "fast": True,
        "hardcore": False,
        "map": 2,
        "public": True,
    })
    logger.success(Instance._asdict())
    logger.success(RedisInstance().get(Instance.id)._asdict())
    logger.success(RedisInstance().destroy(Instance.id))
    logger.success(RedisInstance().get(Instance.id))

    """
    FT.CREATE instance_idx PREFIX 1 "instances:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "instance_score"
        SCHEMA
            creator TEXT
            fast TEXT
            hardcore TEXT
            id TEXT
            map NUMERIC
            public TEXT
            tick NUMERIC

    FT.SEARCH instance_idx "Turlututu" LIMIT 0 10

    FT.DROPINDEX instance_idx
    """
