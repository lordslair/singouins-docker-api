# -*- coding: utf8 -*-

from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r


class RedisHS:
    def __init__(self, creature=None):
        if creature is not None:
            self.creature = creature
            self.hlog = f'[Creature.id:{self.creature.id}]'
            self.hkey = f'highscores:{creature.id}'
        else:
            self.hlog = '[Creature.id:None]'

        if hasattr(self, 'hkey') and r.exists(self.hkey):
            # The HighScores does already exist in redis
            try:
                hashdict = r.hgetall(self.hkey)
                logger.trace(f'{self.hlog} Method >> (HASH Loading)')

                for k, v in hashdict.items():
                    # We create the object attribute with converted INT
                    setattr(self, k, int(v))

                logger.trace(f'{self.hlog} Method >> (HASH Loaded)')
            except Exception as e:
                logger.error(f'{self.hlog} Method KO [{e}]')
            else:
                logger.trace(f'{self.hlog} Method OK')
        else:
            # The HighScores does not already exist in redis
            logger.trace(f'{self.hlog} Method >> (HASH NotFound)')
            pass

    def incr(self, key, count=1):
        try:
            logger.trace(f'{self.hlog} Method >> (HASH Incrementing)')
            # We increment the object attribute
            if hasattr(self, key):
                setattr(self, key, getattr(self, key) + count)
                # We increment the hash key
                r.hincrby(self.hkey, key, count)
            else:
                setattr(self, key, count)
                # We create the hash key
                r.hset(self.hkey, key, count)

        except Exception as e:
            logger.error(f'{self.hlog} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.hlog} Method OK')
            return True

    def destroy(self):
        try:
            logger.trace(f'{self.hlog} Method >> (Destroying HASH)')
            r.delete(self.hkey)
        except Exception as e:
            logger.error(f'{self.hlog} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.hlog} Method OK')
            return True

    def search(self, query, maxpaging=25):
        self.hlog = '[Creature.id:None]'
        index = 'highscore_idx'
        try:
            r.ft(index).info()
        except Exception as e:
            logger.error(f'{self.hlog} Method KO [{e}]')
            return None
        else:
            # logger.trace(r.ft(index).info())
            pass

        try:
            logger.trace(f'{self.hlog} Method >> (Searching {query})')
            # Query("search engine").paging(0, 10)
            # f"@bearer:[{bearerid} {bearerid}]"
            results = r.ft(index).search(
                Query(query).paging(0, maxpaging)
                )
        except Exception as e:
            logger.error(f'{self.hlog} Method KO [{e}]')
            return None
        else:
            # logger.trace(results)
            pass

        # If we are here, we got results
        highscores = list()
        for result in results.docs:
            highscore = dict()
            for key, val in result.__dict__.items():
                if key == 'id':
                    highscore[key] = val.removeprefix('highscores:')
                elif val is not None:
                    highscore[key] = int(val)
                else:
                    highscore[key] = None
            highscores.append(highscore)

        logger.trace(f'{self.hlog} Method OK')
        return highscores

    def _asdict(self):
        tree = {}
        for key, val in self.__dict__.items():
            if any([
                key == 'creature',
                key == 'hkey',
                key == 'hlog',
            ]):
                pass
            else:
                """Return nested dict by splitting the keys on a delimiter."""
                t = tree
                prev = None
                for part in key.split('_'):
                    if prev is not None:
                        t = t.setdefault(prev, {})
                    prev = part
                else:
                    t.setdefault(prev, val)
        return tree


if __name__ == '__main__':
    from nosql.models.RedisCreature import RedisCreature
    Creature = RedisCreature().get('20671520-85fb-35ad-861a-e8ccebe1ebb9')
    HS = RedisHS(Creature)
    logger.success(HS)
    logger.success(HS._asdict())
    HS.incr('global_kills', 1)
    logger.success(HS._asdict())
    logger.warning(HS.search(query='*'))
