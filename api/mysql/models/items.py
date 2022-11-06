# -*- coding: utf8 -*-

from sqlalchemy                 import (Column,
                                        Integer,
                                        DateTime,
                                        Boolean,
                                        Text,
                                        Enum)
from sqlalchemy                 import func

from dataclasses                import dataclass

from ..base                     import Base


@dataclass
class Item(Base):
    __tablename__ = 'items'

    id: int
    metatype: str
    metaid: int
    bearer: int
    bound: bool
    bound_type: str
    modded: bool
    mods: str
    state: int
    ammo: int
    rarity: str
    offsetx: int
    offsety: int
    date: str

    id          = Column(Integer, primary_key=True)
    metatype    = Column(Enum('armor', 'weapon'))
    metaid      = Column(Integer, nullable=False)
    bearer      = Column(Integer, nullable=True)
    bound       = Column(Boolean, nullable=False)
    bound_type  = Column(Enum('BoE', 'BoP', 'BoA', 'BoU', 'BtA'))
    modded      = Column(Boolean, nullable=False, server_default='0')
    mods        = Column(Text, nullable=True)
    state       = Column(Integer, nullable=True)
    ammo        = Column(Integer, nullable=True)
    rarity      = Column(Enum('Legendary',
                              'Epic',
                              'Rare',
                              'Common',
                              'Uncommon',
                              'Broken'))
    offsetx     = Column(Integer, nullable=True)
    offsety     = Column(Integer, nullable=True)
    date        = Column(DateTime(timezone=True),
                         nullable=False,
                         server_default=func.now(), server_onupdate=func.now())
