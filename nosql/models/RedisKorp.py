# -*- coding: utf8 -*-

import copy
import uuid

from datetime                    import datetime
from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisKorp:
    def __init__(self):
        self.hkey     = 'korps'

    def destroy(self, korpuuid):
        self.logh = f'[Korp.id:{korpuuid}]'
        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(f'{self.hkey}:{korpuuid}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self, korpuuid):
        self.logh = f'[Korp.id:{korpuuid}]'
        if r.exists(f'{self.hkey}:{korpuuid}'):
            logger.trace(f'{self.logh} Method >> (KEY Loading)')
            try:
                hashdict = r.hgetall(f'{self.hkey}:{korpuuid}')

                self.id = hashdict['id']
                self.name = str2typed(hashdict['name'])
                self.leader = str2typed(hashdict['leader'])
                self.created = hashdict['created']

                logger.trace(f'{self.logh} Method >> (KEY Loaded)')
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
                return None
            else:
                logger.trace(f'{self.logh} Method OK')
                return self
        else:
            logger.warning(f'{self.logh} Method KO - NotFound')
            return False

    def new(self, creature, korpname):
        self.logh = '[Korp.id:None]'
        # Checking if it exists
        logger.trace(f'{self.logh} Method >> (Checking uniqueness)')
        try:
            possible_uuid = str(
                uuid.uuid3(uuid.NAMESPACE_DNS, korpname)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            self.logh = f'[Korp.id:{possible_uuid}]'
            if r.exists(f'{self.hkey}:{possible_uuid}'):
                logger.error(f'{self.logh} Method KO - Already Exists')
                return False

        logger.trace(f'{self.logh} Method >> (Creating dict)')
        try:
            self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.id = possible_uuid
            self.leader = creature.id
            self.name = korpname
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (Storing HASH)')
        try:
            hashdict = {
                "created": self.created,
                "date": self.date,
                "id": self.id,
                "name": typed2str(self.name),
                "leader": self.leader,
            }
            r.hset(f'{self.hkey}:{self.id}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def search(self, query, maxpaging=25):
        self.logh = '[Korp.id:None]'
        index = 'korp_idx'
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
            # Query("search engine").paging(0, 10)
            # f"@bearer:[{bearerid} {bearerid}]"
            results = r.ft(index).search(
                Query(query).paging(0, maxpaging)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(results)
            pass

        # If we are here, we got results
        korps = []
        for result in results.docs:
            korp = {
                "created": result.created,
                "date": result.date,
                "id": result.id.removeprefix('korps:'),
                "name": typed2str(result.name),
                "leader": result.leader,
                }
            korps.append(korp)

        logger.trace(f'{self.logh} Method OK')
        return korps

    def _asdict(self):
        clone = copy.deepcopy(self)
        if clone.logh:
            del clone.logh
        if clone.hkey:
            del clone.hkey
        return clone.__dict__


if __name__ == '__main__':
    pass

    """
    FT.CREATE korp_idx PREFIX 1 "korps:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "korp_score"
        SCHEMA
            id TAG
            leader TEXT
            name TEXT

    FT.SEARCH korp_idx "YSquad" LIMIT 0 10

    FT.DROPINDEX korp_idx
    """
