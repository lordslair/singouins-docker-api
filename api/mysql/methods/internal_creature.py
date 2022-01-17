# -*- coding: utf8 -*-

import dataclasses
import datetime

from ..session          import Session
from ..models           import PJ,Wallet,CreatureSlots,Item

from ..utils.redis      import *

from .fn_creature       import fn_creature_get,fn_creature_stats
from .fn_user           import fn_user_get_from_discord

#
# Queries /internal/creature/*
#
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
                f'PC unknown (creatureid:{creatureid})',
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
