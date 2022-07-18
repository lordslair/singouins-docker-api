# -*- coding: utf8 -*-

from nosql.connector            import *

class RedisWallet:
    def __init__(self,creature):
        self.hkey     = f'wallet:{creature.id}'
        self.logh     = f'[creature.id:{creature.id}]'

        if r.exists(self.hkey):
            # The Wallet does already exist in Redis
            try:
                hash = r.hgetall(self.hkey)
                logger.trace(f'{self.logh} Method >> (Loading HASH)')

                self.cal22     = int(hash['cal22'])
                self.cal223    = int(hash['cal223'])
                self.cal311    = int(hash['cal311'])
                self.cal50     = int(hash['cal50'])
                self.cal55     = int(hash['cal55'])
                self.shell     = int(hash['shell'])
                self.bolt      = int(hash['bolt'])
                self.arrow     = int(hash['arrow'])

                self.legendary = int(hash['legendary'])
                self.epic      = int(hash['epic'])
                self.rare      = int(hash['rare'])
                self.uncommon  = int(hash['uncommon'])
                self.common    = int(hash['common'])
                self.broken    = int(hash['broken'])

                self.bananas   = int(hash['bananas'])
                self.sausages  = int(hash['sausages'])

                logger.trace(f'{self.logh} Method >> (Creating dict)')
                self.dict = {
                                "ammo":
                                        {
                                            "cal22":  self.cal22,
                                            "cal223": self.cal223,
                                            "cal311": self.cal311,
                                            "cal50":  self.cal50,
                                            "cal55":  self.cal55,
                                            "shell":  self.shell,
                                            "bolt":   self.bolt,
                                            "arrow":  self.arrow
                                        },
                                "currency":
                                        {
                                            "bananas": self.bananas,
                                            "sausages": self.sausages
                                        },
                                "shards":
                                        {
                                            "broken":    self.broken,
                                            "common":    self.common,
                                            "uncommon":  self.uncommon,
                                            "rare":      self.rare,
                                            "epic":      self.epic,
                                            "legendary": self.legendary
                                        }
                                  }
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')

    def init(self):
        try:
            # We push data in final dict
            logger.trace(f'{self.logh} Method >> (Creating dict)')
            hashdict =  {
                            "cal22":     0,
                            "cal223":    0,
                            "cal311":    0,
                            "cal50":     0,
                            "cal55":     0,
                            "shell":     0,
                            "bolt":      0,
                            "arrow":     0,
                            "legendary": 0,
                            "epic":      0,
                            "rare":      0,
                            "uncommon":  0,
                            "common":    0,
                            "broken":    0,
                            "bananas":   0,
                            "sausages":  0
                        }
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            logger.trace(f'self.hkey:{self.hkey}')
            r.hset(self.hkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def store(self):
        try:
            # We push data in final dict
            logger.trace(f'{self.logh} Method >> (Creating dict)')
            hashdict =  {
                            "cal22":     self.cal22,
                            "cal223":    self.cal223,
                            "cal311":    self.cal311,
                            "cal50":     self.cal50,
                            "cal55":     self.cal55,
                            "shell":     self.shell,
                            "bolt":      self.bolt,
                            "arrow":     self.arrow,
                            "legendary": self.legendary,
                            "epic":      self.epic,
                            "rare":      self.rare,
                            "uncommon":  self.uncommon,
                            "common":    self.common,
                            "broken":    self.broken,
                            "bananas":   self.bananas,
                            "sausages":  self.sausages
                        }
            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            logger.trace(f'self.hkey:{self.hkey}')
            r.hset(self.hkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def refresh(self):
        if r.exists(self.hkey):
            # The Wallet does already exist in Redis
            try:
                hash = r.hgetall(self.hkey)
                logger.trace(f'{self.logh} Method >> (HASH Loading)')

                self.cal22     = int(hash['cal22'])
                self.cal223    = int(hash['cal223'])
                self.cal311    = int(hash['cal311'])
                self.cal50     = int(hash['cal50'])
                self.cal55     = int(hash['cal55'])
                self.shell     = int(hash['shell'])
                self.bolt      = int(hash['bolt'])
                self.arrow     = int(hash['arrow'])

                self.legendary = int(hash['legendary'])
                self.epic      = int(hash['epic'])
                self.rare      = int(hash['rare'])
                self.uncommon  = int(hash['uncommon'])
                self.common    = int(hash['common'])
                self.broken    = int(hash['broken'])

                self.bananas   = int(hash['bananas'])
                self.sausages  = int(hash['sausages'])

                self.dict = {
                                "ammo":
                                        {
                                            "cal22":  self.cal22,
                                            "cal223": self.cal223,
                                            "cal311": self.cal311,
                                            "cal50":  self.cal50,
                                            "cal55":  self.cal55,
                                            "shell":  self.shell,
                                            "bolt":   self.bolt,
                                            "arrow":  self.arrow
                                        },
                                "currency":
                                        {
                                            "bananas": self.bananas,
                                            "sausages": self.sausages
                                        },
                                "shards":
                                        {
                                            "broken":    self.broken,
                                            "common":    self.common,
                                            "uncommon":  self.uncommon,
                                            "rare":      self.rare,
                                            "epic":      self.epic,
                                            "legendary": self.legendary
                                        }
                                  }

                logger.trace(f'{self.logh} Method >> (HASH Loaded)')
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK')
        else:
            # Wallet not found, we create the object but that's not normal
            logger.error(f'{self.logh} Method KO - Non existing Wallet')
            return None

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

if __name__ == '__main__':
    from mysql.methods.fn_creature  import fn_creature_get

    creature    = fn_creature_get(None,1)[3]
    creature_wallet = RedisWallet(creature)
    logger.info(creature_wallet.dict)

    creature_wallet.arrow = 666

    # This returns True if the HASH is properly stored in Redis
    stored_status = creature_wallet.store()
    logger.info(stored_status)

    #del_status = creature_wallet.destroy()
    #logger.info(del_status)
