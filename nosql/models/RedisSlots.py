# -*- coding: utf8 -*-

import json

from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisSlots:
    def __init__(self, creatureuuid=None):
        self.hkey = 'slots'
        self.logh = f'[Slots.id:{creatureuuid}]'

        try:
            if creatureuuid:
                self.id = creatureuuid
                if r.exists(f'{self.hkey}:{self.id}'):
                    logger.trace(f'{self.logh} Method >> (HASH Loading)')
                    for k, v in r.hgetall(f'{self.hkey}:{self.id}').items():
                        setattr(self, f'_{k}', str2typed(v))
                else:
                    logger.trace(f'{self.logh} Method KO (HASH NotFound)')
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK (HASH Loaded)')

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
            "feet": self.feet,
            "hands": self.hands,
            "head": self.head,
            "holster": self.holster,
            "lefthand": self.lefthand,
            "legs": self.legs,
            "righthand": self.righthand,
            "shoulders": self.shoulders,
            "torso": self.torso,
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
            logger.trace(f'{self.logh} Method >> (HASH Destroying)')
            if r.exists(f'{self.hkey}:{self.id}'):
                r.delete(f'{self.hkey}:{self.id}')
            else:
                logger.warning(f'{self.logh} Method KO - NotFound')
                return False
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Destroyed)')
            return True

    def new(
        self,
        creatureuuid,
    ):
        try:
            self.id = creatureuuid
            self.logh = f'[Slots.id:{creatureuuid}]'

            self._feet = None
            self._hands = None
            self._head = None
            self._holster = None
            self._lefthand = None
            self._legs = None
            self._righthand = None
            self._shoulders = None
            self._torso = None
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None

        try:
            logger.trace(f'{self.logh} Method >> (Dict Creating)')
            # We push data in final dict
            hashdict = {}
            # We loop over object properties to create it
            for property, value in self.as_dict().items():
                if any([
                    property == 'logh',
                    property == 'hkey',
                ]):
                    pass
                else:
                    hashdict[property] = typed2str(value)

            logger.trace(f'{self.logh} Method >> (HASH Storing)')
            r.hset(f'{self.hkey}:{self.id}', mapping=hashdict)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK (HASH Stored)')
            return self

    """
    Getter/Setter block for Slot management
    It is done that way to r.hset() every time API code manipulates a Slot
    And avoid to build a store() method just for that purpose
    """
    @property
    def feet(self):
        return self._feet

    @feet.setter
    def feet(self, feet):
        self._feet = feet
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Slot.feet')
            r.hset(
                f'{self.hkey}:{self.id}',
                'feet',
                typed2str(self._feet),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def hands(self):
        return self._hands

    @hands.setter
    def hands(self, hands):
        self._hands = hands
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Slot.hands')
            r.hset(
                f'{self.hkey}:{self.id}',
                'hands',
                typed2str(self._hands),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def head(self):
        return self._head

    @head.setter
    def head(self, head):
        self._head = head
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Slot.head')
            r.hset(
                f'{self.hkey}:{self.id}',
                'head',
                typed2str(self._head),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def holster(self):
        return self._holster

    @holster.setter
    def holster(self, holster):
        self._holster = holster
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Slot.holster')
            r.hset(
                f'{self.hkey}:{self.id}',
                'holster',
                typed2str(self._holster),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def lefthand(self):
        return self._lefthand

    @lefthand.setter
    def lefthand(self, lefthand):
        self._lefthand = lefthand
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Slot.lefthand')
            r.hset(
                f'{self.hkey}:{self.id}',
                'lefthand',
                typed2str(self._lefthand),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def legs(self):
        return self._legs

    @legs.setter
    def legs(self, legs):
        self._legs = legs
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Slot.legs')
            r.hset(
                f'{self.hkey}:{self.id}',
                'legs',
                typed2str(self._legs),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def righthand(self):
        return self._righthand

    @righthand.setter
    def righthand(self, righthand):
        self._righthand = righthand
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Slot.righthand'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'righthand',
                typed2str(self._righthand),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def shoulders(self):
        return self._shoulders

    @shoulders.setter
    def shoulders(self, shoulders):
        self._shoulders = shoulders
        try:
            logger.trace(
                f'{self.logh} Method >> (HASH Setting) Slot.shoulders'
                )
            r.hset(
                f'{self.hkey}:{self.id}',
                'shoulders',
                typed2str(self._shoulders),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def torso(self):
        return self._torso

    @torso.setter
    def torso(self, torso):
        self._torso = torso
        try:
            logger.trace(f'{self.logh} Method >> (HASH Setting) Slot.torso')
            r.hset(
                f'{self.hkey}:{self.id}',
                'torso',
                typed2str(self._torso),
                )
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')
