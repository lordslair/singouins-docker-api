import datetime
import uuid

from mongoengine import (
    Document,
    )
from mongoengine.fields import (
    # BooleanField,
    DateTimeField,
    # EmbeddedDocumentField,
    IntField,
    # DictField,
    # ListField,
    # StringField,
    UUIDField,
)

#
# Collection: profession
#


class ProfessionDocument(Document):
    """
    Define the document for: Profession

    Fields:
    - _id       (UUIDField)
    - recycling (IntField)
    - skinning  (IntField)
    - tanning   (IntField)
    - updated   (DateTimeField)
    """
    _id = UUIDField(binary=False, primary_key=True, default=uuid.uuid4())
    recycling = IntField(default=None)
    skinning = IntField(default=None)
    tanning = IntField(default=None)
    updated = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'professions',
        'indexes': [],
        'uuid_representation': 'pythonLegacy'
    }
