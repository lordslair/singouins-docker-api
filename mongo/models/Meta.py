# -*- coding: utf8 -*-

from mongoengine import (
    DynamicDocument,
    )
from mongoengine.fields import (
    # BooleanField,
    # DateTimeField,
    DynamicField,
    # EmbeddedDocumentField,
    IntField,
    # DictField,
    # ListField,
    StringField,
    # UUIDField,
)


#
# Collection: _metaarmors
#
class MetaArmor(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {
        'collection': '_metaarmors',
        'indexes': [],
        'uuid_representation': 'standard'
        }


#
# Collection: _metaconsumables
#
class MetaConsumable(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {
        'collection': '_metaconsumables',
        'indexes': [],
        'uuid_representation': 'standard'
        }


#
# Collection: _metaraces
#
class MetaRace(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {
        'collection': '_metaraces',
        'indexes': [],
        'uuid_representation': 'standard'
        }


#
# Collection: _metarecipes
#
class MetaRecipe(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {
        'collection': '_metarecipes',
        'indexes': [],
        'uuid_representation': 'standard'
        }


#
# Collection: _metaweapons
#
class MetaWeapon(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    meta = {
        'collection': '_metaweapons',
        'indexes': [],
        'uuid_representation': 'standard'
        }


#
# Collection: _maps
#
class MetaMap(DynamicDocument):
    _id = IntField(primary_key=True, required=True)
    data = DynamicField(required=True)
    mode = StringField(required=True, default='Normal')
    size = StringField(required=True)
    type = StringField(required=True, default='Instance')

    meta = {
        'collection': '_maps',
        'indexes': [],
        'uuid_representation': 'standard'
        }
