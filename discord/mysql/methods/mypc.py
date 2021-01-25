# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

from .fn_user           import *
from .fn_creature       import *

def query_pcs_get(member):
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
        if pcs:
            return (200,
                    True,
                    'PCs successfully found (username:{})'.format(user.name),
                    pcs)
        else:
            return (200,
                    False,
                    'No PC found for this user (username:{})'.format(user.name),
                    None)
    finally:
        session.close()

def query_pc_get(pcid,member):
    session  = Session()
    user     = fn_user_get_from_member(member)
    pc       = fn_creature_get(None,pcid)[3]

    if not user:
        return (200,
                False,
                '[SQL] User query failed (member:{})'.format(member),
                None)

    if not pc:
        return (200,
                False,
                '[SQL] PC query failed (member:{})'.format(member),
                None)

    if pc.account != user.id:
        return (200,
                False,
                'No PC found for this user (userid:{},pcid:{})'.format(user.id,pcid),
                None)
    else:
        return (200,
                True,
                'PCs successfully found (userid:{},pcid:{})'.format(user.id,pc.id),
                pc)
