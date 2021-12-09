# -*- coding: utf8 -*-

import dataclasses
import datetime

from ..session          import Session
from ..models           import PJ,Wallet,CreatureSlots,Item

from ..utils.redis      import *

from .fn_creature       import fn_creature_get,fn_creature_stats
from .fn_user           import fn_user_get_from_discord

#
# Queries /admin/mypc/*
#

# API: POST /admin/mypc
def admin_mypc_one(discordname,pcid):
    # Input checks
    if not isinstance(pcid, int):
        return (200,
                False,
                f'Bad PC id format (pcid:{pcid})',
                None)

    # Pre-flight checks
    pc          = fn_creature_get(None,pcid)[3]
    if pc is None:
        return (200,
                False,
                f'PC unknown (pcid:{pcid})',
                None)

    if discordname == 'Wukong':
        # We received an admin query (no Discorname to match)
        pass
    else:
        # We received an user query (with Discorname to match)
        if not isinstance(discordname, str):
            return (200,
                    False,
                    f'Bad Discordname format (discordname:{discordname})',
                    None)

        user        = fn_user_get_from_discord(discordname)
        if user is None:
            return (200,
                    False,
                    f'Discordname unknown (discordname:{discordname})',
                    None)
        if pc.account != user.id:
            return (409, False, 'Token/username mismatch', None)

    if pc:
        return (200,
                True,
                f'PC found (discordname:{discordname},pcid:{pcid})',
                pc)
    else:
        return (200,
                False,
                f'PC not found (discordname:{discordname},pcid:{pcid})',
                None)

# API: POST /admin/mypcs
def admin_mypc_all(discordname):

    if discordname == 'Wukong':
        # We received an admin query (no Discorname to match)
        pass
    else:
        # We received an user query (with Discorname to match)
        if not isinstance(discordname, str):
            return (200,
                    False,
                    f'Bad Discordname format (discordname:{discordname})',
                    None)

        user        = fn_user_get_from_discord(discordname)
        if user is None:
            return (200,
                    False,
                    f'Discordname unknown (discordname:{discordname})',
                    None)

    session = Session()
    try:
        pcs = session.query(PJ)\
                     .filter(PJ.account == user.id)\
                     .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] PCs query failed [{e}]',
                None)
    else:
        if pcs:
            return (200,
                    True,
                    f'PCs found (discordname:{discordname})',
                    pcs)
        else:
            return (200,
                    False,
                    f'PCs not found (discordname:{discordname})',
                    None)
    finally:
        session.close()

# API: POST /admin/mypc/pa
def admin_mypc_pa(discordname,pcid,redpa,bluepa):
    # Input checks
    if not isinstance(pcid, int):
        return (200,
                False,
                f'Bad PC id format (pcid:{pcid})',
                None)

    if not isinstance(discordname, str):
        return (200,
                False,
                f'Bad Discordname format (discordname:{discordname})',
                None)

    # Pre-flight checks
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get_from_discord(discordname)

    if user is None:
        return (200,
                False,
                f'Discordname unknown (discordname:{discordname})',
                None)
    if pc is None:
        return (200,
                False,
                f'PC unknown (pcid:{pcid})',
                None)

    if pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)


    if redpa is None and bluepa is None:
        # We have a GET PA request
        try:
            pa = get_pa(pcid)[3]
        except Exception as e:
            return (200,
                    False,
                    f'[Redis] PA query failed [{e}]',
                    None)
        else:
            if pa:
                return (200,
                        True,
                        f'PAs found (discordname:{discordname},pcid:{pcid})',
                        {"pa": pa,
                         "pc": pc})
            else:
                return (200,
                        False,
                        f'PAs not found (discordname:{discordname},pcid:{pcid})',
                        None)
    elif isinstance(redpa, int) or isinstance(bluepa, int):
        # We have a SET PA request
        # TODO: We only do a reset by laziness, could be better
        try:
            if isinstance(redpa, int):
                r.set(f'red:{pc.id}','red',ex=1)
            if isinstance(bluepa, int):
                r.set(f'blue:{pc.id}','blue',ex=1)
        except Exception as e:
            return (200,
                    False,
                    f'[Redis] PA query failed [{e}]',
                    None)
        else:
            return (200,
                    True,
                    f'PAs set successed (discordname:{discordname},pcid:{pcid})',
                    None)

