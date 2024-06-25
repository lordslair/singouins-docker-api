# -*- coding: utf8 -*-

import json

from loguru import logger

from nosql.connector import r

# Constants
PA_DURATION = 3600

RED_PA_MAX = 16
RED_MAX_TTL = PA_DURATION * RED_PA_MAX

BLUE_PA_MAX = 8
BLUE_MAX_TTL = PA_DURATION * BLUE_PA_MAX


class RedisPa:
    def __init__(self, creatureuuid):
        """
        Initialize RedisPa instance.

        Parameters:
        creature_uuid (str): UUID of the creature.
        """
        self.hkey = 'pa'
        self.logh = f'[Creature.id:{creatureuuid}]'
        self.id = creatureuuid

        if creatureuuid:
            logger.trace(f'{self.logh} Method >> Initialization')
            self.redttl, self.redpa, self.redttnpa = self._load_pa('red', RED_PA_MAX, RED_MAX_TTL)  # noqa E501
            self.bluettl, self.bluepa, self.bluettnpa = self._load_pa('blue', BLUE_PA_MAX, BLUE_MAX_TTL)  # noqa E501

    def __iter__(self):
        yield from self.as_dict().items()

    def __str__(self):
        return json.dumps(dict(self), ensure_ascii=False)

    def __repr__(self):
        return self.__str__()

    def _load_pa(self, color, pa_max, max_ttl, duration=PA_DURATION):
        """
        Load PA values from Redis.

        Parameters:
        color (str): Color key (red/blue).
        max_ttl (int): Maximum TTL.
        duration (int): Duration per PA.
        pa_max (int): Maximum PA count.

        Returns:
        tuple: ttl, pa, ttnpa
        """
        key = f'{self.hkey}:{self.id}:{color}'
        if r.exists(key):
            logger.trace(f'{self.logh} Method >> (HASH Loading) {color.upper()}')
            try:
                ttl = r.ttl(key)
                pa_temp = max_ttl - abs(ttl)
                pa = int(round(pa_temp / duration))
                ttnpa = ttl % duration
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
            else:
                logger.trace(f'{self.logh} Method OK (HASH Loaded) {color.upper()}:{pa}')
                return ttl, pa, ttnpa
        return 0, pa_max, duration

    def _update_pa(self, color, pa, pa_max, duration=PA_DURATION):
        """
        Update PA values in Redis.

        Parameters:
        color (str): Color key (red/blue).
        pa (int): Number of PAs to consume.
        duration (int): Duration per PA.
        pa_max (int): Maximum PA count.
        """
        key = f'{self.hkey}:{self.id}:{color}'
        ttl = r.ttl(key)
        new_ttl = ttl + (pa * duration)

        if new_ttl < duration * pa_max:
            # Update the object
            setattr(self, f'{color}pa', pa)
            setattr(self, f'{color}ttl', new_ttl)
            setattr(self, f'{color}ttnpa', self.bluettl % duration)

            if ttl > 0:
                # Key still exists (PA count < PA max)
                r.expire(key, new_ttl)
            else:
                # Key does not exist anymore (PA count = PA max)
                r.set(key, 'None', ex=new_ttl)

    def to_json(self):
        """
        Converts Object into a JSON.

        Returns:
        str: JSON representation of the object.
        """
        return self.__str__()

    def as_dict(self):
        """
        Converts Object into a Python dict.

        Returns:
        dict: Dictionary representation of the object.
        """
        return {
            "blue": {
                "pa": self.bluepa,
                "ttnpa": self.bluettnpa,
                "ttl": self.bluettl,
            },
            "red": {
                "pa": self.redpa,
                "ttnpa": self.redttnpa,
                "ttl": self.redttl,
            },
        }

    def destroy(self):
        """
        Destroys an Object and DEL it from Redis DB.

        Returns:
        bool: True if successfully destroyed, False otherwise.
        """
        if not hasattr(self, 'id') or self.id is None:
            logger.warning(f'{self.logh} Method KO - ID NotSet or NotFound')
            return False

        try:
            logger.trace(f'{self.logh} Method >> (HASH Destroying)')
            for color in ['blue', 'red']:
                r.delete(f'{self.hkey}:{self.id}:{color}')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return False
        else:
            logger.trace(f'{self.logh} Method >> (HASH Destroyed)')
            return True

    def consume(self, redpa=0, bluepa=0):
        """
        Consume PAs and update Redis.

        Parameters:
        redpa (int): Number of red PAs to consume.
        bluepa (int): Number of blue PAs to consume.

        Returns:
        bool: True if successfully updated, None if an error occurred.
        """
        try:
            if bluepa > 0:
                self._update_pa('blue', bluepa, BLUE_PA_MAX)
            if redpa > 0:
                self._update_pa('red', redpa, RED_PA_MAX)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (KEY Updated)')
            return True
