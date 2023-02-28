# -*- coding: utf8 -*-

import json
import uuid

from datetime                    import datetime
from loguru                      import logger

from nosql.connector             import r
from nosql.metas                 import metaNames
from nosql.variables             import str2typed, typed2str


class RedisItem:
    def __init__(self, itemuuid=None):
        self.hkey = 'items'
        self.logh = f'[Item.id:{itemuuid}]'
        fullkey = f'{self.hkey}:{itemuuid}'
        logger.trace(f'{self.logh} Method >> Initialization')

        try:
            if itemuuid:
                if r.exists(fullkey):
                    logger.trace(f'{self.logh} Method >> (HASH Loading)')
                    hashdict = r.hgetall(fullkey)

                    for k, v in hashdict.items():
                        # We create the object attribute with converted types
                        # But we skip some of them as they have @setters
                        if any([
                            k == 'ammo',
                            k == 'bearer',
                            k == 'offsetx',
                            k == 'offsety',
                        ]):
                            setattr(self, f'_{k}', str2typed(v))
                        else:
                            setattr(self, k, str2typed(v))
                    logger.trace(f'{self.logh} Method >> (HASH Loaded)')
                else:
                    logger.trace(f'{self.logh} Method KO (HASH NotFound)')
            else:
                logger.trace(f'{self.logh} Method >> Initialized Empty')
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

    def new(self, creatureuuid, item_caracs):
        try:
            self.id = str(uuid.uuid4())
            self.logh = f'[Item.id:{self.id}]'

            self._ammo = None
            self._bearer = creatureuuid
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
            for property, value in self.as_dict().items():
                hashdict[property] = typed2str(value)

            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(fullkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

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
