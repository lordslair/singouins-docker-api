# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get
from .fn_global         import clog

#
# Queries /mypc/{pcid}/trade/*
#

# API: /mypc/<int:pcid>/trade/item/<int:itemid>/give/<int:targetid>
def mypc_trade_item_give(username,pcid,itemid,targetid):
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

# API: /mypc/<int:pcid>/trade/wallet/<str:currtype>/give/<int:targetid>/<int:amount>
def mypc_trade_wallet_give(username,pcid,currtype,targetid,amount):
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

    pcwallet = session.query(Wallet)\
                      .filter(Wallet.id == pc.id)\
                      .one_or_none()
    tgwallet = session.query(Wallet)\
                      .filter(Wallet.id == tg.id)\
                      .one_or_none()

    if pcwallet is None or tgwallet is None:
        # Wallet not found
        return (200,
                False,
                'Wallet not found (pcid:{},targetid:{})'.format(pcid,targetid),
                None)

    try:
        if currtype == 'currency':
            if pcwallet.currency < amount:
                return (200,
                        False,
                        'Not enough in Wallet (pcid:{},amount:{})'.format(pc.id,amount),
                        None)
            else:
                pcwallet.currency -= amount
                tgwallet.currency += amount
        else:
            return (200,
                    False,
                    'Only currency is giveable (pcid:{},currtype:{})'.format(pc.id,currtype),
                    None)
        session.commit()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                '[SQL] Wallet update failed (pcid:{},targetid:{},currtype:{})'.format(pc.id,tg.id,currtype),
                None)
    else:
        tgwallet = session.query(Wallet)\
                          .filter(Wallet.id == tg.id)\
                          .one_or_none()
        return (200,
                True,
                'Item transfered successfully (pcid:{},targetid:{},currtype:{})'.format(pc.id,tg.id,currtype),
                tgwallet)
    finally:
        session.close()
