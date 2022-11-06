# -*- coding: utf8 -*-

from loguru                     import logger

from nosql.connector            import r


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
                    # We create the object attribute
                    if v == '':
                        newv = None
                    # INT
                    elif v.isdigit():
                        newv = int(v)
                    else:
                        newv = v
                    setattr(self, f'_{k}', newv)

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
        if self._feet == '':
            return None
        else:
            return self._feet

    @feet.setter
    def feet(self, feet):
        if feet is None:
            self._feet = ''
        else:
            self._feet = feet
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.feet')
            r.hset(self.hkey, 'feet', self._feet)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def hands(self):
        if self._hands == '':
            return None
        else:
            return self._hands

    @hands.setter
    def hands(self, hands):
        if hands is None:
            self._hands = ''
        else:
            self._hands = hands
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.hands')
            r.hset(self.hkey, 'hands', self._hands)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def head(self):
        if self._head == '':
            return None
        else:
            return self._head

    @head.setter
    def head(self, head):
        if head is None:
            self._head = ''
        else:
            self._head = head
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.head')
            r.hset(self.hkey, 'head', self._head)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def holster(self):
        if self._holster == '':
            return None
        else:
            return self._holster

    @holster.setter
    def holster(self, holster):
        if holster is None:
            self._holster = ''
        else:
            self._holster = holster
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.holster')
            r.hset(self.hkey, 'holster', self._holster)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def lefthand(self):
        if self._lefthand == '':
            return None
        else:
            return self._lefthand

    @lefthand.setter
    def lefthand(self, lefthand):
        if lefthand is None:
            self._lefthand = ''
        else:
            self._lefthand = lefthand
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.lefthand')
            r.hset(self.hkey, 'lefthand', self._lefthand)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def legs(self):
        if self._legs == '':
            return None
        else:
            return self._legs

    @legs.setter
    def legs(self, legs):
        if legs is None:
            self._legs = ''
        else:
            self._legs = legs
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.legs')
            r.hset(self.hkey, 'legs', self._legs)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def righthand(self):
        if self._righthand == '':
            return None
        else:
            return self._righthand

    @righthand.setter
    def righthand(self, righthand):
        if righthand is None:
            self._righthand = ''
        else:
            self._righthand = righthand
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Slot.righthand'
                )
            r.hset(self.hkey, 'righthand', self._righthand)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def shoulders(self):
        if self._shoulders == '':
            return None
        else:
            return self._shoulders

    @shoulders.setter
    def shoulders(self, shoulders):
        if shoulders is None:
            self._shoulders = ''
        else:
            self._shoulders = shoulders
        try:
            logger.trace(
                f'{self.logh} Method >> (Setting HASH) Slot.shoulders'
                )
            r.hset(self.hkey, 'shoulders', self._shoulders)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')

    @property
    def torso(self):
        if self._torso == '':
            return None
        else:
            return self._torso

    @torso.setter
    def torso(self, torso):
        if torso is None:
            self._torso = ''
        else:
            self._torso = torso
        try:
            logger.trace(f'{self.logh} Method >> (Setting HASH) Slot.torso')
            r.hset(self.hkey, 'torso', self._torso)
        except Exception as e:
            logger.error(f'{self.logh} Method KO [{e}]')
        else:
            logger.trace(f'{self.logh} Method OK')


if __name__ == '__main__':
    from mysql.methods.fn_creature  import fn_creature_get

    creature = fn_creature_get(None, 1)[3]
    slots = RedisSlots(creature)
    slots.holster = 198
    slots.righthand = 197
    logger.success(slots._asdict())
    logger.success(slots.righthand)
    logger.success(slots.lefthand)
