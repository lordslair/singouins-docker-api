# -*- coding: utf8 -*-

from ..utils.redis      import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get_from_discord

#
# Queries /admin/squad/*
#

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
