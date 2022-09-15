# -*- coding: utf8 -*-

import string

from datetime                   import datetime
from flask_bcrypt               import generate_password_hash
from loguru                     import logger
from random                     import choice

from mysql.session              import Session
from mysql.models               import User


def fn_forgot_password(username):
    session        = Session()
    length         = 12
    letterset      = string.ascii_letters + string.digits
    password       = ''.join((choice(letterset) for i in range(length)))

    if not fn_user_get(username):
        return (404, None)
    else:
        try:
            user = session.query(User)\
                          .filter(User.name == username)\
                          .one_or_none()

            user.hash      = generate_password_hash(password,
                                                    rounds=10)
            user.date      = datetime.now()

            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f'User Query KO (username:{username}) [{e}]')
            return (422, None)
        else:
            return (200, password)
        finally:
            session.close()


def fn_user_add(username, password):
    session = Session()

    if fn_user_get(username):
        return (409)
    else:
        user = User(name=username,
                    mail=username,
                    hash=generate_password_hash(password, rounds=10))

        session.add(user)

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f'User Query KO (username:{username}) [{e}]')
            return (422)
        else:
            logger.trace(f'User Query OK (username:{username})')
            return (201)
        finally:
            session.close()


def fn_user_confirm(username):
    session        = Session()

    try:
        user = session.query(User)\
                      .filter(User.name == username)\
                      .one_or_none()

        user.active = True

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'User Query KO (username:{username}) [{e}]')
        return None
    else:
        return user
    finally:
        session.close()


def fn_user_del(username):
    session = Session()

    if not fn_user_get(username):
        return (404)
    else:
        try:
            user = session.query(User)\
                          .filter(User.name == username)\
                          .one_or_none()
            session.delete(user)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f'User Query KO (username:{username}) [{e}]')
            return (422)
        else:
            logger.trace(f'User Query OK (username:{username})')
            return (200)
        finally:
            session.close()


def fn_user_get(username):
    session = Session()

    try:
        result = session.query(User)\
                        .filter(User.name == username)\
                        .one_or_none()
    except Exception as e:
        logger.error(f'User Query KO (username:{username}) [{e}]')
        return None
    else:
        if result:
            logger.trace(f'User Query OK (username:{username})')
            return result
        else:
            logger.trace(f'User Query KO - NotFound (username:{username})')
            return False
    finally:
        session.close()


def fn_user_get_from_creature(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        result = session.query(User)\
                        .filter(User.id == creature.account)\
                        .one_or_none()
    except Exception as e:
        logger.error(f'{h} User Query KO[{e}]')
        return False
    else:
        if result:
            logger.trace(f'{h} User Query OK')
            return result
        else:
            logger.warning(f'{h} User Query KO - NotFound')
            return False
    finally:
        session.close()


def fn_user_get_from_discord(discordname):
    session = Session()
    h       = f'[Discord.name:{discordname}]'  # Header for logging

    try:
        result = session.query(User)\
                        .filter(User.d_name == discordname)\
                        .one_or_none()
    except Exception as e:
        logger.error(f'{h} User Query KO [{e}]')
        return False
    else:
        if result:
            logger.trace(f'{h} User Query OK')
            return result
        else:
            logger.warning(f'{h} User Query KO - NotFound')
            return False
    finally:
        session.close()


def fn_user_link_from_discord(discordname, usermail):
    session = Session()
    h       = f'[Discord.name:{discordname}]'  # Header for logging

    try:
        user = session.query(User)\
                      .filter(User.mail == usermail)\
                      .one_or_none()

        user.d_name    = discordname
        user.d_ack     = True

        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} User Query KO [{e}]')
        return False
    else:
        if user:
            logger.trace(f'{h} User Query OK')
            return user
        else:
            logger.warning(f'{h} User Query KO - NotFound')
            return False
    finally:
        session.close()
