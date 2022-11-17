# -*- coding: utf8 -*-

from loguru                      import logger

from nosql.connector             import r
from nosql.variables             import str2typed, typed2str


class RedisSlots:
    def __init__(self, creature):
        self.creature = creature
        self.hkey     = f'slots:{creature.id}'
        self.logh     = f'[Creature.id:{self.creature.id}]'
        self.refresh()

    def destroy(self):
        try:
            logger.trace(f'{self.logh} Method >> (Destroying HASH)')
            r.delete(self.hkey)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
            return None
        else:
            logger.trace(f'{self.logh} Method OK')
            return True

    def refresh(self):
        if r.exists(self.hkey):
            try:
                logger.trace(f'{self.logh} Method >> (KEY Loading)')
                hashdict = r.hgetall(self.hkey)

                for k, v in hashdict.items():
                    setattr(self, f'_{k}', str2typed(v))

                logger.trace(f'{self.logh} Method >> (KEY Loaded)')
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
                return None
            else:
                logger.trace(f'{self.logh} Method OK')
                return True
        else:
            try:
                logger.trace(f'{self.logh} Method >> Initialization')
                self.feet      = None
                self.hands     = None
                self.head      = None
                self.holster   = None
                self.lefthand  = None
                self.legs      = None
                self.righthand = None
                self.shoulders = None
                self.torso     = None
            except Exception as e:
                logger.error(f'{self.logh} Method KO [{e}]')
                return None
            else:
                logger.trace(f'{self.logh} Method OK')
                return True

    def _asdict(self):
        hashdict = {
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
        return hashdict

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
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.feet')
            r.hset(self.hkey, 'feet', typed2str(self._feet))
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
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.hands')
            r.hset(self.hkey, 'hands', typed2str(self._hands))
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
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.head')
            r.hset(self.hkey, 'head', typed2str(self._head))
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
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.holster')
            r.hset(self.hkey, 'holster', typed2str(self._holster))
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
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.lefthand')
            r.hset(self.hkey, 'lefthand', typed2str(self._lefthand))
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
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.legs')
            r.hset(self.hkey, 'legs', typed2str(self._legs))
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
                f'{self.logh} Method >> (Setting HASH) Slot.righthand'
                )
            r.hset(self.hkey, 'righthand', typed2str(self._righthand))
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
                f'{self.logh} Method >> (Setting HASH) Slot.shoulders'
                )
            r.hset(self.hkey, 'shoulders', typed2str(self._shoulders))
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
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.torso')
            r.hset(self.hkey, 'torso', typed2str(self._torso))
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')


if __name__ == '__main__':
    pass
