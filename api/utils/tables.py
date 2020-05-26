# -*- coding: utf8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Column, Integer, String, DateTime, Boolean
from sqlalchemy                 import func

from dataclasses                import dataclass

Base = declarative_base()

class User(Base):
    __tablename__ = 'pjsAuth'

    id      = Column(Integer, primary_key=True)
    name    = Column(String)
    mail    = Column(String)
    hash    = Column(String)
    created = Column(DateTime)
    active  = Column(Boolean)
    date    = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class PJ(Base):
    __tablename__ = 'pjsInfos'

    id: int
    name: str
    race: str
    account: int
    level: int
    x: int
    y: int
    xp: int
    date: str

    id      = Column(Integer, primary_key=True)
    name    = Column(String)
    race    = Column(String)
    account = Column(Integer)
    level   = Column(Integer)
    x       = Column(Integer)
    y       = Column(Integer)
    xp      = Column(Integer)
    date    = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
