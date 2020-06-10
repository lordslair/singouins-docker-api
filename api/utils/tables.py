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

@dataclass
class MP(Base):
    __tablename__ = 'mps'

    id: int
    src_id: int
    src: str
    dst_id: int
    dst: int
    subject: str
    body: str
    date: str

    id      = Column(Integer, primary_key=True)
    src_id  = Column(Integer)
    src     = Column(String)
    dst_id  = Column(Integer)
    dst     = Column(String)
    subject = Column(String)
    body    = Column(String)
    date    = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class WeaponsMeta(Base):
    __tablename__ = 'weaponsMeta'

    id: int
    name: str
    mastery: int
    onehanded: bool
    ranged: bool
    rng: int
    pas_use: int
    pas_reload: int
    moddable: bool
    caliber: str
    rounds: int
    size: str
    dmg_base: int
    dmg_sneaky: int
    parry: int
    arpen: int
    defcan: int
    rarity: int

    id         = Column(Integer, primary_key=True)
    name       = Column(String)
    mastery    = Column(Integer)
    onehanded  = Column(Boolean)
    ranged     = Column(Boolean)
    rng        = Column(Integer)
    pas_use    = Column(Integer)
    pas_reload = Column(Integer)
    moddable   = Column(Boolean)
    caliber    = Column(String)
    rounds     = Column(Integer)
    size       = Column(String)
    dmg_base   = Column(Integer)
    dmg_sneaky = Column(Integer)
    parry      = Column(Integer)
    arpen      = Column(Integer)
    defcan     = Column(Integer)
    rarity     = Column(Integer)

@dataclass
class Weapons(Base):
    __tablename__ = 'weapons'

    id: int
    type: int
    bearer: int
    bound: bool
    bound_type: str
    modded: bool
    mods: str
    state: int
    date: str

    id         = Column(Integer, primary_key=True)
    type       = Column(Integer)
    bearer     = Column(Integer)
    bound      = Column(Boolean)
    bound_type = Column(String)
    modded     = Column(Boolean)
    mods       = Column(String)
    state      = Column(Integer)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
