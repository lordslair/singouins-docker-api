# -*- coding: utf8 -*-

from datetime       import datetime
from random         import randint

from ..session          import Session
from ..models           import *
from ..utils.loot       import *
from ..utils.redis      import *

from .fn_creature       import *
from .fn_user           import *
from .fn_global         import clog

#
# Queries /meta
#

def get_meta_item(metatype):
    session = Session()

    try:
        if    metatype == 'weapon': meta = session.query(MetaWeapon).all()
        elif  metatype == 'armor':  meta = session.query(MetaArmor).all()
        else:  meta = None
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Meta query failed (metatype:{})'.format(metatype),
                None)
    else:
        if meta:
            return (200, True, 'OK', meta)
        else:
            return (200, False, 'Meta does not exist (metatype:{})'.format(metatype), None)
    finally:
        session.close()

#
# Queries /events
#

def get_mypc_event(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            log   = session.query(Log)\
                           .filter((Log.src == pc.id) | (Log.dst == pc.id))\
                           .order_by(Log.date.desc())\
                           .limit(50)\
                           .all()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Event query failed (username:{},pcid:{})'.format(username,pcid),
                    None)
        else:
            return (200, True, 'Events successfully retrieved (pcid:{})'.format(pc.id), log)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)

def get_pc_event(creatureid):
    (code, success, msg, creature) = fn_creature_get(None,creatureid)
    session                        = Session()

    if creature is None: return (200, True, 'Creature does not exist (creatureid:{})'.format(creatureid), None)

    try:
        log   = session.query(Log)\
                       .filter(Log.src == creature.id)\
                       .order_by(Log.date.desc())\
                       .limit(50)\
                       .all()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Event query failed (creatureid:{})'.format(creature.id),
                None)
    else:
        return (200, True, 'Events successfully retrieved (creatureid:{})'.format(creature.id), log)
    finally:
        session.close()
