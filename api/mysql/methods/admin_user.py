# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models.users     import User

from .fn_user           import fn_user_get_from_discord

#
# Queries /admin/user/*
#

# API: POST /admin/user
def admin_user(discordname):

    if not isinstance(discordname, str):
        return (200,
                False,
                f'Bad Discordname format (discordname:{discordname})',
                None)

    user = fn_user_get_from_discord(discordname)
    if user:
        return (200,
                True,
                f'Discordname found (discordname:{discordname})',
                user)
    else:
        return (200,
                False,
                f'Discordname not found (discordname:{discordname})',
                None)

def admin_user_validate(discordname, usermail):
    session = Session()

    if not isinstance(discordname, str):
        return (200,
                False,
                f'Bad Discordname format (discordname:{discordname})',
                None)
    if not isinstance(usermail, str):
        return (200,
                False,
                f'Bad Usermail format (usermail:{usermail})',
                None)
    try:
        user = session.query(User)\
                      .filter(User.mail == usermail)\
                      .one_or_none()

        user.d_name    = discordname
        user.d_ack     = True
        user.date      = datetime.now()
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Discord validation failed (discordname:{discordname},usermail:{usermail}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'Discord validation successed (discordname:{discordname},usermail:{usermail})',
                None)
    finally:
        session.close()
