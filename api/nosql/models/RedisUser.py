# -*- coding: utf8 -*-

import uuid

from datetime                    import datetime
from flask_bcrypt                import generate_password_hash
from loguru                      import logger
from redis.commands.search.query import Query

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisUser:
    def __init__(self):
        self.hkey     = 'users'

    def destroy(self, username):
        try:
            self.logh = f'[User.id:{username}]'
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            useruuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))
            if r.exists(f'{self.hkey}:{useruuid}'):
                r.delete(f'{self.hkey}:{useruuid}')
            else:
                logger.trace(f'{self.logh} Method KO - NotFound')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def get(self, username):
        self.logh = f'[User.name:{username}]'
        useruuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))
        fullkey = f'{self.hkey}:{useruuid}'
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
                    k == 'active',
                    k == 'd_ack',
                    k == 'd_name',
                    k == 'hash',
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

    def new(self, username, password):
        self.logh = f'[User.id:{username}]'
        # Checking if it exists
        logger.trace(f'{self.logh} Method >> (Checking uniqueness)')
        try:
            possible_uuid = str(
                uuid.uuid3(uuid.NAMESPACE_DNS, username)
                )
            if r.exists(f'{self.hkey}:{possible_uuid}'):
                logger.error(f'{self.logh} Method KO - Already Exists')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        logger.trace(f'{self.logh} Method >> (Creating object)')
        try:
            self._active = True
            self.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._d_ack = False
            self._d_name = None
            self.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._hash = generate_password_hash(password, rounds=10)
            self.id = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))
            self.name = username
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

            logger.trace(f'{self.logh} Method >> (Storing HASH)')
            r.hset(fullkey, mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return self

    def search(self, field, query, maxpaging=25):
        self.logh = '[User.id:None]'
        index = 'user_idx'
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
        users = []
        for result in results.docs:
            user = {
                "active": str2typed(result.active),
                "created": result.created,
                "d_ack": str2typed(result.d_ack),
                "d_name": result.d_name,
                "date": result.date,
                "hash": result.hash,
                "id": result.id.removeprefix('users:'),
                "name": result.name,
                }
            users.append(user)

        logger.trace(f'{self.logh} Method OK')
        return users

    def _asdict(self):
        hashdict = {
            "active": self.active,
            "created": self.created,
            "d_ack": self.d_ack,
            "d_name": self.d_name,
            "date": self.date,
            "hash": self.hash,
            "id": self.id,
            "name": self.name
        }
        return hashdict

    """
    Getter/Setter block for User management
    It is done that way to r.hset() every time API code manipulates a User
    And avoid to build a store() method just for that purpose
    """
    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) User.active')
            r.hset(
                f'{self.hkey}:{self.id}',
                'active',
                typed2str(self._active)
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'date',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def d_name(self):
        return self._d_name

    @d_name.setter
    def d_name(self, d_name):
        self._d_name = d_name
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) User.d_name')
            r.hset(
                f'{self.hkey}:{self.id}',
                'd_name',
                typed2str(self._d_name)
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'date',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def d_ack(self):
        return self._d_ack

    @d_ack.setter
    def d_ack(self, d_ack):
        self._d_ack = d_ack
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) User.d_ack')
            r.hset(
                f'{self.hkey}:{self.id}',
                'd_ack',
                typed2str(self._d_ack)
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'date',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def hash(self):
        return self._hash

    @hash.setter
    def hash(self, hash):
        self._hash = hash
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) User.hash')
            r.hset(
                f'{self.hkey}:{self.id}',
                'hash',
                typed2str(self._hash)
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'date',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')


if __name__ == '__main__':
    """
    FT.CREATE user_idx PREFIX 1 "users:"
        LANGUAGE english
        SCORE 0.5
        SCORE_FIELD "user_score"
        SCHEMA
            active TEXT
            d_ack TEXT
            d_name TEXT
            id TEXT
            TAG TEXT

    FT.SEARCH user_idx "Lordslair" LIMIT 0 10

    FT.DROPINDEX user_idx
    """
