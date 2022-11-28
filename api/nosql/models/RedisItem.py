# -*- coding: utf8 -*-

import uuid

from datetime                    import datetime
from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r
from nosql.metas                 import metaNames
from nosql.variables             import str2typed, typed2str


class RedisItem:
    def __init__(self, creature=None):
        self.creature = creature
        self.hkey     = 'items'

    def destroy(self, itemuuid):
        try:
            self.item = itemuuid
            self.logh = f'[Item.id:{self.item}]'
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

    def get(self, itemuuid):
        self.logh = f'[Item.id:{itemuuid}]'
        fullkey = f'{self.hkey}:{itemuuid}'
        try:
            logger.trace(f'{self.logh} Method >> (HASH Loading)')
            if r.exists(fullkey):
                hashdict = r.hgetall(fullkey)
            else:
                logger.trace(f'{self.logh} Method KO (HASH NotFound)')
                return False

            for k, v in hashdict.items():
                # We create the object attribute with converted types
                # But we skip some of them as they have @setters
                # Note: any is like many 'or', all is like many 'and'.
                if any([
                    k == 'ammo',
                    k == 'bearer',
                    k == 'offsetx',
                    k == 'offsety',
                ]):
                    setattr(self, f'_{k}', str2typed(v))
                else:
                    setattr(self, k, str2typed(v))
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def new(self, item_caracs):
        try:
            self.id = str(uuid.uuid4())
            self.logh = f'[Item.id:{self.id}]'

            self._ammo = None
            self._bearer = self.creature.id
            self.bound = item_caracs['bound']
            self.bound_type = item_caracs['bound_type']
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.metatype = item_caracs['metatype']
            self.metaid = item_caracs['metaid']
            self.modded = item_caracs['modded']
            self.mods = item_caracs['mods']
            self.rarity = item_caracs['rarity']
            self._offsetx = None
            self._offsety = None
            self.state = item_caracs['state']

            """
            Gruik: This is done only for Alpha/Beta
            Its is needed as players can't either find/buy/craft ammo
            So we fill the weapon when we create it
            """

            if self.metatype == 'weapon':
                itemmeta = metaNames[self.metatype][self.metaid]
                # item.ammo is by default None, we initialize it here
                if itemmeta['ranged'] is True:
                    self._ammo = itemmeta['max_ammo']

            """
            # TODO: Delete the block above for poduction
            """
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (Creating dict)')
        try:
            fullkey = f'{self.hkey}:{self.id}'
            # We push data in final dict
            hashdict = {}
            # We loop over object properties to create it
            for property, value in self._asdict().items():
                hashdict[property] = typed2str(value)

            # We should have hashdict like this
            """
            hashdict = {
                "ammo": self.ammo,
                "bearer": self.bearer,
                "bound": self.bound,
                "bound_type": self.bound_type,
                "date": self.date,
                "id": self.id,
                "metatype": self.metatype,
                "metaid": self.metaid,
                "modded": self.modded,
                "mods": self.mods,
                "rarity": self.rarity,
                "offsetx": self.offsetx,
                "offsety": self.offsety,
                "state": self.state,
            }
            """
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(fullkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def search(self, field, query, maxpaging=25):
        self.logh = '[Item.id:None]'
        index = 'item_idx'
        try:
            r.ft(index).info()
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(r.ft(index).info())
            pass

        try:
            logger.trace(f'{self.logh} Method >> (Searching {field})')
            # Query("search engine").paging(0, 10)
            # f"@bearer:[{bearerid} {bearerid}]"
            results = r.ft(index).search(
                Query(
                    f"@{field}:{query}"
                    ).paging(0, maxpaging)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            # logger.trace(results)
            pass

        # If we are here, we got results
        # We loop over them to build the DICT to return
        # No more objects
        items = []
        for result in results.docs:
            item = {}
            for attr, value in result.__dict__.items():
                if attr == 'payload':
                    continue
                item[attr] = str2typed(value)

            # We need to scrape the ID value
            item['id'] = item['id'].removeprefix('items:')
            # We add the item in the items list
            items.append(item)
        logger.trace(f'{self.logh} Method OK')
        return items

    def _asdict(self):
        hashdict = {
            "ammo": self.ammo,
            "bearer": self.bearer,
            "bound": self.bound,
            "bound_type": self.bound_type,
            "date": self.date,
            "id": self.id,
            "metatype": self.metatype,
            "metaid": self.metaid,
            "modded": self.modded,
            "mods": self.mods,
            "rarity": self.rarity,
            "offsetx": self.offsetx,
            "offsety": self.offsety,
            "state": self.state,
        }
        return hashdict

    """
    Getter/Setter block for Slot management
    It is done that way to r.hset() every time API code manipulates a Slot
    And avoid to build a store() method just for that purpose
    """
    @property
    def ammo(self):
        return self._ammo

    @ammo.setter
    def ammo(self, ammo):
        self._ammo = typed2str(ammo)
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Item.ammo')
            r.hset(f'{self.hkey}:{self.id}', 'ammo', self._ammo)
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def bearer(self):
        return self._bearer

    @bearer.setter
    def bearer(self, bearer):
        self._bearer = typed2str(bearer)
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Item.bearer')
            r.hset(f'{self.hkey}:{self.id}', 'bearer', self._bearer)
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def offsetx(self):
        return self._offsetx

    @offsetx.setter
    def offsetx(self, offsetx):
        self._offsetx = typed2str(offsetx)
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Item.offsetx')
            r.hset(f'{self.hkey}:{self.id}', 'offsetx', self._offsetx)
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def offsety(self):
        return self._offsety

    @offsety.setter
    def offsety(self, offsety):
        self._offsety = typed2str(offsety)
        self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Item.offsety')
            r.hset(f'{self.hkey}:{self.id}', 'offsety', self._offsety)
            r.hset(f'{self.hkey}:{self.id}', 'date', self.date)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')


if __name__ == '__main__':
    item_caracs = {
        "metatype": 'weapon',
        "metaid": 32,
        "bound": True,
        "bound_type": 'BoP',
        "modded": False,
        "mods": None,
        "state": 100,
        "rarity": 'Common'
    }

    """
    FT.CREATE item_idx PREFIX 1 "items:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "item_score"
        SCHEMA
            bearer TEXT
            bound TEXT
            bound_type TEXT
            id TAG
            metatype TEXT
            metaid NUMERIC
            modded TEXT
            mods TEXT
            state NUMERIC
            rarity TEXT

    FT.SEARCH item_idx "Common" LIMIT 0 10

    FT.DROPINDEX item_idx
    """
