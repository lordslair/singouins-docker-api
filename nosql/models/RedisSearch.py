# -*- coding: utf8 -*-

from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r

from nosql.models.RedisAuction import RedisAuction
from nosql.models.RedisCd import RedisCd
from nosql.models.RedisCosmetic import RedisCosmetic
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisEffect import RedisEffect
from nosql.models.RedisEvent import RedisEvent
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisItem import RedisItem
from nosql.models.RedisKorp import RedisKorp
from nosql.models.RedisSquad import RedisSquad
from nosql.models.RedisStatus import RedisStatus
from nosql.models.RedisUser import RedisUser


class RedisSearch:
    """
    Search for KEYS in Redis DB using RediSearch.

    Parameters:
    maxpaging (int): Limits the number of returned results [Default:25]

    Returns: list()
    """
    def __init__(self, maxpaging=25):
        logger.trace('[Index:None] Method >> Initialization')
        self.maxpaging = maxpaging
        self.results = []
        self.results_as_dict = []

    def search(self, index, query):
        """
        Search for XXX in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(Document)
        """
        logger.trace(f'{self.logh} Method >> Search')

        try:
            r.ft(index).info()
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        try:
            logger.trace(f'{self.logh} Method >> (Searching {query})')
            results = r.ft(index).search(
                Query(query).paging(0, self.maxpaging)
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        return results.docs

    def auction(self, query):
        """
        Search for Auctions in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisAuction)
        """
        index = 'auction_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            auctionuuid = result.id.removeprefix('auctions:')

            Auction = RedisAuction(auctionuuid=auctionuuid)

            self.results.append(Auction)
            self.results_as_dict.append(Auction.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def cd(self, query):
        """
        Search for Cds in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisCd)
        """
        index = 'cd_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            creatureuuid = result.id.removeprefix('cds:')
            creatureuuid = creatureuuid.removesuffix(f':{result.name}')

            Cd = RedisCd(creatureuuid=creatureuuid, name=result.name)

            self.results.append(Cd)
            self.results_as_dict.append(Cd.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def cosmetic(self, query):
        """
        Search for Cosmetics in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisCosmetic)
        """
        index = 'cosmetic_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            cosmeticuuid = result.id.removeprefix('cosmetics:')

            Cosmetic = RedisCosmetic(cosmeticuuid=cosmeticuuid)

            self.results.append(Cosmetic)
            self.results_as_dict.append(Cosmetic.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def creature(self, query):
        """
        Search for Creatures in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisCreature)
        """
        index = 'creature_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            creatureuuid = result.id.removeprefix('creatures:')

            Creature = RedisCreature(creatureuuid=creatureuuid)

            self.results.append(Creature)
            self.results_as_dict.append(Creature.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def event(self, query):
        """
        Search for Events in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisEvent)
        """
        index = 'event_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            eventuuid = result.id.removeprefix('events:')

            Event = RedisEvent(eventuuid=eventuuid)

            self.results.append(Event)
            self.results_as_dict.append(Event.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def effect(self, query):
        """
        Search for Effects in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisEffect)
        """
        index = 'effect_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            creatureuuid = result.id.removeprefix('effects:')
            creatureuuid = creatureuuid.removesuffix(f':{result.name}')

            Effect = RedisEffect(creatureuuid=creatureuuid, name=result.name)

            self.results.append(Effect)
            self.results_as_dict.append(Effect.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def instance(self, query):
        """
        Search for Instances in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisInstance)
        """
        index = 'instance_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            instanceuuid = result.id.removeprefix('instances:')

            Instance = RedisInstance(instanceuuid=instanceuuid)

            self.results.append(Instance)
            self.results_as_dict.append(Instance.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def item(self, query):
        """
        Search for Items in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisItem)
        """
        index = 'item_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            itemuuid = result.id.removeprefix('items:')

            Items = RedisItem(itemuuid=itemuuid)

            self.results.append(Items)
            self.results_as_dict.append(Items.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def korp(self, query):
        """
        Search for Korps in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisKorp)
        """
        index = 'korp_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            korpuuid = result.id.removeprefix('korps:')

            Korp = RedisKorp(korpuuid=korpuuid)

            self.results.append(Korp)
            self.results_as_dict.append(Korp.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def squad(self, query):
        """
        Search for Squad in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisSquad)
        """
        index = 'squad_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            squaduuid = result.id.removeprefix('squads:')

            Squad = RedisSquad(squaduuid=squaduuid)

            self.results.append(Squad)
            self.results_as_dict.append(Squad.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def status(self, query):
        """
        Search for Effects in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisStatus)
        """
        index = 'status_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            creatureuuid = result.id.removeprefix('statuses:')
            creatureuuid = creatureuuid.removesuffix(f':{result.name}')

            Status = RedisStatus(creatureuuid=creatureuuid, name=result.name)

            self.results.append(Status)
            self.results_as_dict.append(Status.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self

    def user(self, query):
        """
        Search for Users in Redis DB using RediSearch.

        Parameters:
        query (str): Redisearch raw query

        Returns: list(RedisUser)
        """
        index = 'user_idx'
        self.logh = f'[Index:{index}]'
        self.results_raw = self.search(index=index, query=query)

        # If we are here, we got results
        for result in self.results_raw:
            logger.trace(f'{self.logh} Method >> (Filling self.results)')

            User = RedisUser(username=result.name)

            self.results.append(User)
            self.results_as_dict.append(User.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self
