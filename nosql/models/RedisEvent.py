# -*- coding: utf8 -*-

import time
import uuid

from datetime                    import datetime
from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisEvent:
    def __init__(self):
        self.hlog = '[Event.id:None]'
        logger.trace(f'{self.hlog} Method >> Initialization')

    def new(
        self,
        action_src,
        action_dst,
        action_type,
        action_text,
        action_ttl=None,
    ):
        ts  = time.time_ns() // 1000000  # Time in milliseconds
        eventuuid = str(uuid.uuid4())
        self.hlog = f'[Event.id:{eventuuid}]'

        try:
            logger.trace(f'{self.hlog} Method >> (HASH Creating)')

            hashdict = {
                "dst": typed2str(action_dst),
                "src": typed2str(action_src),
                "action": typed2str(action_text),
                "type": typed2str(action_type),
                "id": eventuuid,
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "timestamp": ts,
            }
            r.hset(f'events:{eventuuid}', mapping=hashdict)
            if action_ttl is not None:
                r.expire(f'events:{eventuuid}', action_ttl)
        except Exception as e:
            logger.error(f'{self.hlog} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.hlog} Method OK')
            return True

    def destroy(self, eventuuid):
        self.hlog = f'[Event.id:{eventuuid}]'
        try:
            logger.trace(f'{self.hlog} Method >> (HASH Destroying)')
            r.delete(f'events:{eventuuid}')
        except Exception as e:
            logger.error(f'{self.hlog} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.hlog} Method OK')
            return True

    def search(self, query, maxpaging=25):
        self.logh = '[Event.id:None]'
        index = 'event_idx'
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
        self._asdict = []
        for result in results.docs:
            result_dict = {}
            del result.payload
            result.id = result.id.removeprefix('events:')
            for attr, value in result.__dict__.items():
                setattr(result, attr, str2typed(value))
                result_dict[attr] = getattr(result, attr)
            self._asdict.append(result_dict)

        self.results = results.docs

        logger.trace(f'{self.logh} Method OK')
        return self
