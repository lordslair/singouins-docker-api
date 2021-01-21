# -*- coding: utf8 -*-

from sqlalchemy                 import Column, Integer, DateTime, Boolean, Text
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base

@dataclass
class User(Base):
    __tablename__ = 'users'

    id:        int
    name:      str
    mail:      str
    hash:      str
    d_name:    str
    d_monkeys: str
    d_ack:     bool
    created:   str
    active:    bool
    date:      str

    id        = Column(Integer, primary_key=True)
    name      = Column(Text   , nullable=False)
    mail      = Column(Text   , nullable=False)
    hash      = Column(Text   , nullable=False)
    d_name    = Column(Text   , nullable=True)
    d_monkeys = Column(Text(collation='utf8mb4_general_ci') , nullable=True)
    d_ack     = Column(Boolean, nullable=False, server_default='0')
    created   = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    active    = Column(Boolean, nullable=False, server_default='0')
    date      = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
