# -*- coding: utf8 -*-

import re
import uuid

from datetime                    import datetime
from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r


def str2typed(string):
    # BOOLEAN False
    if string == 'False':
        return False
    # BOOLEAN True
    elif string == 'True':
        return True
    # None
    elif string == 'None':
        return None
    # Date
    elif re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', string):
        return string
    # INT
    elif string.isdigit():
        return int(string)
    else:
        return string


def typed2str(string):
    # None
    if string is None:
        return 'None'
    # BOOLEAN True
    elif string is True:
        return 'True'
    # BOOLEAN False
    elif string is False:
        return 'False'
    else:
        return string


class RedisCosmetic:
    def __init__(self, creature=None):
        self.creature = creature
        self.hkey     = 'cosmetics'

    def destroy(self, itemuuid):
        try:
            self.item = itemuuid
            self.logh = f'[Cosmetic.id:{self.item}]'
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            if r.exists(f'{self.hkey}:{itemuuid}'):
                r.delete(f'{self.hkey}:{itemuuid}')
            else:
                logger.trace(f'{self.logh} Method KO - NotFound')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def destroy_all(self):
        self.logh = '[Cosmetic.id:None]'
        index = 'cosmetic_idx'
        try:
            r.ft(index).info()
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(r.ft(index).info())
            pass

        try:
            bearer = self.creature.id.replace('-', ' ')
            logger.trace(
                f'{self.logh} Method >> '
                f'(Searching @bearer:{bearer})'
                )
            # Query("search engine").paging(0, 10)
            # f"@bearer:[{bearerid} {bearerid}]"
            results = r.ft(index).search(
                Query(
                    f"@bearer:{bearer}"
                    ).paging(0, 25)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(results)
            pass

        try:
            for result in results.docs:
                self.destroy(result.id.removeprefix('cosmetics:'))
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self, itemuuid):
        self.logh = f'[Cosmetic.id:{itemuuid}]'
        fullkey = f'{self.hkey}:{itemuuid}'
        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            if r.exists(fullkey):
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

    def get_all(self):
        self.logh = '[Cosmetic.id:None]'
        index = 'cosmetic_idx'
        try:
            r.ft(index).info()
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(r.ft(index).info())
            pass

        try:
            bearer = self.creature.id.replace('-', ' ')
            logger.trace(
                f'{self.logh} Method >> '
                f'(Searching @bearer:{bearer})'
                )
            # Query("search engine").paging(0, 10)
            # f"@bearer:[{bearerid} {bearerid}]"
            results = r.ft(index).search(
                Query(
                    f"@bearer:{bearer}"
                    ).paging(0, 25)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(results)
            pass

        # If we are here, we got results
        items = []
        for result in results.docs:
            item = {
                "bearer": str2typed(result.bearer),
                "bound": str2typed(result.bound),
                "bound_type": result.bound_type,
                "data": {
                    "beforeArmor": str2typed(result.beforeArmor),
                    "hasGender": str2typed(result.hasGender),
                    "hideArmor": str2typed(result.hideArmor),
                },
                "date": result.date,
                "id": result.id.removeprefix('cosmetics:'),
                "metaid": str2typed(result.metaid),
                "rarity": result.rarity,
                "state": str2typed(result.state),
            }
            items.append(item)

        logger.trace(f'{self.logh} Method OK')
        return items

    def new(self, cosmetic_caracs):
        try:
            self.id = str(uuid.uuid4())
            self.logh = f'[Cosmetic.id:{self.id}]'

            self.bearer = self.creature.id
            self.beforeArmor = cosmetic_caracs['data']['beforeArmor']
            self.bound = True
            self.bound_type = 'BoP'
            self.hasGender = cosmetic_caracs['data']['hasGender']
            self.hideArmor = cosmetic_caracs['data']['hideArmor']
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.metaid = cosmetic_caracs['metaid']
            self.rarity = 'Epic'
            self.state = 100
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (Creating dict)')
        try:
            fullkey = f'{self.hkey}:{self.id}'
            # We push data in final dict
            hashdict = {}
            # We loop over object properties to create it
            for property, value in self.__dict__.items():
                if property not in ['creature', 'logh', 'hkey']:
                    hashdict[property] = typed2str(value)

            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(fullkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def _asdict(self):
        hashdict = {
            "bearer": self.bearer,
            "bound": self.bound,
            "bound_type": self.bound_type,
            "data": {
                "beforeArmor": self.beforeArmor,
                "hasGender": self.hasGender,
                "hideArmor": self.hideArmor,
            },
            "date": self.date,
            "id": self.id,
            "metaid": self.metaid,
            "rarity": self.rarity,
            "state": self.state,
        }
        return hashdict


if __name__ == '__main__':
    """
    FT.CREATE cosmetic_idx PREFIX 1 "cosmetics:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "cosmetic_score"
        SCHEMA
            bearer TEXT
            bound TEXT
            bound_type TEXT
            id TAG
            metaid NUMERIC
            state NUMERIC
            rarity TEXT

    FT.SEARCH cosmetic_idx "Common" LIMIT 0 10

    FT.DROPINDEX cosmetic_idx
    """
