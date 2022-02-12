# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import Creature, Korp

#
# Queries /internal/korp/*
#

# API: POST /internal/korp
def internal_korp_get_all():
    session = Session()

    try:
        korps = session.query(Korp)\
                       .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Korps query failed [{e}]',
                None)
    else:
        if korps:
            return (200,
                    True,
                    f'Korps found',
                    korps)
        else:
            return (200,
                    False,
                    f'Korps not found',
                    None)
    finally:
        session.close()

# API: POST /internal/korp
def internal_korp_get_one(korpid):
    session = Session()

    if not isinstance(korpid, int):
        return (200,
                False,
                f'Korp ID Malformed ({korpid})',
                None)

    try:
        korp    = session.query(Korp)\
                         .filter(Korp.id == korpid)\
                         .one_or_none()
        members = session.query(Creature)\
                         .filter(Creature.korp == korpid)\
                         .filter(Creature.korp_rank != 'Pending')\
                         .all()
        pending = session.query(Creature)\
                         .filter(Creature.korp == korpid)\
                         .filter(Creature.korp_rank == 'Pending')\
                         .all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Korp query failed (korpid:{korpid}) [{e}]',
                None)
    else:
        if korp:
            return (200,
                    True,
                    f'Korp found (korpid:{korpid})',
                    {"korp": korp, "members": members, "pending": pending})
        else:
            return (200,
                    False,
                    f'Korp not found (korpid:{korpid})',
                    None)
    finally:
        session.close()
