# -*- coding: utf8 -*-

from ..engine                   import engine
from ..base                     import Base

def initialize_db():
    Base.metadata.create_all(bind=engine)
