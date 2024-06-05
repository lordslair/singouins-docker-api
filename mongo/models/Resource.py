# -*- coding: utf8 -*-

import datetime
import uuid

from mongoengine import (
    Document,
    )
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    # DynamicField,
    # EmbeddedDocumentField,
    IntField,
    # DictField,
    # ListField,
    StringField,
    UUIDField,
)

#
# Collection: event
#


class EventDocument(Document):
    """
    Define the document for: Resource

    Fields:
    - _id       (UUIDField)
    - created   (DateTimeField)
    - instance  (UUIDField)
    - material  (StringField)
    - rarity    (StringField)
    - sprite    (StringField)
    - updated   (DateTimeField)
    - visible   (BooleanField)
    - x         (IntField)
    - y         (IntField)
    """
    _id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4())
    created = DateTimeField(default=datetime.datetime.utcnow)
    instance = UUIDField(binary=False, default=None)
    material = StringField(required=True)
    rarity = StringField(required=True, default='Common')
    sprite = StringField(required=True)
    updated = DateTimeField(default=datetime.datetime.utcnow)
    visible = BooleanField(required=True, default=False)
    x = IntField(required=True)
    y = IntField(required=True)

    meta = {
        'collection': 'resource',
        'indexes': [],
        'uuid_representation': 'pythonLegacy'
    }
