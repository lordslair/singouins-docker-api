# -*- coding: utf8 -*-

from mongoengine import (
    DynamicDocument,
    )
from mongoengine.fields import (
    # BooleanField,
    # DateTimeField,
    # EmbeddedDocumentField,
    IntField,
    # DictField,
    # ListField,
    # StringField,
    # UUIDField,
)


#
# Collection: meta_weapon
#
class MetaWeapon(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {'collection': 'meta_weapon'}


#
# Collection: meta_armor
#
class MetaArmor(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {'collection': 'meta_armor'}


#
# Collection: meta_race
#
class MetaRace(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {'collection': 'meta_race'}
