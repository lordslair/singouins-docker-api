# -*- coding: utf8 -*-

from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r

from nosql.models.RedisCd import RedisCd
from nosql.models.RedisEffect import RedisEffect
from nosql.models.RedisStatus import RedisStatus


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

        for result in self.results_raw:
            creatureuuid = self.results_raw[0].id.split(':')[1]
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            Cd = RedisCd(creatureuuid=creatureuuid, name=result.name)

            self.results.append(Cd)
            self.results_as_dict.append(Cd.as_dict())

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

        for result in self.results_raw:
            creatureuuid = self.results_raw[0].id.split(':')[1]
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            Effect = RedisEffect(creatureuuid=creatureuuid, name=result.name)

            self.results.append(Effect)
            self.results_as_dict.append(Effect.as_dict())

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
            creatureuuid = self.results_raw[0].id.split(':')[1]
            logger.trace(f'{self.logh} Method >> (Filling self.results)')
            Status = RedisStatus(creatureuuid=creatureuuid, name=result.name)

            self.results.append(Status)
            self.results_as_dict.append(Status.as_dict())

        logger.trace(f'{self.logh} Method OK')
        return self
