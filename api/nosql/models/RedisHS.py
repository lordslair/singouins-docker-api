# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector            import r


class RedisHS:
    def __init__(self, creature):
        self.creature = creature
        self.hkey     = f'highscores:{creature.id}'
        self.hlog     = f'[Creature.id:{self.creature.id}]'

        if r.exists(self.hkey):
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
            logger.debug(self.__dict__)
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
    HS.incr('plop', 1)
    logger.success(HS._asdict())
