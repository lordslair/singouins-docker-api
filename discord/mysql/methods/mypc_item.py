# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *

from .fn_user           import *
from .fn_creature       import *

def query_mypc_items_get(pcid,member):
    session  = Session()
    user     = fn_user_get_from_member(member)
    pc       = fn_creature_get(None,pcid)[3]

    if not user:
        return (200,
                False,
                '[SQL] User query failed (member:{})'.format(member),
                None)

    if not pc:
        return (200,
                False,
                '[SQL] PC query failed (member:{})'.format(member),
                None)

    if pc.account is None:
        return (200, False, 'NPCs do not have items (pcid:{})'.format(pc.id), None)

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
        # Something went wrong during query
        return (200,
                False,
                '[SQL] Equipment query failed (pcid:{})'.format(pc.id),
                None)
    else:
        return (200,
                True,
                'Equipment query successed (pcid:{})'.format(pc.id),
                {"weapon": weapon,
                 "armor": armor,
                 "equipment": equipment,
                 "cosmetic": cosmetic,
                 "wallet": wallet})
    finally:
        session.close()
