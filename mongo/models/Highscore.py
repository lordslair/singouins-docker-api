import datetime

from mongoengine import (
    Document,
    EmbeddedDocument,
    )
from mongoengine.fields import (
    DateTimeField,
    EmbeddedDocumentField,
    IntField,
    # DictField,
    # ListField,
    # StringField,
    UUIDField,
)

#
# Collection: highscore
#


class HighscoreInternalGenericResource(EmbeddedDocument):
    """
    Define the embedded document for:
    - Highscore.internal.item
    - Highscore.internal.meat
    - Highscore.internal.shard
    - Highscore.internal.skin

    Fields:
    - bought    (IntField)
    - obtained  (IntField)
    - recycled  (IntField)
    - sold      (IntField)
    """
    bought = IntField(required=True, default=0)
    obtained = IntField(required=True, default=0)
    recycled = IntField(required=True, default=0)
    sold = IntField(required=True, default=0)


class HighscoreProfession(EmbeddedDocument):
    """
    Define the embedded document for: Highscore.profession

    Fields:
    - gathering (IntField)
    - mining    (IntField)
    - recycling (IntField)
    - skinning  (IntField)
    - tanning   (IntField)
    """
    gathering = IntField(required=True, default=0)
    mining = IntField(required=True, default=0)
    recycling = IntField(required=True, default=0)
    skinning = IntField(required=True, default=0)
    tanning = IntField(required=True, default=0)


class HighscoreInternal(EmbeddedDocument):
    """
    Define the embedded document for: Highscore.internal

    Fields:
    - fur       (EmbeddedDocumentField)
    - item      (EmbeddedDocumentField)
    - leather   (EmbeddedDocumentField)
    - meat      (EmbeddedDocumentField)
    - ore       (EmbeddedDocumentField)
    - shard     (EmbeddedDocumentField)
    - skin      (EmbeddedDocumentField)
    """
    fur = EmbeddedDocumentField(HighscoreInternalGenericResource, required=True)
    item = EmbeddedDocumentField(HighscoreInternalGenericResource, required=True)
    leather = EmbeddedDocumentField(HighscoreInternalGenericResource, required=True)
    meat = EmbeddedDocumentField(HighscoreInternalGenericResource, required=True)
    ore = EmbeddedDocumentField(HighscoreInternalGenericResource, required=True)
    shard = EmbeddedDocumentField(HighscoreInternalGenericResource, required=True)
    skin = EmbeddedDocumentField(HighscoreInternalGenericResource, required=True)


class HighscoreGeneral(EmbeddedDocument):
    """
    Define the embedded document for: Highscore.general

    Fields:
    - death (IntField)
    - kill  (IntField)
    """
    death = IntField(required=True, default=0)
    kill = IntField(required=True, default=0)


class HighscoreDocument(Document):
    """
    Define the document for: Highscore

    Fields:
    - _id           (UUIDField)
    - created       (DateTimeField)
    - general       (EmbeddedDocumentField)
    - internal      (EmbeddedDocumentField)
    - profession    (EmbeddedDocumentField)
    - updated       (DateTimeField)
    """
    _id = UUIDField(binary=False, primary_key=True)
    created = DateTimeField(default=datetime.datetime.utcnow)
    general = EmbeddedDocumentField(HighscoreGeneral, required=True)
    internal = EmbeddedDocumentField(HighscoreInternal, required=True)
    profession = EmbeddedDocumentField(HighscoreProfession, required=True)
    updated = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'highscores',
        'indexes': [],
        'uuid_representation': 'standard'
        }
