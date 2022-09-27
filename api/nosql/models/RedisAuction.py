# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector            import r

from nosql.models.RedisMeta    import RedisMeta


class RedisAuction:
    def __init__(self):
        self.hkey     = 'auctions'

    def destroy(self, item):
        try:
            self.item = item
            self.logh = f'[Item.id:{self.item.id}]'
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(f'{self.hkey}:{item.metatype}:{item.metaid}:{item.id}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self, item):
        self.item = item
        self.logh = f'[Item.id:{self.item.id}]'
        fullkey = f'{self.hkey}:{item.metatype}:{item.metaid}:{item.id}'
        try:
            if r.exists(fullkey):
                logger.trace(f'{self.logh} Method >> (HASH Loading)')
                hashdict = r.hgetall(fullkey)
            else:
                logger.warning(f'{self.logh} Method KO (HASH NotFound)')
                return False

            for k, v in hashdict.items():
                # We create the object attribute with converted INT
                if v.isdigit():
                    newv = int(v)
                else:
                    newv = v
                setattr(self, k, newv)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def sell(
            self,
            creature,
            item,
            price,
            duration=172800,
            ):
        try:
            self.item = item
            self.logh = f'[Item.id:{self.item.id}]'
            fullkey = f'{self.hkey}:{item.metatype}:{item.metaid}:{item.id}'

            if r.exists(fullkey):
                logger.trace(f'{self.logh} Method KO (Already exists)')
                return False

            logger.trace(f'{self.logh} Method >> (Creating dict)')
            # We push data in final dict
            self.duration_base = duration
            self.id            = item.id
            self.meta          = RedisMeta(item.metaid, item.metatype)
            self.price         = price
            self.seller        = creature
            hashdict = {
                "duration_base": self.duration_base,
                "id": self.id,
                "meta_id": self.meta.id,
                "meta_name": self.meta.name,
                "price": self.price,
                "rarity": self.item.rarity,
                "seller_id": self.seller.id,
                "seller_name": self.seller.name,
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

    def search(
        self,
        metaid=None,
        metatype=None,
    ):
        try:
            self.logh = f'[Meta.type:{metatype},Meta.id:{metaid}]'
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            if metaid and metatype:
                path = f'{self.hkey}:{metatype}:{metaid}:*'
            elif metatype:
                path = f'{self.hkey}:{metatype}:*'
            elif metaid:
                path = f'{self.hkey}:*'
            else:
                logger.warning(f'{self.logh} Method KO - Wrong parameters')
                return None

            keys  = r.keys(path)
            auctions = []
            # We initialize indexes used during iterations
            index = 0
            # We create a pipeline to query the keys TTL
            p = r.pipeline()
            for key in keys:
                p.hgetall(key)
                p.ttl(key)
            pipeline = p.execute()

            # We loop over the effect keys to build the data
            for key in keys:
                logger.trace(f'key:{key}')
                auction = {
                    "duration_base": int(pipeline[index]['duration_base']),
                    "duration_left": int(pipeline[index + 1]),
                    "id": int(pipeline[index]['id']),
                    "meta_id": int(pipeline[index]['meta_id']),
                    "meta_name": pipeline[index]['meta_name'],
                    "price": int(pipeline[index]['price']),
                    "rarity": pipeline[index]['rarity'],
                    "seller_id": int(pipeline[index]['seller_id']),
                    "seller_name": pipeline[index]['seller_name'],
                }
                # We update the index for next iteration
                index += 2
                # We add the effect into effects list
                auctions.append(auction)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return auctions
