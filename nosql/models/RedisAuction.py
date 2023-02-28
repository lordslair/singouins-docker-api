# -*- coding: utf8 -*-

import json

from loguru                      import logger

from nosql.connector             import r
from nosql.models.RedisMeta      import RedisMeta
from nosql.variables             import str2typed


class RedisAuction:
    def __init__(self, auctionuuid=None):
        self.hkey = 'auctions'
        self.logh = f'[Auction.id:{auctionuuid}]'
        fullkey = f'{self.hkey}:{auctionuuid}'

        try:
            if auctionuuid:
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
            "duration_base": self.duration_base,
            "duration_left": self.duration_left,
            "id": self.id,
            "metaid": self.metaid,
            "metaname": self.metaname,
            "metatype": self.metatype,
            "price": self.price,
            "rarity": self.rarity,
            "sellerid": self.sellerid,
            "sellername": self.sellername,
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
            if r.exists(f'{self.hkey}:{self.id}'):
                logger.trace(f'{self.logh} Method >> (HASH Destroying)')
                r.delete(f'{self.hkey}:{self.id}')
            else:
                logger.warning(f'{self.logh} Method KO (HASH NotFound)')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method >> (HASH Destroyed)')
            return True

    def new(
        self,
        Creature,
        Item,
        price,
        duration=172800,
    ):
        try:
            self.logh = f'[Auction.id:{Item.id}]'
            fullkey = f'{self.hkey}:{Item.id}'

            if r.exists(fullkey):
                logger.trace(f'{self.logh} Method KO (Already exists)')
                return False

            logger.trace(f'{self.logh} Method >> (Dict Creating)')
            # We push data in final dict
            self.duration_base = duration
            self.id            = Item.id
            self.item          = Item
            self.meta          = RedisMeta(Item.metaid, Item.metatype)
            self.price         = price
            self.seller        = Creature

            # To use as_dict() just after if needed
            self.duration_left = duration
            self.metaid        = self.meta.id
            self.metaname      = self.meta.name
            self.metatype      = self.item.metatype
            self.sellerid      = self.seller.id
            self.sellername    = self.seller.name
            self.rarity        = self.item.rarity

            hashdict = {
                "duration_base": self.duration_base,
                "duration_left": self.duration_left,
                "id": self.id,
                "metaid": self.meta.id,
                "metaname": self.meta.name,
                "metatype": self.item.metatype,
                "price": self.price,
                "rarity": self.item.rarity,
                "sellerid": self.seller.id,
                "sellername": self.seller.name,
            }
            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(fullkey, mapping=hashdict)
            r.expire(fullkey, self.duration_base)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self
