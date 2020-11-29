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

def mypc_item_dismantle(username,pcid,itemid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    item = session.query(Item).filter(Item.id == itemid).one_or_none()

    if item:
        if   item.rarity == 'Broken':
            shards = [6,0,0,0,0,0]
        elif item.rarity == 'Common':
            shards = [0,5,0,0,0,0]
        elif item.rarity == 'Uncommon':
            shards = [0,0,4,0,0,0]
        elif item.rarity == 'Rare':
            shards = [0,0,0,3,0,0]
        elif item.rarity == 'Epic':
            shards = [0,0,0,0,2,0]
        elif item.rarity == 'Legendary':
            shards = [0,0,0,0,0,1]

        try:
            wallet = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()

            wallet.broken    += shards[0]
            wallet.common    += shards[1]
            wallet.uncommon  += shards[2]
            wallet.rare      += shards[3]
            wallet.epic      += shards[4]
            wallet.legendary += shards[5]

            session.delete(item)

            session.commit()
        except Exception as e:
            # Something went wrong during query
            return (200,
                    False,
                    '[SQL] Wallet update failed (pcid:{})'.format(pc.id),
                    None)
        else:
            return (200,
                    True,
                    'Item dismantle successed (pcid:{},itemid:{})'.format(pc.id,item.id),
                    {"shards": {
                        "Broken":    shards[0],
                        "Common":    shards[1],
                        "Uncommon":  shards[2],
                        "Rare":      shards[3],
                        "Epic":      shards[4],
                        "Legendary": shards[5]}
                    })
        finally:
            session.close()

    else:
        return (200,
                False,
                'Item do not exist (pcid:{},itemid:{})'.format(pc.id,itemid),
                None)

def mypc_items_get(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

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
