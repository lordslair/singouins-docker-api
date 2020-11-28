# -*- coding: utf8 -*-

from sqlalchemy                 import Column, Integer, Text, DateTime, Enum
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base

@dataclass
class Map(Base):
    __tablename__ = 'maps'

    id:        int
    type:      str
    mode:      str
    size:      str
    data:      str
    date:      str

    id         = Column(Integer, primary_key=True)
    type       = Column(Text   , nullable=False)
    mode       = Column(Enum('Normal','Challenge'), default='Normal')
    size       = Column(Text   , nullable=False)
    data       = Column(Text   , nullable=False)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
