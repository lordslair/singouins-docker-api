# -*- coding: utf8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Column, Integer, String, DateTime, Boolean
from sqlalchemy                 import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id        = Column(Integer, primary_key=True)
    name      = Column(String)
    mail      = Column(String)
    hash      = Column(String)
    d_name    = Column(String)
    d_monkeys = Column(String)
    d_ack     = Column(Boolean)
    created   = Column(DateTime)
    active    = Column(Boolean)
    date      = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class Creatures(Base):
    __tablename__ = 'creatures'

    id: int
    name: str
    race: str
    account: int
    level: int
    x: int
    y: int
    xp: int
    instance: int
    squad: int
    squad_rank: str
    avatar: str
    sprite: str
    m: int
    r: int
    g: int
    v: int
    p: int
    b: int
    arm_p: int
    hp: int
    date: str

    id         = Column(Integer, primary_key=True)
    name       = Column(String)
    race       = Column(String)
    account    = Column(Integer)
    level      = Column(Integer)
    x          = Column(Integer)
    y          = Column(Integer)
    xp         = Column(Integer)
    instance   = Column(Integer)
    squad      = Column(Integer)
    squad_rank = Column(String)
    avatar     = Column(String)
    sprite     = Column(String)
    m          = Column(Integer)
    r          = Column(Integer)
    g          = Column(Integer)
    v          = Column(Integer)
    p          = Column(Integer)
    b          = Column(Integer)
    arm_p      = Column(Integer)
    hp         = Column(Integer)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
