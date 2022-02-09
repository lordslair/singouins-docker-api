# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import Log

from .fn_creature       import fn_creature_get

#
# Queries /pc/{pcid}/item/{itemid}/*
#

# API: /pc/<int:pcid>/event
def pc_events_get(creatureid):
    creature = fn_creature_get(None,creatureid)[3]
    session  = Session()

    # Pre-flight checks
    if creature is None:
        return (200,
                False,
                f'Creature not found (creatureid:{creatureid})',
                None)

    try:
        log   = session.query(Log)\
                       .filter(Log.src == creature.id)\
                       .order_by(Log.date.desc())\
                       .limit(50)\
                       .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Event query failed (creatureid:{creature.id})',
                None)
    else:
        return (200,
                True,
                f'Event query successed (creatureid:{creature.id})',
                log)
    finally:
        session.close()
