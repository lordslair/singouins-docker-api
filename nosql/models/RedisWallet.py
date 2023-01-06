# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector            import r


class RedisWallet:
    def __init__(self, creature):
        self.creature = creature
        self.hkey     = f'wallet:{creature.id}'
        self.logh     = f'[Creature.id:{self.creature.id}]'
        logger.trace(f'{self.logh} Method >> Initialization')

        if r.exists(self.hkey):
            # The pre-generated stats does already exist in redis
            try:
                hashdict = r.hgetall(self.hkey)
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                for k, v in hashdict.items():
                    # We create the object attribute with converted INT
                    setattr(self, f'_{k}', int(v))

                logger.trace(f'{self.logh} Method >> (HASH Loaded)')
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')
        else:
            # The pre-generated stats does not already exist in redis
            logger.trace(f'{self.logh} Method >> (HASH Creating)')
            try:
                hashdict = {
                    "cal22": 0,
                    "cal223": 0,
                    "cal311": 0,
                    "cal50": 0,
                    "cal55": 0,
                    "shell": 0,
                    "bolt": 0,
                    "arrow": 0,
                    "legendary": 0,
                    "epic": 0,
                    "rare": 0,
                    "uncommon": 0,
                    "common": 0,
                    "broken": 0,
                    "bananas": 0,
                    "sausages": 0,
                }
                for k, v in hashdict.items():
                    setattr(self, f'_{k}', v)
                r.hset(self.hkey, mapping=hashdict)
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')

    def destroy(self):
        try:
            if r.exists(self.hkey):
                logger.trace(f'{self.logh} Method >> (Destroying HASH)')
                r.delete(self.hkey)
            else:
                logger.warning(f'{self.logh} Method >> (HASH not found)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def _asdict(self):
        hashdict = {
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
        return hashdict

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
                f'{self.logh} Method >> (Setting HASH) Wallet.bananas'
                )
            r.hset(f'{self.hkey}', 'bananas', self._bananas)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def sausages(self):
        return self._sausages

    @sausages.setter
    def sausages(self, sausages):
        self._sausages = sausages
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.sausages'
                )
            r.hset(f'{self.hkey}', 'sausages', self._sausages)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def broken(self):
        return self._broken

    @broken.setter
    def broken(self, broken):
        self._broken = broken
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.broken'
                )
            r.hset(f'{self.hkey}', 'broken', self._broken)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def common(self):
        return self._common

    @common.setter
    def common(self, common):
        self._common = common
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.common'
                )
            r.hset(f'{self.hkey}', 'common', self._common)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def uncommon(self):
        return self._uncommon

    @uncommon.setter
    def uncommon(self, uncommon):
        self._uncommon = uncommon
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.uncommon'
                )
            r.hset(f'{self.hkey}', 'uncommon', self._uncommon)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

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
                f'{self.logh} Method >> (Setting HASH) Wallet.rare'
                )
            r.hset(f'{self.hkey}', 'rare', self._rare)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def epic(self):
        return self._epic

    @epic.setter
    def epic(self, epic):
        self._epic = epic
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.epic'
                )
            r.hset(f'{self.hkey}', 'epic', self._epic)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def legendary(self):
        return self._legendary

    @legendary.setter
    def legendary(self, legendary):
        self._legendary = legendary
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.legendary'
                )
            r.hset(f'{self.hkey}', 'legendary', self._legendary)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def cal22(self):
        return self._cal22

    @cal22.setter
    def cal22(self, cal22):
        self._cal22 = cal22
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.cal22'
                )
            r.hset(f'{self.hkey}', 'cal22', self._cal22)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def cal223(self):
        return self._cal223

    @cal223.setter
    def cal223(self, cal223):
        self._cal223 = cal223
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.cal223'
                )
            r.hset(f'{self.hkey}', 'cal223', self._cal223)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def cal311(self):
        return self._cal311

    @cal311.setter
    def cal311(self, cal311):
        self._cal311 = cal311
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.cal311'
                )
            r.hset(f'{self.hkey}', 'cal311', self._cal311)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def cal50(self):
        return self._cal50

    @cal50.setter
    def cal50(self, cal50):
        self._cal50 = cal50
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.cal50'
                )
            r.hset(f'{self.hkey}', 'cal50', self._cal50)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def cal55(self):
        return self._cal55

    @cal55.setter
    def cal55(self, cal55):
        self._cal55 = cal55
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.cal55'
                )
            r.hset(f'{self.hkey}', 'cal55', self._cal55)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def shell(self):
        return self._shell

    @shell.setter
    def shell(self, shell):
        self._shell = shell
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.shell'
                )
            r.hset(f'{self.hkey}', 'shell', self._shell)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def bolt(self):
        return self._bolt

    @bolt.setter
    def bolt(self, bolt):
        self._bolt = bolt
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.bolt'
                )
            r.hset(f'{self.hkey}', 'bolt', self._bolt)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def arrow(self):
        return self._arrow

    @arrow.setter
    def arrow(self, arrow):
        self._arrow = arrow
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Wallet.arrow'
                )
            r.hset(f'{self.hkey}', 'arrow', self._arrow)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')
