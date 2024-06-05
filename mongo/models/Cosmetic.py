# -*- coding: utf8 -*-

import datetime
import uuid

from mongoengine import (
    Document,
    EmbeddedDocument,
    )
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    EmbeddedDocumentField,
    IntField,
    # DictField,
    # ListField,
    StringField,
    UUIDField,
)

#
# Collection: cosmetic
#


class CosmeticData(EmbeddedDocument):
    """
    Define the embedded document for: Cosmetic.data

    Fields:
    - beforeArmor   (BooleanField)
    - hasGender     (BooleanField)
    - hideArmor     (BooleanField)
    """
    beforeArmor = BooleanField(required=True, default=False)
    hasGender = BooleanField(required=True, default=True)
    hideArmor = BooleanField(required=True, default=False)


class CosmeticDocument(Document):
    """
    Define the document for: Cosmetic

    Fields:
    - _id       (UUIDField)

    """
    _id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4())
    bearer = UUIDField(required=True, binary=False)
    bound = BooleanField(required=True, default=True)
    bound_type = StringField(required=True, default='BoP')
    created = DateTimeField(default=datetime.datetime.utcnow)
    data = EmbeddedDocumentField(CosmeticData, required=True)
    metaid = IntField(required=True)
    rarity = StringField(required=True, default='Common')
    state = IntField(required=True, default=100)
    updated = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'cosmetic',
        'indexes': [],
        'uuid_representation': 'pythonLegacy'
    }
