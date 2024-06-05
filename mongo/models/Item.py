# -*- coding: utf8 -*-

import datetime
import uuid

from mongoengine import (
    Document,
    # EmbeddedDocument,
    )
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    # EmbeddedDocumentField,
    IntField,
    # DictField,
    ListField,
    StringField,
    UUIDField,
)

#
# Collection: item
#


class ItemDocument(Document):
    """
    Define the document for: Creature

    Fields:
    - _id       (UUIDField)

    """
    _id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4())
    ammo = IntField(default=None)
    auctioned = BooleanField(required=True, default=False)
    bearer = UUIDField(required=True, binary=False)
    bound = BooleanField(required=True, default=True)
    bound_type = StringField(required=True, default='BoP')
    created = DateTimeField(default=datetime.datetime.utcnow)
    metatype = StringField(required=True)
    metaid = IntField(required=True)
    modded = BooleanField(required=True, default=False)
    mods = ListField(default=[])
    offsetx = IntField(default=None)
    offsety = IntField(default=None)
    rarity = StringField(required=True, default='Common')
    state = IntField(required=True, default=100)
    updated = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'item',
        'indexes': [],
        'uuid_representation': 'pythonLegacy'
    }
