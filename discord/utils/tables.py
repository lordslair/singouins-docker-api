# -*- coding: utf8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy                 import Column, Integer, String, DateTime, Boolean
from sqlalchemy                 import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'pjsAuth'

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
