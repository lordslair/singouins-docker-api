# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get
from .fn_global         import clog

#
# Queries /mypc/{pcid}/item/*
#

def mypc_items_get(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc.account is None:
        return (200,
                False,
                f'NPCs do not have items (pcid:{pc.id})',
                None)

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    try:
        weapon    = session.query(Item)\
                           .filter(Item.bearer == pc.id)\
                           .filter(Item.metatype == 'weapon')\
                           .all()
        armor     = session.query(Item)\
                           .filter(Item.bearer == pc.id)\
                           .filter(Item.metatype == 'armor')\
                           .all()
        equipment = session.query(CreatureSlots)\
                           .filter(CreatureSlots.id == pc.id)\
                           .all()
        cosmetic  = session.query(Cosmetic)\
                           .filter(Cosmetic.bearer == pc.id)\
                           .all()
        wallet    = session.query(Wallet)\
                           .filter(Wallet.id == pc.id)\
                           .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Equipment query failed (pcid:{pc.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'Equipment query successed (pcid:{pc.id})',
                {"weapon": weapon,
                 "armor": armor,
                 "equipment": equipment,
                 "cosmetic": cosmetic,
                 "wallet": wallet})
    finally:
        session.close()
