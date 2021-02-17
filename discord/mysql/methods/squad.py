# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

from .fn_user           import *
from .fn_creature       import *

def query_squads_get(member):
    session  = Session()
    user     = fn_user_get_from_member(member)

    if not user:
        return (200,
                False,
                '[SQL] User query failed (member:{})'.format(member),
                None)

    try:
        pcs    = session.query(Creature).filter(Creature.account == user.id).all()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                '[SQL] PCs query failed (username:{})'.format(user.name),
                None)
    else:
        if not pcs:
            return (200,
                    False,
                    'No PC found for this user (username:{})'.format(user.name),
                    None)
        leader = []
        member = []
        for pc in pcs:
            if pc.squad_rank == 'Leader' and pc.squad > 0:
                leader.append(pc.squad)
            elif pc.squad_rank == 'Member' and pc.squad > 0:
                member.append(pc.squad)

        return (200,
                True,
                'Squads found for this user (username:{})'.format(user.name),
                {"leader": leader, "member": member})
    finally:
        session.close()
