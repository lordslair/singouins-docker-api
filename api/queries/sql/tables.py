# -*- coding: utf8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Column, Integer, String, DateTime, Boolean
from sqlalchemy                 import func

from dataclasses                import dataclass

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
class PJ(Base):
    __tablename__ = 'creatures'

    id: int
    name: str
    race: str
    account: int
    level: int
    x: int
    y: int
    xp: int
    hp: int
    hp_max: int
    arm_p: int
    arm_b: int
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
    hp         = Column(Integer)
    hp_max     = Column(Integer)
    arm_b      = Column(Integer)
    arm_p      = Column(Integer)
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
class Squad(Base):
    __tablename__ = 'squads'

    id: int
    name: str
    leader: int
    created: str
    date: str

    id      = Column(Integer, primary_key=True)
    name    = Column(String)
    leader  = Column(String)
    created = Column(DateTime)
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
    min_m: int
    min_r: int
    min_g: int
    min_v: int
    min_p: int
    min_b: int

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
    min_m      = Column(Integer)
    min_r      = Column(Integer)
    min_g      = Column(Integer)
    min_v      = Column(Integer)
    min_p      = Column(Integer)
    min_b      = Column(Integer)

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
    rarity: int
    offsetx: int
    offsety: int
    date: str

    id         = Column(Integer, primary_key=True)
    type       = Column(Integer)
    bearer     = Column(Integer)
    bound      = Column(Boolean)
    bound_type = Column(String)
    modded     = Column(Boolean)
    mods       = Column(String)
    state      = Column(Integer)
    rarity     = Column(Integer)
    offsetx    = Column(Integer)
    offsety    = Column(Integer)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class GearMeta(Base):
    __tablename__ = 'gearMeta'

    id: int
    name: str
    tier: bool
    mastery: int
    moddable: bool
    size: str
    arm_p: int
    arm_b: int
    min_m: int
    min_r: int
    min_g: int
    min_v: int
    min_p: int
    min_b: int

    id         = Column(Integer, primary_key=True)
    name       = Column(String)
    mastery    = Column(Integer)
    tier       = Column(Integer)
    moddable   = Column(Boolean)
    size       = Column(String)
    arm_p      = Column(Integer)
    arm_b      = Column(Integer)
    min_m      = Column(Integer)
    min_r      = Column(Integer)
    min_g      = Column(Integer)
    min_v      = Column(Integer)
    min_p      = Column(Integer)
    min_b      = Column(Integer)

@dataclass
class Gear(Base):
    __tablename__ = 'gear'

    id: int
    type: int
    bearer: int
    bound: bool
    bound_type: str
    modded: bool
    mods: str
    state: int
    rarity: int
    offsetx: int
    offsety: int
    date: str

    id         = Column(Integer, primary_key=True)
    type       = Column(Integer)
    bearer     = Column(Integer)
    bound      = Column(Boolean)
    bound_type = Column(String)
    modded     = Column(Boolean)
    mods       = Column(String)
    state      = Column(Integer)
    rarity     = Column(Integer)
    offsetx    = Column(Integer)
    offsety    = Column(Integer)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class Map(Base):
    __tablename__ = 'maps'

    id: int
    type: str
    size: int
    data: bool
    date: str

    id         = Column(Integer, primary_key=True)
    type       = Column(String)
    size       = Column(String)
    data       = Column(String)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class Log(Base):
    __tablename__ = 'creaturesLog'

    id: int
    src: int
    dst: int
    action: str
    date: str

    id         = Column(Integer, primary_key=True)
    src        = Column(Integer)
    dst        = Column(Integer)
    action     = Column(String)
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
    ammo:      int

    id         = Column(Integer, primary_key=True)
    lefthand   = Column(Integer)
    righthand  = Column(Integer)
    holster    = Column(Integer)
    head       = Column(Integer)
    shoulders  = Column(Integer)
    torso      = Column(Integer)
    hands      = Column(Integer)
    legs       = Column(Integer)
    feet       = Column(Integer)
    ammo       = Column(Integer)
    date       = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
