# -*- coding: utf8 -*-

from sqlalchemy                 import Column, Integer, DateTime, Boolean, Text, Enum
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base

@dataclass
class Cosmetic(Base):
    __tablename__ = 'cosmetics'

    id:         int
    metaid:     int
    bearer:     int
    bound:      bool
    bound_type: str
    state:      int
    rarity:     str
    data:       str
    date:       str

    id          = Column(Integer, primary_key=True)
    metaid      = Column(Integer, nullable=False)
    bearer      = Column(Integer, nullable=True)
    bound       = Column(Boolean, nullable=False)
    bound_type  = Column(Enum('BoE','BoP','BoA','BoU','BtA'))
    state       = Column(Integer, nullable=True)
    rarity      = Column(Enum('Legendary','Epic','Rare','Common','Uncommon','Broken'))
    data        = Column(Text,    nullable=True)
    date        = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())

@dataclass
class MetaWeapon(Base):
    __tablename__ = 'metaWeapons'

    id:         int
    name:       str
    tier:       int
    mastery:    int
    onehanded:  bool
    ranged:     bool
    rng:        int
    pas_use:    int
    pas_reload: int
    moddable:   bool
    caliber:    str
    rounds:     int
    max_ammo:   int
    burst_acc:  int
    size:       str
    dmg_base:   int
    dmg_sneaky: int
    dmg_shape:  str
    dmg_radius: int
    parry:      int
    arpen:      int
    defcan:     int
    min_m:      int
    min_r:      int
    min_g:      int
    min_v:      int
    min_p:      int
    min_b:      int

    id          = Column(Integer, primary_key=True)
    name        = Column(Text)
    tier        = Column(Integer)
    mastery     = Column(Integer)
    onehanded   = Column(Boolean)
    ranged      = Column(Boolean)
    rng         = Column(Integer) # Not 'range' cause it's s reserved SQL word
    pas_use     = Column(Integer)
    pas_reload  = Column(Integer)
    moddable    = Column(Boolean)
    caliber     = Column(Text)
    rounds      = Column(Integer)
    max_ammo    = Column(Integer, nullable=True)
    burst_acc   = Column(Integer, nullable=True)
    size        = Column(Text)
    dmg_base    = Column(Integer)
    dmg_sneaky  = Column(Integer)
    dmg_shape   = Column(Enum('Conic','Through'), nullable=True)
    dmg_radius  = Column(Integer, nullable=True)
    parry       = Column(Integer)
    arpen       = Column(Integer)
    defcan      = Column(Integer)
    min_m       = Column(Integer)
    min_r       = Column(Integer)
    min_g       = Column(Integer)
    min_v       = Column(Integer)
    min_p       = Column(Integer)
    min_b       = Column(Integer)

@dataclass
class MetaArmor(Base):
    __tablename__ = 'metaArmors'

    id:        int
    name:      str
    tier:      int
    mastery:   int
    moddable:  bool
    size:      str
    slot:      str
    block:     int
    parry:     int
    evasion:   int
    arm_p:     int
    arm_b:     int
    min_m:     int
    min_r:     int
    min_g:     int
    min_v:     int
    min_p:     int
    min_b:     int

    id         = Column(Integer, primary_key=True)
    name       = Column(Text)
    tier       = Column(Integer)
    mastery    = Column(Integer)
    moddable   = Column(Boolean)
    size       = Column(Text)
    slot       = Column(Enum('Head','Torso','Shoulders','Hands','Legs','Feet','Shield'))
    block      = Column(Integer)
    parry      = Column(Integer)
    evasion    = Column(Integer)
    arm_p      = Column(Integer)
    arm_b      = Column(Integer)
    min_m      = Column(Integer)
    min_r      = Column(Integer)
    min_g      = Column(Integer)
    min_v      = Column(Integer)
    min_p      = Column(Integer)
    min_b      = Column(Integer)

@dataclass
class Item(Base):
    __tablename__ = 'items'

    id:         int
    metatype:   str
    metaid:     int
    bearer:     int
    bound:      bool
    bound_type: str
    modded:     bool
    mods:       str
    state:      int
    ammo:       int
    rarity:     str
    offsetx:    int
    offsety:    int
    date:       str

    id          = Column(Integer, primary_key=True)
    metatype    = Column(Enum('armor','weapon'))
    metaid      = Column(Integer, nullable=False)
    bearer      = Column(Integer, nullable=False)
    bound       = Column(Boolean, nullable=False)
    bound_type  = Column(Enum('BoE','BoP','BoA','BoU','BtA'))
    modded      = Column(Boolean, nullable=False, server_default='0')
    mods        = Column(Text   , nullable=True)
    state       = Column(Integer, nullable=True)
    ammo        = Column(Integer, nullable=False, server_default='0')
    rarity      = Column(Enum('Legendary','Epic','Rare','Common','Uncommon','Broken'))
    offsetx     = Column(Integer, nullable=True)
    offsety     = Column(Integer, nullable=True)
    date        = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), server_onupdate=func.now())
