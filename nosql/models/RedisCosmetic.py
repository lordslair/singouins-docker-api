# -*- coding: utf8 -*-

import json
import uuid

from datetime                    import datetime
from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisCosmetic:
    def __init__(self, cosmeticuuid=None):
        self.hkey = 'cosmetics'
        self.logh = f'[Cosmetic.id:{cosmeticuuid}]'
        fullkey = f'{self.hkey}:{cosmeticuuid}'

        try:
            if cosmeticuuid:
                if r.exists(fullkey):
                    logger.trace(f'{self.logh} Method >> (HASH Loading)')
                    hashdict = r.hgetall(fullkey)

                    for k, v in hashdict.items():
                        setattr(self, k, str2typed(v))

                    # We need to add an Auction attribute for the TTL
                    self.duration_left = r.ttl(fullkey)
                    logger.trace(f'{self.logh} Method >> (HASH Loaded)')
                else:
                    logger.trace(f'{self.logh} Method KO (HASH NotFound)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    def __iter__(self):
        yield from self.as_dict().items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        """
        Converts Object into a JSON

        Parameters: None

        Returns: str()
        """
        return self.__str__()

    def as_dict(self):
        """
        Converts Object into a Python dict

        Parameters: None

        Returns: dict()
        """
        return {
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

    def destroy(self):
        """
        Destroys an Object and DEL it from Redis DB.

        Parameters: None

        Returns: bool()
        """
        if hasattr(self, 'id') is False:
            logger.warning(f'{self.logh} Method KO - ID NotSet')
            return False
        if self.id is None:
            logger.warning(f'{self.logh} Method KO - ID NotFound')
            return False

        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            if r.exists(f'{self.hkey}:{self.id}'):
                r.delete(f'{self.hkey}:{self.id}')
            else:
                logger.warning(f'{self.logh} Method KO - NotFound')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def new(
        self,
        creatureuuid,
        cosmetic_caracs,
    ):
        try:
            self.id = str(uuid.uuid4())
            self.logh = f'[Cosmetic.id:{self.id}]'

            self.bearer = creatureuuid
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
                if any([
                    property == 'logh',
                    property == 'hkey',
                ]):
                    pass
                else:
                    hashdict[property] = typed2str(value)

            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(fullkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self
