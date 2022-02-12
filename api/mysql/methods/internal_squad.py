# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import Creature, Squad

#
# Queries /internal/squad/*
#

# API: POST /internal/squad
def internal_squad_get_all():
    session = Session()

    try:
        squads = session.query(Squad)\
                       .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Squads query failed [{e}]',
                None)
    else:
        if squads:
            return (200,
                    True,
                    f'Squads found',
                    squads)
        else:
            return (200,
                    False,
                    f'Squads not found',
                    None)
    finally:
        session.close()

# API: POST /internal/squad
def internal_squad_get_one(squadid):
    session = Session()

    try:
        squad = session.query(Squad)\
                       .filter(Squad.id == squadid)\
                       .one_or_none()
        members = session.query(Creature)\
                         .filter(Creature.squad == squadid)\
                         .filter(Creature.squad_rank != 'Pending')\
                         .all()
        pending = session.query(Creature)\
                         .filter(Creature.squad == squadid)\
                         .filter(Creature.squad_rank == 'Pending')\
                         .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Squad query failed (squadid:{squadid}) [{e}]',
                None)
    else:
        if squad:
            return (200,
                    True,
                    f'Squad found (squadid:{squadid})',
                    {"squad": squad, "members": members, "pending": pending})
        else:
            return (200,
                    False,
                    f'Squad not found (squadid:{squadid})',
                    None)
    finally:
        session.close()
