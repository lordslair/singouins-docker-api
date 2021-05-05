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
    korp:        int
    korp_rank:   str
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
    rarity       = Column(Enum('Small','Medium','Big','Unique','Boss','God'), default='Medium')
    account      = Column(Integer, nullable=True)
    targeted_by  = Column(Integer, nullable=True)
    level        = Column(Integer, nullable=False, server_default='1')
    x            = Column(Integer, nullable=False, server_default='0')
    y            = Column(Integer, nullable=False, server_default='0')
    xp           = Column(Integer, nullable=False, server_default='0')
    hp           = Column(Integer, nullable=False)
    hp_max       = Column(Integer, nullable=False)
    arm_b        = Column(Integer, nullable=False, server_default='0')
    arm_p        = Column(Integer, nullable=False, server_default='0')
    instance     = Column(Integer, nullable=True)
    squad        = Column(Integer, nullable=True)
    squad_rank   = Column(Enum('Leader','Member','Pending'), nullable=True)
    korp         = Column(Integer, nullable=True)
    korp_rank    = Column(Enum('Leader','Member','Pending'), nullable=True)
    m            = Column(Integer, nullable=False, server_default='0')
    r            = Column(Integer, nullable=False, server_default='0')
    g            = Column(Integer, nullable=False, server_default='0')
    v            = Column(Integer, nullable=False, server_default='0')
    p            = Column(Integer, nullable=False, server_default='0')
    b            = Column(Integer, nullable=False, server_default='0')
    date         = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
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
    arrow:     int
    bolt:      int
    shell:     int
    cal22:     int
    cal223:    int
    cal311:    int
    cal50:     int
    cal55:     int
    date:      str

    id         = Column(Integer, primary_key=True)
    currency   = Column(Integer, nullable=False, server_default='0')
    legendary  = Column(Integer, nullable=False, server_default='0')
    epic       = Column(Integer, nullable=False, server_default='0')
    rare       = Column(Integer, nullable=False, server_default='0')
    uncommon   = Column(Integer, nullable=False, server_default='0')
    common     = Column(Integer, nullable=False, server_default='0')
    broken     = Column(Integer, nullable=False, server_default='0')
    arrow      = Column(Integer, nullable=False, server_default='0')
    bolt       = Column(Integer, nullable=False, server_default='0')
    shell      = Column(Integer, nullable=False, server_default='0')
    cal22      = Column(Integer, nullable=False, server_default='0')
    cal223     = Column(Integer, nullable=False, server_default='0')
    cal311     = Column(Integer, nullable=False, server_default='0')
    cal50      = Column(Integer, nullable=False, server_default='0')
    cal55      = Column(Integer, nullable=False, server_default='0')
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class CreatureSlots(Base):
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
    action     = Column(Text   , nullable=False)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class CreatureStats(Base):
    __tablename__ = 'creaturesStats'

    id:        int
    m_race:    int
    m_class:   int
    m_skill:   int
    m_point:   int
    r_race:    int
    r_class:   int
    r_skill:   int
    r_point:   int
    g_race:    int
    g_class:   int
    g_skill:   int
    g_point:   int
    v_race:    int
    v_class:   int
    v_skill:   int
    v_point:   int
    p_race:    int
    p_class:   int
    p_skill:   int
    p_point:   int
    b_race:    int
    b_class:   int
    b_skill:   int
    b_point:   int
    points:    int
    date:      str

    id         = Column(Integer, primary_key=True)
    m_race     = Column(Integer, nullable=False, server_default='0')
    m_class    = Column(Integer, nullable=False, server_default='0')
    m_skill    = Column(Integer, nullable=False, server_default='0')
    m_point    = Column(Integer, nullable=False, server_default='0')
    r_race     = Column(Integer, nullable=False, server_default='0')
    r_class    = Column(Integer, nullable=False, server_default='0')
    r_skill    = Column(Integer, nullable=False, server_default='0')
    r_point    = Column(Integer, nullable=False, server_default='0')
    g_race     = Column(Integer, nullable=False, server_default='0')
    g_class    = Column(Integer, nullable=False, server_default='0')
    g_skill    = Column(Integer, nullable=False, server_default='0')
    g_point    = Column(Integer, nullable=False, server_default='0')
    v_race     = Column(Integer, nullable=False, server_default='0')
    v_class    = Column(Integer, nullable=False, server_default='0')
    v_skill    = Column(Integer, nullable=False, server_default='0')
    v_point    = Column(Integer, nullable=False, server_default='0')
    p_race     = Column(Integer, nullable=False, server_default='0')
    p_class    = Column(Integer, nullable=False, server_default='0')
    p_skill    = Column(Integer, nullable=False, server_default='0')
    p_point    = Column(Integer, nullable=False, server_default='0')
    b_race     = Column(Integer, nullable=False, server_default='0')
    b_class    = Column(Integer, nullable=False, server_default='0')
    b_skill    = Column(Integer, nullable=False, server_default='0')
    b_point    = Column(Integer, nullable=False, server_default='0')
    points     = Column(Integer, nullable=False, server_default='0')
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class Squad(Base):
    __tablename__ = 'creaturesSquads'

    id:      int
    name:    str
    leader:  int
    created: str
    date:    str

    id       = Column(Integer, primary_key=True)
    name     = Column(Text   , nullable=True)
    leader   = Column(Integer, nullable=False)
    created  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date     = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class Korp(Base):
    __tablename__ = 'creaturesKorps'

    id:      int
    name:    str
    leader:  int
    created: str
    date:    str

    id       = Column(Integer, primary_key=True)
    name     = Column(Text   , nullable=True)
    leader   = Column(Integer, nullable=False)
    created  = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    date     = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class MetaRace(Base):
    __tablename__ = 'metaRaces'

    id:        int
    name:      str
    lootable:  bool
    min_level: int
    max_level: int
    min_m:     int
    max_m:     int
    min_r:     int
    max_r:     int
    min_g:     int
    max_g:     int
    min_v:     int
    max_v:     int
    min_p:     int
    max_p:     int
    min_b:     int
    max_b:     int

    id         = Column(Integer, primary_key=True)
    name       = Column(Text   , nullable=False)
    lootable   = Column(Boolean, nullable=False, server_default='1')
    min_level  = Column(Integer, nullable=False)
    max_level  = Column(Integer, nullable=False)
    min_m      = Column(Integer, nullable=False)
    max_m      = Column(Integer, nullable=False)
    min_r      = Column(Integer, nullable=False)
    max_r      = Column(Integer, nullable=False)
    min_g      = Column(Integer, nullable=False)
    max_g      = Column(Integer, nullable=False)
    min_v      = Column(Integer, nullable=False)
    max_v      = Column(Integer, nullable=False)
    min_p      = Column(Integer, nullable=False)
    max_p      = Column(Integer, nullable=False)
    min_b      = Column(Integer, nullable=False)
    max_b      = Column(Integer, nullable=False)

@dataclass
class CreatureSkills(Base):
    __tablename__ = 'creaturesSkills'

    id:      int
    skills:  str
    date:    str

    id       = Column(Integer, primary_key=True)
    skills   = Column(Text   , nullable=True)    # Here it will be a JSON
    date     = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
