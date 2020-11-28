# -*- coding: utf8 -*-

from sqlalchemy                 import Column, Integer, DateTime, Text
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base

@dataclass
class MP(Base):
    __tablename__ = 'mps'

    id:      int
    src_id:  int
    src:     str
    dst_id:  int
    dst:     int
    subject: str
    body:    str
    date:    str

    id       = Column(Integer, primary_key=True)
    src_id   = Column(Integer, nullable=False)
    src      = Column(Text   , nullable=False)
    dst_id   = Column(Integer, nullable=False)
    dst      = Column(Text   , nullable=False)
    subject  = Column(Text   , nullable=False)
    body     = Column(Text   , nullable=False)
    date     = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
