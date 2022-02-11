# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import Log

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get

#
# Queries /events
#

def get_mypc_event(username,creatureid):
    creature    = fn_creature_get(None,creatureid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if creature is None:
        return (200,
                False,
                f'PC not found (creatureid:{creatureid})',
                None)
    if creature.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (creatureid:{creature.id},username:{username})',
                None)

    try:
        log   = session.query(Log)\
                       .filter((Log.src == creature.id) | (Log.dst == creature.id))\
                       .order_by(Log.date.desc())\
                       .limit(50)\
                       .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Event query failed (creatureid:{creatureid})',
                None)
    else:
        return (200,
                True,
                f'Event query successed (creatureid:{creatureid})',
                log)
    finally:
        session.close()
