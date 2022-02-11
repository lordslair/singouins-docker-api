# -*- coding: utf8 -*-

import textwrap

from ..session          import Session
from ..models           import MP, Creature

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get

#
# Queries /mypc/{pcid}/mp/*
#

# API: POST /mypc/<int:pcid>/mp
def mypc_mp_add(username,pcsrcid,dsts,subject,body):
    pcsrc   = fn_creature_get(None,pcsrcid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if pcsrc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pcsrc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    for pcdstid in dsts:
        pcdst   = fn_creature_get(None,pcdstid)[3]
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
        session.rollback()
        return (200,
                False,
                f'[SQL] MP creation failed (srcid:{pcsrc.id},dstid:{dsts}) [{e}]',
                None)
    else:
        return (201,
                True,
                f'MP creation successed (srcid:{pcsrc.id},dstid:{pcdst.id})',
                None)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>/mp/<int:mpid>
def mypc_mp_get(username,pcid,mpid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    try:
        mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[SQL] MP query failed (pcid:{pc.id},mpid:{mpid})',
                None)
    else:
        if mp:
            return (200,
                    True,
                    f'MP query successed (pcid:{pc.id},mpid:{mpid})',
                    mp)
        else:
            return (200, True, f'MP not found (pcid:{pc.id},mpid:{mpid})', None)
    finally:
        session.close()

# API: DELETE /mypc/<int:pcid>/mp/<int:mpid>
def mypc_mp_del(username,pcid,mpid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    try:
        mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
        if not mp: return (200, False, f'No MP found for this PC (pcid:{pc.id})', None)
        session.delete(mp)
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200, False, f'[SQL] MP deletion failed (pcid:{pc.id},mpid:{mpid})', None)
    else:
        return (200, True, f'MP deletion successed (pcid:{pc.id},mpid:{mpid})', None)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>/mp
def mypc_mps_get(username,pcid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    try:
        mps = session.query(MP).filter(MP.dst_id == pc.id).all()
    except Exception as e:
        # Something went wrong during commit
        return (200, False, f'[SQL] MPs query failed (pcid:{pc.id})', None)
    else:
        if mps:
            for mp in mps: mp.body = textwrap.shorten(mp.body, width=50, placeholder="...")
            return (200, True, f'MPs query successed (pcid:{pc.id})', mps)
        else:
            return (200, True, f'No MP found (pcid:{pc.id})', None)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>/mp/addressbook
def mypc_mp_addressbook(username,pcid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    try:
        addressbook = session.query(Creature)\
                             .filter(Creature.race < 10)\
                             .with_entities(Creature.id,Creature.name).all()
    except Exception as e:
        # Something went wrong during commit
        return (200, False, f'[SQL] Addressbook query failed (pcid:{pc.id})', None)
    else:
        if addressbook:
            return (200, True, f'Addressbook query successed (pcid:{pc.id})', addressbook)
        else:
            return (200, True, f'No Addressbook found (pcid:{pc.id})', None)
    finally:
        session.close()
