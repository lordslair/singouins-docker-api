# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import User


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
