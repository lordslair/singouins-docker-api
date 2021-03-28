# -*- coding: utf8 -*-

from datetime       import datetime
from random         import randint

import textwrap

from ..session          import Session
from ..models           import *
from ..utils.loot       import *
from ..utils.redis      import *

from .fn_creature       import *
from .fn_user           import *
from .fn_global         import clog

#
# Queries: /mp
#

def add_mp(username,src,dsts,subject,body):
    (code, success, msg, pcsrc) = fn_creature_get(None,src)
    user                        = fn_user_get(username)
    session                     = Session()

    if pcsrc:
        for dst in dsts:
            (code, success, msg, pcdst) = fn_creature_get(None,dst)
            if pcdst:
                mp = MP(src_id  = pcsrc.id,
                        src     = pcsrc.name,
                        dst_id  = pcdst.id,
                        dst     = pcdst.name,
                        subject = subject,
                        body    = body)
                session.add(mp)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            session.rollback()
            return (200,
                    False,
                    '[SQL] MP creation failed (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                    None)
        else:
            return (201,
                    True,
                    'MP successfully created (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                    None)
        finally:
            session.close()

    elif user.id != pcsrc.account:
        return (409, False, 'Token/username mismatch', None)
    else:
        return (200,
                False,
                'PC does not exist (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                None)

def get_mp(username,pcid,mpid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
        except Exception as e:
            # Something went wrong during query
            return (200,
                    False,
                    '[SQL] MP query failed (pcid:{},mpid:{})'.format(pc.id,mpid),
                    None)
        else:
            if mp:
                return (200,
                        True,
                        'MP successfully found (pcid:{},mpid:{})'.format(pc.id,mpid),
                        mp)
            else:
                return (200, True, 'MP not found (pcid:{},mpid:{})'.format(pc.id,mpid), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def del_mp(username,pcid,mpid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
            if not mp: return (200, True, 'No MP found for this PC', None)
            session.delete(mp)
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] MP deletion failed', None)
        else:
            return (200, True, 'MP successfully deleted', None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def get_mps(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mps = session.query(MP).filter(MP.dst_id == pc.id).all()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] MPs query failed (pcid:{})'.format(pc.id), None)
        else:
            if mps:
                for mp in mps: mp.body = textwrap.shorten(mp.body, width=50, placeholder="...")
                return (200, True, 'MPs successfully found (pcid:{})'.format(pc.id), mps)
            else:
                return (200, True, 'No MP found (pcid:{})'.format(pc.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def get_mp_addressbook(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            addressbook = session.query(PJ).with_entities(PJ.id,PJ.name).all()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Addressbook query failed (pcid:{})'.format(pc.id), None)
        else:
            if addressbook:
                return (200, True, 'Addressbook successfully found (pcid:{})'.format(pc.id), addressbook)
            else:
                return (200, True, 'No Addressbook found (pcid:{})'.format(pc.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

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
# Queries /map
#

def get_map(mapid):
    session = Session()

    if mapid:
        try:
            map = session.query(Map).filter(Map.id == mapid).one_or_none()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Map query failed (mapid:{})'.format(mapid), None)
        else:
            if map:
                return (200, True, 'Map query successed (mapid:{})'.format(mapid), map)
            else:
                return (200, False, 'Map does not exist (mapid:{})'.format(mapid), None)
        finally:
            session.close()
    else: return (200, False, 'Incorrect mapid (mapid:{})'.format(mapid), None)

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
