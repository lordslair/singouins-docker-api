# -*- coding: utf8 -*-

from sqlalchemy                 import Column, Integer, DateTime, Boolean, Text, Enum
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base

@dataclass
class Cosmetics(Base):
    __tablename__ = 'cosmetics'

    id:         int
    bearer:     int
    bound:      bool
    bound_type: str
    state:      int
    rarity:     str
    data:       str
    date:       str

    id          = Column(Integer, primary_key=True)
    bearer      = Column(Integer, nullable=True)
    bound       = Column(Boolean, nullable=False)
    bound_type  = Column(Enum('BoE','BoP','BoA','BoU','BtA'))
    state       = Column(Integer, nullable=True)
    rarity      = Column(Enum('Legendary','Epic','Rare','Common','Uncommon','Broken'))
    data        = Column(Text,    nullable=True)
    date        = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
