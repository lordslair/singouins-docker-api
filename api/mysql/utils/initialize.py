# -*- coding: utf8 -*-

from ..engine                   import engine
from ..base                     import Base

def initialize_db():
    print('DB init: start')
    Base.metadata.create_all(bind=engine)
    print('DB init: end')
