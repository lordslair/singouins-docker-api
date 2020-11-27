# -*- coding: utf8 -*-

from sqlalchemy                 import Column, Integer, DateTime, Boolean, Text, Enum
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base

@dataclass
class PJ(Base):
    __tablename__ = 'creatures'

    id:          int
    name:        str
    race:        int
    rarity:      str
    account:     int
    targeted_by: int
    level:       int
    x:           int
    y:           int
    xp:          int
    hp:          int
    hp_max:      int
    arm_p:       int
    arm_b:       int
    instance:    int
    squad:       int
    squad_rank:  str
    m:           int
    r:           int
    g:           int
    v:           int
    p:           int
    b:           int
    date:        str

    id           = Column(Integer, primary_key=True)
    name         = Column(Text   , nullable=False)
    race         = Column(Integer, nullable=False)
    rarity       = Column(Enum('Small','Normal','Big','Unique','Boss','God'), default='Normal')
    account      = Column(Integer, nullable=True)
    targeted_by  = Column(Integer, nullable=True)
    level        = Column(Integer, nullable=False, default=1)
    x            = Column(Integer, nullable=False, default=0)
    y            = Column(Integer, nullable=False, default=0)
    xp           = Column(Integer, nullable=False, default=0)
    hp           = Column(Integer, nullable=False)
    hp_max       = Column(Integer, nullable=False)
    arm_b        = Column(Integer, nullable=False, default=0)
    arm_p        = Column(Integer, nullable=False, default=0)
    instance     = Column(Integer, nullable=True)
    squad        = Column(Integer, nullable=True)
    squad_rank   = Column(Enum('Leader','Member','Pending'), nullable=True)
    m            = Column(Integer, nullable=False, default=0)
    r            = Column(Integer, nullable=False, default=0)
    g            = Column(Integer, nullable=False, default=0)
    v            = Column(Integer, nullable=False, default=0)
    p            = Column(Integer, nullable=False, default=0)
    b            = Column(Integer, nullable=False, default=0)
    date         = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

class Wallet(Base):
    __tablename__ = 'creaturesWallet'

    id:        int
    currency:  int
    legendary: int
    epic:      int
    rare:      int
    uncommon:  int
    common:    int
    broken:    int
    date:      str

    id         = Column(Integer, primary_key=True)
    currency   = Column(Integer, default=0)
    legendary  = Column(Integer, default=0)
    epic       = Column(Integer, default=0)
    rare       = Column(Integer, default=0)
    uncommon   = Column(Integer, default=0)
    common     = Column(Integer, default=0)
    broken     = Column(Integer, default=0)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class CreaturesSlots(Base):
    __tablename__ = 'creaturesSlots'

    id:        int
    lefthand:  int
    righthand: int
    holster:   int
    head:      int
    shoulders: int
    torso:     int
    hands:     int
    legs:      int
    feet:      int
    date:      str

    id         = Column(Integer, primary_key=True)
    lefthand   = Column(Integer, nullable=True)
    righthand  = Column(Integer, nullable=True)
    holster    = Column(Integer, nullable=True)
    head       = Column(Integer, nullable=True)
    shoulders  = Column(Integer, nullable=True)
    torso      = Column(Integer, nullable=True)
    hands      = Column(Integer, nullable=True)
    legs       = Column(Integer, nullable=True)
    feet       = Column(Integer, nullable=True)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class Log(Base):
    __tablename__ = 'creaturesLog'

    id:        int
    src:       int
    dst:       int
    action:    str
    date:      str

    id         = Column(Integer, primary_key=True)
    src        = Column(Integer, nullable=False)
    dst        = Column(Integer, nullable=True)
    action     = Column(Text,  nullable=False)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class CreaturesStats(Base):
    __tablename__ = 'creaturesStats'

    id: int
    m_race:  int
    m_class: int
    m_skill: int
    m_point: int
    r_race:  int
    r_class: int
    r_skill: int
    r_point: int
    g_race:  int
    g_class: int
    g_skill: int
    g_point: int
    v_race:  int
    v_class: int
    v_skill: int
    v_point: int
    p_race:  int
    p_class: int
    p_skill: int
    p_point: int
    b_race:  int
    b_class: int
    b_skill: int
    b_point: int
    points:  int
    date: str

    id         = Column(Integer, primary_key=True)
    m_race     = Column(Integer)
    m_class    = Column(Integer)
    m_skill    = Column(Integer)
    m_point    = Column(Integer)
    r_race     = Column(Integer)
    r_class    = Column(Integer)
    r_skill    = Column(Integer)
    r_point    = Column(Integer)
    g_race     = Column(Integer)
    g_class    = Column(Integer)
    g_skill    = Column(Integer)
    g_point    = Column(Integer)
    v_race     = Column(Integer)
    v_class    = Column(Integer)
    v_skill    = Column(Integer)
    v_point    = Column(Integer)
    p_race     = Column(Integer)
    p_class    = Column(Integer)
    p_skill    = Column(Integer)
    p_point    = Column(Integer)
    b_race     = Column(Integer)
    b_class    = Column(Integer)
    b_skill    = Column(Integer)
    b_point    = Column(Integer)
    points     = Column(Integer)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
