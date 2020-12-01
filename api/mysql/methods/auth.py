# -*- coding: utf8 -*-

from flask_bcrypt       import generate_password_hash

from ..session          import Session
from ..models           import *

#
# Queries /mypc/{pcid}/action/*
#

def get_username_exists(username):
    session = Session()

    try:
        result = session.query(User)\
                        .filter(User.name == username)\
                        .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return True
    finally:
        session.close()

def get_usermail_exists(usermail):
    session = Session()

    try:
       result = session.query(User)\
                       .filter(User.mail == usermail)\
                       .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return True
    finally:
        session.close()

def add_user(username,password,usermail):
    session = Session()

    if get_username_exists(username) or get_usermail_exists(usermail):
        return (409)
    else:
        user = User(name      = username,
                    mail      = usermail,
                    hash      = generate_password_hash(password, rounds = 10),
                    d_name    = '',
                    d_monkeys = '', # Todo later
                    d_ack     = False,
                    created   = datetime.now(),
                    active    = False)

        session.add(user)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (422)
        else:
            return (201)
        finally:
            session.close()

def set_user_confirmed(usermail):
    session = Session()

    try:
        user = session.query(User)\
                      .filter(User.mail == usermail)\
                      .one_or_none()
        user.active = True
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (422)
    else:
        return (201)
    finally:
        session.close()

def del_user(username):
    session = Session()

    if not get_username_exists(username):
        return (404)
    else:
        try:
            user = session.query(User)\
                          .filter(User.name == username)\
                          .one_or_none()
            session.delete(user)
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (422)
        else:
            return (200)
        finally:
            session.close()
