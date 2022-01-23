# -*- coding: utf8 -*-

import dataclasses
import datetime

from ..session              import Session
from ..models               import CreatureSlots,Item,PJ,Wallet

from ..utils.redis.effects  import *
from ..utils.redis.cds      import *
from ..utils.redis.statuses import *
from ..utils.redis.pa       import *

from .fn_creature           import fn_creature_get,fn_creature_stats
from .fn_user               import fn_user_get_from_discord

#
# Queries /internal/creature/*
#
# API: POST /internal/creature/cds
def internal_creature_cds(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    # CDs fetching
    cds  = get_cds(creature)
    if isinstance(cds, list):
        return (200,
                True,
                f'CDs found (creatureid:{creature.id})',
                {"cds": cds,
                 "creature": creature})
    else:
        return (200,
                False,
                f'CDs query failed (creatureid:{creature.id})',
                None)

# API: POST /internal/creature/{creatureid}/effects
def internal_creature_effects(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    # Effects fetch
    effects  = get_effects(creature)
    if isinstance(effects, list):
        return (200,
                True,
                f'Effects found (creatureid:{creature.id})',
                {"effects": effects,
                 "creature": creature})
    else:
        return (200,
                False,
                f'Effects query failed (creatureid:{creature.id})',
                None)

# API: PUT /internal/creature/effects
def internal_creature_effects_add(creatureid,duration,effectname,sourceid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)
    if not isinstance(duration, int):
        return (200,
                False,
                f'Bad Duration format (duration:{duration})',
                None)
    if not isinstance(effectname, str):
        return (200,
                False,
                f'Bad Effect name format (effectname:{effectname})',
                None)
    if not isinstance(sourceid, int):
        return (200,
                False,
                f'Bad Source id format (sourceid:{sourceid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)
    source      = fn_creature_get(None,sourceid)[3]
    if source is None:
        return (200,
                False,
                f'Creature unknown (sourceid:{sourceid})',
                None)

    # Effect add
    effect  = add_effect(creature,duration,effectname,source)
    effects = get_effects(creature)
    if effect:
        return (200,
                True,
                f'Effect add successed (creatureid:{creature.id})',
                {"effects": effects,
                 "creature": creature})
    else:
        return (200,
                False,
                f'Effects add failed (creatureid:{creature.id})',
                None)

# API: DELETE /internal/creature/effect/{effectid}
def internal_creature_effects_del(effectid):
    # Input checks
    if not isinstance(effectid, int):
        return (200,
                False,
                f'Bad Effect id format (effectid:{effectid})',
                None)

    # Effect delete
    effect  = del_effect(effectid)
    if effect > 0:
        return (200,
                True,
                f'Effect del successed (effectid:{effectid})',
                None)
    elif effect == 0:
        return (200,
                False,
                f'Effect not found (effectid:{effectid})',
                None)
    else:
        return (200,
                False,
                f'Effect del failed (effectid:{effectid})',
                None)

# API: POST /internal/creature/equipment
def internal_creature_equipment(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    session = Session()

    try:
        slots = session.query(CreatureSlots)\
                       .filter(CreatureSlots.id == creature.id)\
                       .one_or_none()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Slots query failed (creatureid:{creature.id}) [{e}]',
                None)
    else:
        if slots is None or creature.account is None:
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

                if feet and isinstance(feet.date, datetime.datetime):
                    feet.date      = feet.date.strftime('%Y-%m-%d %H:%M:%S')
                    feet           = dataclasses.asdict(feet)
                if hands and isinstance(hands.date, datetime.datetime):
                    hands.date     = hands.date.strftime('%Y-%m-%d %H:%M:%S')
                    hands          = dataclasses.asdict(hands)
                if head and isinstance(head.date, datetime.datetime):
                    head.date      = head.date.strftime('%Y-%m-%d %H:%M:%S')
                    head           = dataclasses.asdict(head)
                if holster and isinstance(holster.date, datetime.datetime):
                    holster.date   = holster.date.strftime('%Y-%m-%d %H:%M:%S')
                    holster        = dataclasses.asdict(holster)
                if lefthand and isinstance(lefthand.date, datetime.datetime):
                    lefthand.date  = lefthand.date.strftime('%Y-%m-%d %H:%M:%S')
                    lefthand       = dataclasses.asdict(lefthand)
                if righthand and isinstance(righthand.date, datetime.datetime):
                    righthand.date = righthand.date.strftime('%Y-%m-%d %H:%M:%S')
                    righthand      = dataclasses.asdict(righthand)
                if shoulders and isinstance(shoulders.date, datetime.datetime):
                    shoulders.date = shoulders.date.strftime('%Y-%m-%d %H:%M:%S')
                    shoulders      = dataclasses.asdict(shoulders)
                if torso and isinstance(torso.date, datetime.datetime):
                    torso.date     = torso.date.strftime('%Y-%m-%d %H:%M:%S')
                    torso          = dataclasses.asdict(torso)
                if legs and isinstance(legs.date, datetime.datetime):
                    legs.date      = legs.date.strftime('%Y-%m-%d %H:%M:%S')
                    legs           = dataclasses.asdict(legs)

            except Exception as e:
                return (200,
                        False,
                        f'[SQL] Equipment query failed (creatureid:{creature.id}) [{e}]',
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
                f'Equipment found (creatureid:{creature.id})',
                {"equipment": equipment,
                 "creature": creature})

    finally:
        session.close()

# API: POST /internal/creature/pa
def internal_creature_pa(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    try:
        pa = get_pa(creature.id)[3]
    except Exception as e:
        return (200,
                False,
                f'[Redis] PA query failed (creatureid:{creature.id}) [{e}]',
                None)
    else:
        if pa:
            return (200,
                    True,
                    f'PAs found (creatureid:{creature.id})',
                    {"pa": pa,
                     "creature": creature})
        else:
            return (200,
                    False,
                    f'PAs not found (creatureid:{creature.id})',
                    None)

# API: POST /internal/creature/pa/reset
def internal_creature_pa_reset(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    # TODO: We only do a reset by laziness, could be better
    try:
        r.set(f'red:{creature.id}','red',ex=1)
        r.set(f'blue:{creature.id}','blue',ex=1)
    except Exception as e:
        return (200,
                False,
                f'[Redis] PA query failed (creatureid:{creature.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'PAs set successed (creatureid:{creature.id})',
                None)

# API: POST /internal/creature/profile
def internal_creature_profile(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)
    else:
        return (200,
                True,
                f'Creature found (creatureid:{creatureid})',
                creature)

# API: POST /internal/creature/stats
def internal_creature_stats(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    # We force stats re-compute
    stats = fn_creature_stats(creature)
    if stats:
        # Data was computed, so we return it
        return (200,
                True,
                f'Stats computation successed (creatureid:{creature.id})',
                {"stats": stats,
                 "creature": creature})
    else:
        return (200,
                False,
                f'Stats query failed (creatureid:{creature.id})',
                None)

# API: POST /internal/creature/statuses
def internal_creature_statuses(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    # Statuese fetching
    statuses  = get_statuses(creature)
    if isinstance(statuses, list):
        return (200,
                True,
                f'Statuses found (creatureid:{creatureid})',
                {"statuses": statuses,
                 "creature": creature})
    else:
        return (200,
                False,
                f'Statuses query failed (creatureid:{creatureid})',
                None)

# API: POST /internal/creature/wallet
def internal_creature_wallet(creatureid):
    # Input checks
    if not isinstance(creatureid, int):
        return (200,
                False,
                f'Bad Creature id format (creatureid:{creatureid})',
                None)

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return (200,
                False,
                f'Creature unknown (creatureid:{creatureid})',
                None)

    session = Session()
    try:
        wallet = session.query(Wallet)\
                        .filter(Wallet.id == creature.id)\
                        .one_or_none()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Wallet query failed (creatureid:{creature.id}) [{e}]',
                None)
    else:
        if wallet:
            return (200,
                    True,
                    f'Wallet found (creatureid:{creature.id})',
                    {"wallet": wallet,
                     "creature": creature})
        else:
            return (200,
                    False,
                    f'Wallet not found (creatureid:{creature.id})',
                    None)
    finally:
        session.close()
