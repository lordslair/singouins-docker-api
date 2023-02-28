# -*- coding: utf8 -*-

import json

from loguru                     import logger

from nosql.connector            import r


class RedisWallet:
    def __init__(self, creatureuuid=None):
        self.hkey = 'wallets'
        self.logh = f'[Creature.id:{creatureuuid}]'
        self.id = creatureuuid
        logger.trace(f'{self.logh} Method >> Initialization')

        if creatureuuid:
            if r.exists(f'{self.hkey}:{self.id}'):
                logger.trace(f'{self.logh} Method >> (HASH Loading)')
                try:
                    for k, v in r.hgetall(f'{self.hkey}:{self.id}').items():
                        # We create the object attribute with converted INT
                        setattr(self, f'_{k}', int(v))
                    logger.trace(f'{self.logh} Method >> (HASH Loaded)')
                except Exception as e:
                    logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method KO (HASH NotFound)')

    def __iter__(self):
        yield from {
            "cal22": self.cal22,
            "cal223": self.cal223,
            "cal311": self.cal311,
            "cal50": self.cal50,
            "cal55": self.cal55,
            "shell": self.shell,
            "bolt": self.bolt,
            "arrow": self.arrow,
            "legendary": self.legendary,
            "epic": self.epic,
            "rare": self.rare,
            "uncommon": self.uncommon,
            "common": self.common,
            "broken": self.broken,
            "bananas": self.bananas,
            "sausages": self.sausages,
        }.items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def to_json(self):
        """
        Converts RedisWallet object into a JSON

        Parameters: None

        Returns: str()
        """
        return self.__str__()

    def as_dict(self):
        """
        Converts RedisWallet object into a Python dict

        Parameters: None

        Returns: dict()
        """
        return {
            "ammo":
                {
                    "cal22": self.cal22,
                    "cal223": self.cal223,
                    "cal311": self.cal311,
                    "cal50": self.cal50,
                    "cal55": self.cal55,
                    "shell": self.shell,
                    "bolt": self.bolt,
                    "arrow": self.arrow,
                },
            "currency":
                {
                    "bananas": self.bananas,
                    "sausages": self.sausages,
                },
            "shards":
                {
                    "broken": self.broken,
                    "common": self.common,
                    "uncommon": self.uncommon,
                    "rare": self.rare,
                    "epic": self.epic,
                    "legendary": self.legendary,
                }
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

    def new(self):
        """
        Creates a new Wallet and stores it into Redis DB.

        Parameters: None

        Returns: RedisWallet object
        """
        if self.id is None:
            logger.warning(f'{self.logh} Method KO - Creature.id NotFound')
            return None

        self.logh = f'[Wallet.id:{self.id}]'
        try:
            if r.exists(f'{self.hkey}:{self.id}'):
                logger.error(f'{self.logh} Method KO - Already Exists')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        self._cal22 = 0
        self._cal223 = 0
        self._cal311 = 0
        self._cal50 = 0
        self._cal55 = 0
        self._shell = 0
        self._bolt = 0
        self._arrow = 0
        self._legendary = 0
        self._epic = 0
        self._rare = 0
        self._uncommon = 0
        self._common = 0
        self._broken = 0
        self._sausages = 0
        self._bananas = 0

        logger.trace(f'{self.logh} Method >> (Dict Creating)')
        try:
            hashdict = {
                "cal22": self.cal22,
                "cal223": self.cal223,
                "cal311": self.cal311,
                "cal50": self.cal50,
                "cal55": self.cal55,
                "shell": self.shell,
                "bolt": self.bolt,
                "arrow": self.arrow,
                "bananas": self.bananas,
                "sausages": self.sausages,
                "broken": self.broken,
                "common": self.common,
                "uncommon": self.uncommon,
                "rare": self.rare,
                "epic": self.epic,
                "legendary": self.legendary,
                }
            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(f'{self.hkey}:{self.id}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self

    """
    Getter/Setter block for Wallet management
    It is done that way to r.hset() every time API code manipulates a Wallet
    And avoid to build a store() method just for that purpose
    """
    @property
    def bananas(self):
        return self._bananas

    @bananas.setter
    def bananas(self, bananas):
        self._bananas = bananas
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.bananas'
                )
            r.hset(f'{self.hkey}:{self.id}', 'bananas', self._bananas)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def sausages(self):
        return self._sausages

    @sausages.setter
    def sausages(self, sausages):
        self._sausages = sausages
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.sausages'
                )
            r.hset(f'{self.hkey}:{self.id}', 'sausages', self._sausages)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def broken(self):
        return self._broken

    @broken.setter
    def broken(self, broken):
        self._broken = broken
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.broken'
                )
            r.hset(f'{self.hkey}:{self.id}', 'broken', self._broken)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def common(self):
        return self._common

    @common.setter
    def common(self, common):
        self._common = common
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.common'
                )
            r.hset(f'{self.hkey}:{self.id}', 'common', self._common)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def uncommon(self):
        return self._uncommon

    @uncommon.setter
    def uncommon(self, uncommon):
        self._uncommon = uncommon
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.uncommon'
                )
            r.hset(f'{self.hkey}:{self.id}', 'uncommon', self._uncommon)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

            @property
            def uncommon(self):
                return self._uncommon

    @property
    def rare(self):
        return self._rare

    @rare.setter
    def rare(self, rare):
        self._rare = rare
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.rare'
                )
            r.hset(f'{self.hkey}:{self.id}', 'rare', self._rare)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def epic(self):
        return self._epic

    @epic.setter
    def epic(self, epic):
        self._epic = epic
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.epic'
                )
            r.hset(f'{self.hkey}:{self.id}', 'epic', self._epic)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def legendary(self):
        return self._legendary

    @legendary.setter
    def legendary(self, legendary):
        self._legendary = legendary
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.legendary'
                )
            r.hset(f'{self.hkey}:{self.id}', 'legendary', self._legendary)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def cal22(self):
        return self._cal22

    @cal22.setter
    def cal22(self, cal22):
        self._cal22 = cal22
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.cal22'
                )
            r.hset(f'{self.hkey}:{self.id}', 'cal22', self._cal22)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def cal223(self):
        return self._cal223

    @cal223.setter
    def cal223(self, cal223):
        self._cal223 = cal223
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.cal223'
                )
            r.hset(f'{self.hkey}:{self.id}', 'cal223', self._cal223)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def cal311(self):
        return self._cal311

    @cal311.setter
    def cal311(self, cal311):
        self._cal311 = cal311
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.cal311'
                )
            r.hset(f'{self.hkey}:{self.id}', 'cal311', self._cal311)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def cal50(self):
        return self._cal50

    @cal50.setter
    def cal50(self, cal50):
        self._cal50 = cal50
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.cal50'
                )
            r.hset(f'{self.hkey}:{self.id}', 'cal50', self._cal50)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def cal55(self):
        return self._cal55

    @cal55.setter
    def cal55(self, cal55):
        self._cal55 = cal55
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.cal55'
                )
            r.hset(f'{self.hkey}:{self.id}', 'cal55', self._cal55)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def shell(self):
        return self._shell

    @shell.setter
    def shell(self, shell):
        self._shell = shell
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.shell'
                )
            r.hset(f'{self.hkey}:{self.id}', 'shell', self._shell)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def bolt(self):
        return self._bolt

    @bolt.setter
    def bolt(self, bolt):
        self._bolt = bolt
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.bolt'
                )
            r.hset(f'{self.hkey}:{self.id}', 'bolt', self._bolt)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')

    @property
    def arrow(self):
        return self._arrow

    @arrow.setter
    def arrow(self, arrow):
        self._arrow = arrow
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Wallet.arrow'
                )
            r.hset(f'{self.hkey}:{self.id}', 'arrow', self._arrow)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Set)')
