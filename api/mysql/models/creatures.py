# -*- coding: utf8 -*-

from sqlalchemy                 import (Column,
                                        Integer,
                                        DateTime,
                                        Boolean,
                                        Text,
                                        Enum)
from sqlalchemy                 import func

from dataclasses                import dataclass
from datetime                   import datetime

from ..base                     import Base


# New Creature class.
# It will slowly replace in calls the former PJ class
@dataclass
class Creature(Base):
    __tablename__ = 'creatures'

    def __hash__(self):         # Used to aggregate & dedup lists of Creatures
        return hash(self.name)  # ex: with set() in /view

    id: int
    name: str
    race: int
    gender: bool
    rarity: str
    account: int
    targeted_by: int
    level: int
    x: int
    y: int
    xp: int
    hp: int      # Deprecated: remove it later
    hp_max: int  # Deprecated: remove it later
    instance: int
    squad: int
    squad_rank: str
    korp: int
    korp_rank: str
    date: str

    id           = Column(Integer, primary_key=True)
    name         = Column(Text, nullable=False)
    race         = Column(Integer, nullable=False)
    gender       = Column(Boolean, nullable=True, server_default='1')
    rarity       = Column(Enum('Small',
                               'Medium',
                               'Big',
                               'Unique',
                               'Boss',
                               'God'
                               ),
                          default='Medium')
    account      = Column(Integer, nullable=True)
    targeted_by  = Column(Integer, nullable=True)
    level        = Column(Integer, nullable=False, server_default='1')
    x            = Column(Integer, nullable=False, server_default='0')
    y            = Column(Integer, nullable=False, server_default='0')
    xp           = Column(Integer, nullable=False, server_default='0')
    hp           = Column(Integer, nullable=False)  # Deprecated
    hp_max       = Column(Integer, nullable=False)  # Deprecated
    instance     = Column(Integer, nullable=True)
    squad        = Column(Integer, nullable=True)
    squad_rank   = Column(Enum('Leader', 'Member', 'Pending'), nullable=True)
    korp         = Column(Integer, nullable=True)
    korp_rank    = Column(Enum('Leader', 'Member', 'Pending'), nullable=True)
    date         = Column(DateTime(timezone=True),
                          nullable=False,
                          server_default=datetime.now().isoformat(),
                          server_onupdate=datetime.now().isoformat())


@dataclass
class CreatureStats(Base):
    __tablename__ = 'creaturesStats'

    id: int
    m_race: int
    m_class: int
    m_skill: int
    m_point: int
    r_race: int
    r_class: int
    r_skill: int
    r_point: int
    g_race: int
    g_class: int
    g_skill: int
    g_point: int
    v_race: int
    v_class: int
    v_skill: int
    v_point: int
    p_race: int
    p_class: int
    p_skill: int
    p_point: int
    b_race: int
    b_class: int
    b_skill: int
    b_point: int
    points: int
    date: str

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
    date       = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now(), server_onupdate=func.now())


@dataclass
class Squad(Base):
    __tablename__ = 'creaturesSquads'

    id: int
    name: str
    leader: int
    created: str
    date: str

    id       = Column(Integer, primary_key=True)
    name     = Column(Text, nullable=True)
    leader   = Column(Integer, nullable=False)
    created  = Column(DateTime(timezone=True),
                      nullable=False,
                      server_default=func.now())
    date     = Column(DateTime(timezone=True),
                      nullable=False,
                      server_default=func.now(), server_onupdate=func.now())


@dataclass
class Korp(Base):
    __tablename__ = 'creaturesKorps'

    id: int
    name: str
    leader: int
    created: str
    date: str

    id       = Column(Integer, primary_key=True)
    name     = Column(Text, nullable=True)
    leader   = Column(Integer, nullable=False)
    created  = Column(DateTime(timezone=True),
                      nullable=False,
                      server_default=func.now())
    date     = Column(DateTime(timezone=True),
                      nullable=False,
                      server_default=func.now(), server_onupdate=func.now())
