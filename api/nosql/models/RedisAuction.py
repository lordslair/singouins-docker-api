# -*- coding: utf8 -*-

from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r

from nosql.models.RedisMeta      import RedisMeta
from nosql.variables             import str2typed


class RedisAuction:
    def __init__(self):
        self.hkey     = 'auctions'

    def destroy(self, auctionuuid):
        try:
            self.logh = f'[Auction.id:{auctionuuid}]'
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(f'{self.hkey}:{auctionuuid}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self, auctionuuid):
        self.logh = f'[Auction.id:{auctionuuid}]'
        fullkey = f'{self.hkey}:{auctionuuid}'
        try:
            if r.exists(fullkey):
                logger.trace(f'{self.logh} Method >> (HASH Loading)')
                hashdict = r.hgetall(fullkey)
            else:
                logger.warning(f'{self.logh} Method KO (HASH NotFound)')
                return False

            for k, v in hashdict.items():
                setattr(self, k, str2typed(v))

            # We neet to add an Auction attribute for the TTL
            self.duration_left = r.ttl(fullkey)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

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

            logger.trace(f'{self.logh} Method >> (Creating dict)')
            # We push data in final dict
            self.duration_base = duration
            self.id            = Item.id
            self.item          = Item
            self.meta          = RedisMeta(Item.metaid, Item.metatype)
            self.price         = price
            self.seller        = Creature

            # To use _asdict() just after if needed
            self.duration_left = duration
            self.metaid        = self.meta.id
            self.metaname      = self.meta.name
            self.metatype      = self.item.metatype
            self.sellerid      = self.seller.id
            self.sellername    = self.seller.name
            self.rarity        = self.item.rarity

            hashdict = {
                "duration_base": self.duration_base,
                "id": self.id,
                "metaid": self.meta.id,
                "metaname": self.meta.name,
                "metatype": self.item.metatype,
                "price": self.price,
                "rarity": self.item.rarity,
                "sellerid": self.seller.id,
                "sellername": self.seller.name,
            }
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(fullkey, mapping=hashdict)
            r.expire(fullkey, self.duration_base)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def search(self, query, maxpaging=25):
        self.logh = '[Auction.id:None]'
        index = 'auction_idx'
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
        auctions = []
        for result in results.docs:
            auction = {
                "duration_base": str2typed(result.duration_base),
                "duration_left": r.ttl(result.id),
                "id": result.id.removeprefix('auctions:'),
                "metaid": str2typed(result.metaid),
                "metaname": result.metaname,
                "metatype": result.metatype,
                "price": str2typed(result.price),
                "rarity": result.rarity,
                "sellerid": result.sellerid,
                "sellername": result.sellername,
                }
            auctions.append(auction)

        logger.trace(f'{self.logh} Method OK')
        return auctions

    def _asdict(self):
        hashdict = {
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
        return hashdict


if __name__ == '__main__':
    from nosql.models.RedisCreature import RedisCreature
    from nosql.models.RedisItem import RedisItem

    Creature = RedisCreature().get('20671520-85fb-35ad-861a-e8ccebe1ebb9')
    logger.info(Creature._asdict())
    Item = RedisItem().get('6421c5d8-9f5e-42f9-b0df-9e9a3b5ad910')
    logger.info(Item._asdict())

    Auction = RedisAuction().new(Creature, Item, 666)
    logger.info(Auction._asdict())
    Auction = RedisAuction().get(Item.id)
    logger.info(Auction._asdict())

    logger.success(RedisAuction().search(query='@metatype:weapon'))

    logger.success(RedisAuction().destroy(Item.id))

    """
    FT.CREATE auction_idx PREFIX 1 "auctions:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "auction_score"
        SCHEMA
            duration_base NUMERIC
            id TEXT
            metaid NUMERIC
            metaname TEXT
            metatype TEXT
            price NUMERIC
            rarity TEXT
            sellerid TEXT
            sellername TEXT

    FT.SEARCH auction_idx "Common" LIMIT 0 10

    FT.DROPINDEX auction_idx
    """
