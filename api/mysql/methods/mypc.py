# -*- coding: utf8 -*-

from random                import randint

from ..session             import Session
from ..models              import (Cosmetic,
                                   Creature,
                                   CreatureSlots,
                                   CreatureStats,
                                   Item,
                                   Wallet)

from .fn_creature          import *
from .fn_user              import fn_user_get

# Loading the Meta for later use
try:
    metaRaces   = metas.get_meta('race')
    metaWeapons = metas.get_meta('weapon')
except Exception as e:
    logger.error(f'Meta fectching: KO [{e}]')
else:
    logger.trace(f'Meta fectching: OK')

#
# Queries /mypc/*
#
# API: GET /mypc/<int:pcid>/stats
def mypc_get_stats(pc):

    # We check if we have the data in redis
    creature_stats = stats.get_stats(pc)
    if creature_stats:
        # Data was in Redis, so we return it
        return (200,
                True,
                f'Stats Redis query successed (pcid:{pc.id})',
                creature_stats)

    # Data was not in Redis, so we compute it
    creature_stats = fn_creature_stats(pc)
    if creature_stats:
        # Data was computed, so we return it
        return (200,
                True,
                f'Stats computation successed (pcid:{pc.id})',
                creature_stats)
    else:
        # Data computation failed
        return (200,
                False,
                f'Stats computation failed (pcid:{pc.id})',
                None)

# API: GET /mypc/<int:pcid>/cds
def mypc_get_cds(username,pcid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()

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
        creature_cds = cds.get_cds(pc)
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[Redis] CDs query failed (pcid:{pc.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'CDs found (pcid:{pc.id})',
                creature_cds)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>/effects
def mypc_get_effects(username,pcid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)

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
        creature_effects = effects.get_effects(pc)
    except Exception as e:
        return (200,
                False,
                f'[Redis] Effects query failed (pcid:{pc.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'Effects found (pcid:{pc.id})',
                creature_effects)