# API: POST /admin/mypc/wallet
def admin_mypc_wallet(discordname,pcid):
    # Input checks
    if not isinstance(pcid, int):
        return (200,
                False,
                f'Bad PC id format (pcid:{pcid})',
                None)

    # Pre-flight checks
    pc          = fn_creature_get(None,pcid)[3]
    if pc is None:
        return (200,
                False,
                f'PC unknown (pcid:{pcid})',
                None)

    if discordname == 'Wukong':
        # We received an admin query (no Discorname to match)
        pass
    else:
        # We received an user query (with Discorname to match)
        if not isinstance(discordname, str):
            return (200,
                    False,
                    f'Bad Discordname format (discordname:{discordname})',
                    None)

        user        = fn_user_get_from_discord(discordname)
        if user is None:
            return (200,
                    False,
                    f'Discordname unknown (discordname:{discordname})',
                    None)
        if pc.account != user.id:
            return (409, False, 'Token/username mismatch', None)

    session = Session()
    try:
        wallet = session.query(Wallet)\
                        .filter(Wallet.id == pc.id)\
                        .one_or_none()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Wallet query failed [{e}]',
                None)
    else:
        if wallet:
            return (200,
                    True,
                    f'Wallet found (discordname:{discordname},pcid:{pcid})',
                    {"wallet": wallet,
                     "pc": pc})
        else:
            return (200,
                    False,
                    f'Wallet not found (discordname:{discordname},pcid:{pcid})',
                    None)
    finally:
        session.close()

# API: POST /admin/mypc/equipment
def admin_mypc_equipment(discordname,pcid):
    # Input checks
    if not isinstance(pcid, int):
        return (200,
                False,
                f'Bad PC id format (pcid:{pcid})',
                None)

    # Pre-flight checks
    pc          = fn_creature_get(None,pcid)[3]
    if pc is None:
        return (200,
                False,
                f'PC unknown (pcid:{pcid})',
                None)

    if discordname == 'Wukong':
        # We received an admin query (no Discorname to match)
        pass
    else:
        # We received an user query (with Discorname to match)
        if not isinstance(discordname, str):
            return (200,
                    False,
                    f'Bad Discordname format (discordname:{discordname})',
                    None)

        user        = fn_user_get_from_discord(discordname)
        if user is None:
            return (200,
                    False,
                    f'Discordname unknown (discordname:{discordname})',
                    None)
        if pc.account != user.id:
            return (409, False, 'Token/username mismatch', None)

    session = Session()

    try:
        slots = session.query(CreatureSlots)\
                       .filter(CreatureSlots.id == pc.id)\
                       .one_or_none()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Slots query failed (discordname:{discordname},pcid:{pc.id}) [{e}]',
                None)
    else:
        if slots is None or pc.account is None:
            equipment = {"feet": None,
                         "hands": None,
                         "head": None,
                         "holster": None,
                         "lefthand": None,
                         "righthand": None,
                         "shoulders": None,
                         "torso": None,
                         "legs": None}
        else:
            try:
                feet      = session.query(Item).filter(Item.id == slots.feet).one_or_none()
                hands     = session.query(Item).filter(Item.id == slots.hands).one_or_none()
                head      = session.query(Item).filter(Item.id == slots.head).one_or_none()
                holster   = session.query(Item).filter(Item.id == slots.holster).one_or_none()
                lefthand  = session.query(Item).filter(Item.id == slots.lefthand).one_or_none()
                righthand = session.query(Item).filter(Item.id == slots.righthand).one_or_none()
                shoulders = session.query(Item).filter(Item.id == slots.shoulders).one_or_none()
                torso     = session.query(Item).filter(Item.id == slots.torso).one_or_none()
                legs      = session.query(Item).filter(Item.id == slots.legs).one_or_none()

                if feet and isinstance(feet.date, datetime):
                    feet.date      = feet.date.strftime('%Y-%m-%d %H:%M:%S')
                    feet           = dataclasses.asdict(feet)
                if hands and isinstance(hands.date, datetime):
                    hands.date     = hands.date.strftime('%Y-%m-%d %H:%M:%S')
                    hands          = dataclasses.asdict(hands)
                if head and isinstance(head.date, datetime):
                    head.date      = head.date.strftime('%Y-%m-%d %H:%M:%S')
                    head           = dataclasses.asdict(head)
                if holster and isinstance(holster.date, datetime):
                    holster.date   = holster.date.strftime('%Y-%m-%d %H:%M:%S')
                    holster        = dataclasses.asdict(holster)
                if lefthand and isinstance(lefthand.date, datetime):
                    lefthand.date  = lefthand.date.strftime('%Y-%m-%d %H:%M:%S')
                    lefthand       = dataclasses.asdict(lefthand)
                if righthand and isinstance(righthand.date, datetime):
                    righthand.date = righthand.date.strftime('%Y-%m-%d %H:%M:%S')
                    righthand      = dataclasses.asdict(righthand)
                if shoulders and isinstance(shoulders.date, datetime):
                    shoulders.date = shoulders.date.strftime('%Y-%m-%d %H:%M:%S')
                    shoulders      = dataclasses.asdict(shoulders)
                if torso and isinstance(torso.date, datetime):
                    torso.date     = torso.date.strftime('%Y-%m-%d %H:%M:%S')
                    torso          = dataclasses.asdict(torso)
                if legs and isinstance(legs.date, datetime):
                    legs.date      = legs.date.strftime('%Y-%m-%d %H:%M:%S')
                    legs           = dataclasses.asdict(legs)

            except Exception as e:
                return (200,
                        False,
                        f'[SQL] Equipment query failed (discordname:{discordname},pcid:{pc.id}) [{e}]',
                        None)
            else:
                equipment = {"feet": feet,
                             "hands": hands,
                             "head": head,
                             "holster": holster,
                             "lefthand": lefthand,
                             "righthand": righthand,
                             "shoulders": shoulders,
                             "torso": torso,
                             "legs": legs}

        return (200,
                True,
                f'Equipment found (discordname:{discordname},pcid:{pc.id})',
                {"equipment": equipment,
                 "pc": pc})

    finally:
        session.close()


