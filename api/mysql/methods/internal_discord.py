# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models.users     import User
from ..models.creatures import PJ

from .fn_creature       import fn_creature_get
from .fn_user           import (fn_user_get,
                                fn_user_get_from_discord)

#
# Queries /internal/discord/*
#

# API: POST /internal/discord/creature
def internal_discord_creature(creatureid,discordname):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)
    if not isinstance(discordname, str):
        return (200,
                False,
                f'Bad Discordname format (discordname:{discordname})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)
    user        = fn_user_get_from_discord(discordname)
    if user is None:
        return (200,
                False,
                f'Discordname unknown (discordname:{discordname})',
                None)

    if creature.account == user.id:
        # The Discord user owns the Creature
        return (200,
                True,
                f'User has permissions on Creature (discordname:{discordname},creatureid:{creature.id})',
                {"user": user,
                "creature": creature})
    else:
        # The Discord user do NOT own the Creature
        return (200,
                False,
                f'User has NOT permissions on Creature (discordname:{discordname},creatureid:{creature.id})',
                None)

# API: POST /internal/discord/creatures
def internal_discord_creatures(discordname):

    if not isinstance(discordname, str):
        return (200,
                False,
                f'Bad Discordname format (discordname:{discordname})',
                None)

    user = fn_user_get_from_discord(discordname)
    if user is None:
        return (200,
                False,
                f'Discordname not found (discordname:{discordname})',
                None)

    session = Session()
    try:
        pcs = session.query(PJ)\
                     .filter(PJ.account == user.id)\
                     .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Creatures query failed (discordname:{discordname},userid:{user.id}) [{e}]',
                None)
    else:
        if pcs:
            return (200,
                    True,
                    f'Creatures found (discordname:{discordname},userid:{user.id})',
                    pcs)
        else:
            return (200,
                    False,
                    f'Creatures not found (discordname:{discordname},userid:{user.id})',
                    None)
    finally:
        session.close()

# API: POST /internal/discord/user
def internal_discord_user(discordname):

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

# API: POST /internal/discord/user/associate
def internal_discord_user_associate(discordname, usermail):
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
                f'[SQL] Discord association failed (discordname:{discordname},usermail:{usermail}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'Discord association successed (discordname:{discordname},usermail:{usermail})',
                fn_user_get(usermail))
    finally:
        session.close()
