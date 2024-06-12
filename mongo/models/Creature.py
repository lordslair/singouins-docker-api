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
# Collection: creature
#


class CreatureKorp(EmbeddedDocument):
    """
    Define the embedded document for: Creature.korp

    Fields:
    - id    (UUIDField)
    - rank  (StringField)
    """
    id = UUIDField(binary=False, default=None)
    rank = StringField(default=None)


class CreatureSquad(EmbeddedDocument):
    """
    Define the embedded document for: Creature.squad

    Fields:
    - id    (UUIDField)
    - rank  (StringField)
    """
    id = UUIDField(binary=False, default=None)
    rank = StringField(default=None)


class CreatureSlot(EmbeddedDocument):
    """
    Define the embedded document for: Creature.slots.{slot}

    Fields:
    - id       (UUIDField)
    - metaid    (IntField)
    - metatype  (StringField)
    """
    id = UUIDField(binary=False, default=None)
    metaid = IntField(default=None)
    metatype = StringField(default=None)


class CreatureSlots(EmbeddedDocument):
    """
    Define the embedded document for: Creature.slots

    Fields:
    - feet      (UUIDField)
    - hands     (UUIDField)
    - head      (UUIDField)
    - holster   (UUIDField)
    - lefthand  (UUIDField)
    - legs      (UUIDField)
    - righthand (UUIDField)
    - shoulders (UUIDField)
    - torso     (UUIDField)
    """
    feet = EmbeddedDocumentField(CreatureSlot, default=None)
    hands = EmbeddedDocumentField(CreatureSlot, default=None)
    head = EmbeddedDocumentField(CreatureSlot, default=None)
    holster = EmbeddedDocumentField(CreatureSlot, default=None)
    lefthand = EmbeddedDocumentField(CreatureSlot, default=None)
    legs = EmbeddedDocumentField(CreatureSlot, default=None)
    righthand = EmbeddedDocumentField(CreatureSlot, default=None)
    shoulders = EmbeddedDocumentField(CreatureSlot, default=None)
    torso = EmbeddedDocumentField(CreatureSlot, default=None)


class CreatureStatsType(EmbeddedDocument):
    """
    Define the embedded document for: Creature.stats

    Fields:
    - b     (IntField)
    - g     (IntField)
    - m     (IntField)
    - p     (IntField)
    - r     (IntField)
    - v     (IntField)
    """
    b = IntField(required=True, default=0)
    g = IntField(required=True, default=0)
    m = IntField(required=True, default=0)
    p = IntField(required=True, default=0)
    r = IntField(required=True, default=0)
    v = IntField(required=True, default=0)


class CreatureHP(EmbeddedDocument):
    """
    Define the embedded document for: Creature.hp

    Fields:
    - base      (IntField)
    - current   (IntField)
    - max       (IntField)
    """
    base = IntField(required=True, default=0)
    current = IntField(required=True, default=0)
    max = IntField(required=True, default=0)


class CreatureStats(EmbeddedDocument):
    race = EmbeddedDocumentField(CreatureStatsType, required=True)
    spec = EmbeddedDocumentField(CreatureStatsType, required=True)
    total = EmbeddedDocumentField(CreatureStatsType, required=True)


class CreatureDocument(Document):
    """
    Define the document for: Creature

    Fields:
    - _id       (UUIDField)
    - account   (UUIDField)
    - active    (BooleanField)
    - created   (DateTimeField)
    - discord   (EmbeddedDocumentField)
    - hash      (StringField)
    - name      (StringField)
    - updated   (DateTimeField)
    """
    _id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4())
    account = UUIDField(binary=False, default=None)
    active = BooleanField(required=True, default=False)
    created = DateTimeField(default=datetime.datetime.utcnow)
    gender = BooleanField(required=True)
    hp = EmbeddedDocumentField(CreatureHP, required=True)
    instance = UUIDField(binary=False)
    korp = EmbeddedDocumentField(CreatureKorp, required=True)
    level = IntField(required=True, default=1)
    name = StringField(required=True)
    race = IntField(required=True)
    rarity = StringField(required=True, default='Medium')
    slots = EmbeddedDocumentField(CreatureSlots, required=True)
    squad = EmbeddedDocumentField(CreatureSquad, required=True)
    stats = EmbeddedDocumentField(CreatureStats, required=True)
    targeted_by = StringField(default=None)
    updated = DateTimeField(default=datetime.datetime.utcnow)
    x = IntField(default=None)
    xp = IntField(required=True, default=0)
    y = IntField(default=None)

    meta = {
        'collection': 'creature',
        'indexes': [],
        'uuid_representation': 'pythonLegacy'
    }