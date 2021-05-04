# -*- coding: utf8 -*-

from sqlalchemy                 import Column, Integer, DateTime, Boolean, Text, Enum
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base

@dataclass
class MetaSkill(Base):
    __tablename__ = 'metaSkills'

    id:         int
    name:       str
    duration:   int
    levels:     int

    id          = Column(Integer, primary_key=True)
    name        = Column(Text)
    duration    = Column(Integer)
    levels      = Column(Integer)
