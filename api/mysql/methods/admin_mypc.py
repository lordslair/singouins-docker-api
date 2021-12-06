# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import PJ,Wallet

from ..utils.redis      import *

from .fn_creature       import fn_creature_get
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
