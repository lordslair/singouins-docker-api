# -*- coding: utf8 -*-

from sqlalchemy.orm import sessionmaker,scoped_session

from .engine        import engine

Session = scoped_session(sessionmaker(bind=engine))
