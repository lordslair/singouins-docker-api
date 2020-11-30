# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get
from .fn_global         import clog

#
# Queries /mypc/{pcid}/action/*
#

def mypc_action_item_give(username,pcid,itemid,targetid):
    pc      = fn_creature_get(None,pcid)[3]
    tg      = fn_creature_get(None,targetid)[3]
    user    = fn_user_get(username)
    session = Session()

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    if tg is None:
        return (200,
                False,
                'Target not found (pcid:{},targetid:{})'.format(pcid,targetid),
                None)
    elif tg.account is None:
        return (200,
                False,
                'Target is an NPC (pcid:{},targetid:{})'.format(pcid,targetid),
                None)

    if abs(pc.x - tg.x) > 1 or abs(pc.y - tg.y) > 1:
        # Target is too far
        return (200,
                False,
                'Target is too far (pcid:{},targetid:{})'.format(pcid,targetid),
                None)

    item = session.query(Item)\
                  .filter(Item.id == itemid)\
                  .filter(Item.bearer == pc.id)\
                  .filter(Item.bound_type == 'BoE')\
                  .filter(Item.bound == False)\
                  .one_or_none()

    if item is None:
        # Item not found
        return (200,
                False,
                'Item not found / not givable (pcid:{},itemid:{})'.format(pcid,itemid),
                None)

    try:
        item.bearer = tg.id
        session.commit()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                '[SQL] Item update failed (pcid:{},targetid:{},itemid:{})'.format(pc.id,tg.id,item.id),
                None)
    else:
        return (200,
                True,
                'Item transfered successfully (pcid:{},targetid:{},itemid:{})'.format(pc.id,tg.id,item.id),
                item)
    finally:
        session.close()

def mypc_action_item_dismantle(username,pcid,itemid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    item = session.query(Item)\
                  .filter(Item.id == itemid)\
                  .one_or_none()

    if item is None:
        # Item not found
        return (200,
                False,
                'Item not found (pcid:{},itemid:{})'.format(pcid,itemid),
                None)

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