# API: POST /admin/mypc/effects
def admin_mypc_effects(discordname,pcid):
    # Input checks
    if not isinstance(pcid, int):
        return (200,
                False,
                f'Bad PC id format (pcid:{pcid})',
                None)

    # Pre-flight checks
    pc          = fn_creature_get(None,pcid)[3]
    if pc is None:
        return (200,
                False,
                f'PC unknown (pcid:{pcid})',
                None)

    if discordname == 'Wukong':
        # We received an admin query (no Discorname to match)
        pass
    else:
        # We received an user query (with Discorname to match)
        if not isinstance(discordname, str):
            return (200,
                    False,
                    f'Bad Discordname format (discordname:{discordname})',
                    None)

        user        = fn_user_get_from_discord(discordname)
        if user is None:
            return (200,
                    False,
                    f'Discordname unknown (discordname:{discordname})',
                    None)
        if pc.account != user.id:
            return (409, False, 'Token/username mismatch', None)

    # Effects fetching
    effects  = get_effects(pc)
    if effects:
        return (200,
                True,
                f'Effects found (discordname:{discordname},pcid:{pc.id})',
                {"effects": effects,
                 "pc": pc})
    else:
        return (200,
                False,
                f'Effects query failed (discordname:{discordname},pcid:{pc.id})',
                None)

# API: POST /admin/mypc/statuses
def admin_mypc_statuses(discordname,pcid):
    # Input checks
    if not isinstance(pcid, int):
        return (200,
                False,
                f'Bad PC id format (pcid:{pcid})',
                None)

    # Pre-flight checks
    pc          = fn_creature_get(None,pcid)[3]
    if pc is None:
        return (200,
                False,
                f'PC unknown (pcid:{pcid})',
                None)

    if discordname == 'Wukong':
        # We received an admin query (no Discorname to match)
        pass
    else:
        # We received an user query (with Discorname to match)
        if not isinstance(discordname, str):
            return (200,
                    False,
                    f'Bad Discordname format (discordname:{discordname})',
                    None)

        user        = fn_user_get_from_discord(discordname)
        if user is None:
            return (200,
                    False,
                    f'Discordname unknown (discordname:{discordname})',
                    None)
        if pc.account != user.id:
            return (409, False, 'Token/username mismatch', None)

    # Statuese fetching
    statuses  = get_statuses(pc)
    if statuses:
        return (200,
                True,
                f'Statuses found (discordname:{discordname},pcid:{pc.id})',
                {"statuses": statuses,
                 "pc": pc})
    else:
        return (200,
                False,
                f'Statuses query failed (discordname:{discordname},pcid:{pc.id})',
                None)

# API: POST /admin/mypc/stats
def admin_mypc_stats(discordname,pcid):
    # Input checks
    if not isinstance(pcid, int):
        return (200,
                False,
                f'Bad PC id format (pcid:{pcid})',
                None)

    # Pre-flight checks
    pc          = fn_creature_get(None,pcid)[3]
    if pc is None:
        return (200,
                False,
                f'PC unknown (pcid:{pcid})',
                None)

    if discordname == 'Wukong':
        # We received an admin query (no Discorname to match)
        pass
    else:
        # We received an user query (with Discorname to match)
        if not isinstance(discordname, str):
            return (200,
                    False,
                    f'Bad Discordname format (discordname:{discordname})',
                    None)

        user        = fn_user_get_from_discord(discordname)
        if user is None:
            return (200,
                    False,
                    f'Discordname unknown (discordname:{discordname})',
                    None)
        if pc.account != user.id:
            return (409, False, 'Token/username mismatch', None)

    # We force stats re-compute
    stats = fn_creature_stats(pc)
    if stats:
        # Data was computed, so we return it
        return (200,
                True,
                f'Stats computation successed (pcid:{pc.id})',
                {"stats": stats,
                 "pc": pc})
    else:
        return (200,
                False,
                f'Stats query failed (discordname:{discordname},pcid:{pc.id})',
                None)
