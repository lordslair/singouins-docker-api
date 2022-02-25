# -*- coding: utf8 -*-

import dataclasses

from ..session           import Session
from ..models            import Creature,Korp

from .fn_creature        import *
from .fn_user            import fn_user_get

#
# Queries /mypc/<int:pcid>/korp/*
#

# API: GET /mypc/<int:pcid>/korp/<int:korpid>
def mypc_korp_details(username,pcid,korpid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

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
    if pc.korp != korpid:
        return (200,
                False,
                f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                None)

    # Let's get the korp from DB
    try:
        korp = session.query(Korp)\
                      .filter(Korp.id == pc.korp)\
                      .filter(Creature.id == pc.id)

        pc_is_member  = korp.filter(Creature.korp_rank != 'Pending').one_or_none()
        pc_is_pending = korp.filter(Creature.korp_rank == 'Pending').one_or_none()

        if pc_is_member:
            korp    = korp.session.query(Korp).filter(Korp.id == pc.korp).one_or_none()
            members = session.query(Creature)\
                             .filter(Creature.korp == korp.id)\
                             .filter(Creature.korp_rank != 'Pending')\
                             .all()
            pending = session.query(Creature)\
                             .filter(Creature.korp == korp.id)\
                             .filter(Creature.korp_rank == 'Pending')\
                             .all()
        elif pc_is_pending:
            korp   = korp.session.query(Korp).filter(Korp.id == pc.korp).one_or_none()

    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                f'[SQL] Korp query failed (pcid:{pcid},korpid:{korpid}) [{e}]',
                None)
    else:
        if pc_is_member:
            if korp:
                if isinstance(members, list):
                    if isinstance(pending, list):
                        return (200,
                                True,
                                f'Korp query successed (pcid:{pcid},korpid:{korpid})',
                                {"korp": korp, "members": members, "pending": pending})
        elif pc_is_pending:
            return (200,
                    True,
                    f'PC is pending in a korp (pcid:{pcid},korpid:{korpid})',
                    {"korp": korp})
        else:
            return (200,
                    False,
                    f'PC is not in a korp (pcid:{pcid},korpid:{korpid})',
                    None)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/korp
def mypc_korp_create(username,pcid,korpname):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

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
    # Remove everything, except alphanumeric, space, squote
    korpname = ''.join([c for c in korpname if c.isalnum() or c in [" ","'"]])
    # Size check
    if len(korpname) > 16:
        return (200,
                False,
                f'Korp name too long (korpname:{korpname})',
                None)
    # Unicity test
    if session.query(Korp).filter(Korp.name == korpname).one_or_none():
        return (409,
                False,
                f'Korp already exists (korpname:{korpname})',
                None)
    if pc.korp is not None:
        return (200,
                False,
                f'PC already in a korp (pcid:{pc.id},korpid:{pc.korp})',
                None)

    korp = Korp(leader = pc.id,
                name   = korpname)
    session.add(korp)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Korp creation failed (pcid:{pcid},korpname:{korpname}) [{e}]',
                None)

    # Korp created, let's assign the team creator in the korp
    pc           = session.query(Creature)\
                          .filter(Creature.id == pcid)\
                          .one_or_none()
    korp         = session.query(Korp)\
                          .filter(Korp.leader == pc.id)\
                          .one_or_none()
    pc.korp      = korp.id
    pc.korp_rank = 'Leader'

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Korp leader assignation failed (pcid:{pc.id},korpid:{korp.id}) [{e}]',
                None)
    else:
        try:
            korp_members    = []
            members         = session.query(Creature)\
                                     .filter(Creature.korp == pc.korp)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                korp_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** created this Korp',
                    "embed": None,
                    "scope": f'Korp-{pc.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp_members,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', qmsg)
            return (201,
                    True,
                    f'Korp successfully created (pcid:{pc.id},korpid:{korp.id})',
                    korp)
    finally:
        session.close()

# API: DELETE /mypc/<int:pcid>/korp/<int:korpid>
def mypc_korp_delete(username,leaderid,korpid):
    leader  = fn_creature_get(None,leaderid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if leader is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if leader.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)
    # Rank checks
    if leader.korp != korpid:
        return (200,
                False,
                f'Korp request outside of your scope ({leader.korp} =/= {korpid})',
                None)
    if leader.korp_rank != 'Leader':
        return (200,
                False,
                f'PC is not the korp Leader (pcid:{leader.id},korprank:{leader.korp_rank})',
                None)

    korp = session.query(Korp).filter(Korp.leader == leader.id).one_or_none()
    if korp is None:
        return (200,
                False,
                f'Korp not found (pcid:{leader.id},korpid:{korpid})',
                None)

    count = session.query(Creature).filter(Creature.korp == korp.id).count()
    if count > 1:
        return (200,
                False,
                f'Korp not empty (korpid:{korp.id},members:{count})',
                None)

    try:
        # We delete the Korp
        session.delete(korp)
        # We empty Korp fields for the Leader
        leader           = session.query(Creature)\
                                  .filter(Creature.id == leaderid)\
                                  .one_or_none()
        leader.korp      = None
        leader.korp_rank = None
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Korp deletion failed (korpid:{korp.id}) [{e}]',
                None)
    else:
        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": f':information_source: **[{leader.id}] {leader.name}** deleted this korp',
                "embed": None,
                "scope": f'Korp-{korp.id}'}
        queue.yqueue_put('yarqueue:discord', qmsg)
        # We put the info in queue for ws Front
        qmsg = {"ciphered": False,
                "payload": None,
                "route": 'mypc/{id1}/korp',
                "scope": 'korp'}
        queue.yqueue_put('broadcast', qmsg)

        return (200,
                True,
                f'Korp successfully deleted (korpid:{korpid})',
                None)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/korp/<int:korpid>/invite/<int:targetid>
def mypc_korp_invite(username,leaderid,korpid,targetid):
    target  = fn_creature_get(None,targetid)[3]
    leader  = fn_creature_get(None,leaderid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if leader is None:
        return (200,
                False,
                f'PC not found (leaderid:{leaderid})',
                None)
    if target is None:
        return (200,
                False,
                f'PC not found (targetid:{targetid})',
                None)
    if leader.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (leaderid:{leaderid},username:{username})',
                None)
    # Rank checks
    if leader.korp != korpid:
        return (200,
                False,
                f'Korp request outside of your scope ({leader.korp} =/= {korpid})',
                None)
    if leader.korp_rank != 'Leader':
        return (200,
                False,
                f'PC is not the korp Leader (pcid:{leader.id},korprank:{leader.korp_rank})',
                None)
    if target.korp is not None:
        return (200,
                False,
                f'PC invited is already in a korp (pcid:{target.id},korpid:{target.korp})',
                None)
    # Korp population check
    members    = session.query(Creature)\
                        .filter(Creature.korp == leader.korp)\
                        .all()
    maxmembers = 100
    if len(members) == maxmembers:
        return (200,
                False,
                f'Korp is already full (slots:{len(members)}/{maxmembers})',
                None)

    try:
        pc           = session.query(Creature)\
                              .filter(Creature.id == target.id)\
                              .one_or_none()
        pc.korp      = leader.korp
        pc.korp_rank = 'Pending'
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] PC Invite failed (targetid:{targetid}) [{e}]',
                None)
    else:
        try:
            korp_members    = []
            members         = session.query(Creature)\
                                     .filter(Creature.korp == pc.korp)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                korp_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{leader.id}] {leader.name}** invited **[{target.id}] {target.name}** in this korp',
                    "embed": None,
                    "scope": f'Korp-{leader.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp_members,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC Invite successed (slots:{len(members)}/{maxmembers})',
                    korp_members)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/korp/<int:korpid>/kick/<int:targetid>
def mypc_korp_kick(username,leaderid,korpid,targetid):
    target  = fn_creature_get(None,targetid)[3]
    leader  = fn_creature_get(None,leaderid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if leader is None:
        return (200,
                False,
                f'PC not found (leaderid:{leaderid})',
                None)
    if target is None:
        return (200,
                False,
                f'PC not found (targetid:{targetid})',
                None)
    if leader.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (leaderid:{leaderid},username:{username})',
                None)
    # Rank checks
    if leader.korp != korpid:
        return (200,
                False,
                f'Korp request outside of your scope ({leader.korp} =/= {korpid})',
                None)
    if leader.korp_rank != 'Leader':
        return (200,
                False,
                f'PC is not the korp Leader (pcid:{leader.id},korprank:{leader.korp_rank})',
                None)
    if target.korp is None:
        return (200,
                False,
                f'PC have to be in a korp (pcid:{target.id},korpid:{target.korp})',
                None)
    if leader.id == targetid:
        return (200,
                False,
                f'PC target cannot be the korp Leader (leaderid:{leaderid},targetid:{targetid})',
                None)
    # Korp population check
    maxmembers = 100

    try:
        pc           = session.query(Creature)\
                              .filter(Creature.id == target.id)\
                              .one_or_none()
        pc.korp      = None
        pc.korp_rank = None
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] PC Kick failed (pcid:{target.id},korpid:{target.korp}) [{e}]',
                None)
    else:
        try:
            korp_members    = []
            members         = session.query(Creature)\
                                     .filter(Creature.korp == pc.korp)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                korp_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws Discord
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{leader.id}] {leader.name}** kicked **[{target.id}] {target.name}** from this korp',
                    "embed": None,
                    "scope": f'Korp-{leader.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp_members,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC Kick successed (slots:{len(members)}/{maxmembers})',
                    korp_members)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/korp/<int:korpid>/accept
def mypc_korp_accept(username,pcid,korpid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pc.id},username:{username})',
                None)
    if pc.korp != korpid:
        return (200,
                False,
                f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                None)
    if pc.korp_rank != 'Pending':
        return (200,
                False,
                f'PC is not pending in a korp (pcid:{pc.id},korpid:{korpid})',
                None)

    try:
        pc           = session.query(Creature)\
                              .filter(Creature.id == pcid)\
                              .one_or_none()
        pc.korp_rank = 'Member'
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] PC korp accept failed (pcid:{pc.id},korpid:{korpid}) [{e}]',
                None)
    else:
        try:
            korp_members    = []
            members         = session.query(Creature)\
                                     .filter(Creature.korp == pc.korp)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                korp_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** accepted this korp',
                    "embed": None,
                    "scope": f'Korp-{pc.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp_members,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC korp accept successed (pcid:{pc.id},korpid:{korpid})',
                    None)
    finally:
        session.close()

# API: /mypc/<int:pcid>/korp/<int:korpid>/decline
def mypc_korp_leave(username,pcid,korpid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

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
    if pc.korp != korpid:
        return (200,
                False,
                f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                None)
    if pc.korp_rank == 'Leader':
        return (200,
                False,
                f'Leader cannot leave a Korp (pcid:{pc.id},korpid:{korpid})',
                None)

    try:
        pc           = session.query(Creature)\
                              .filter(Creature.id == pcid)\
                              .one_or_none()
        pc.korp      = None
        pc.korp_rank = None
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] PC korp leave failed (pcid:{pc.id},korpid:{korpid}) [{e}]',
                None)
    else:
        try:
            korp_members    = []
            members         = session.query(Creature)\
                                     .filter(Creature.korp == pc.korp)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                korp_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** declined the invite',
                    "embed": None,
                    "scope": f'Korp-{korpid}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp_members,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC korp leave successed (pcid:{pc.id},korpid:{korpid})',
                    None)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/korp/<int:korpid>/leave
def mypc_korp_decline(username,pcid,korpid):
    pc      = fn_creature_get(None,pcid)[3]
    user    = fn_user_get(username)
    session = Session()

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
    if pc.korp != korpid:
        return (200,
                False,
                f'Korp request outside of your scope (pcid:{pc.id},korpid:{korpid})',
                None)
    if pc.korp_rank == 'Leader':
        return (200,
                False,
                f'PC cannot be the korp Leader (pcid:{pc.id},korpid:{korp.id})',
                None)

    try:
        pc           = session.query(Creature)\
                              .filter(Creature.id == pcid)\
                              .one_or_none()
        pc.korp      = None
        pc.korp_rank = None
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] PC korp leave failed (pcid:{pc.id},korpid:{korpid}) [{e}]',
                None)
    else:
        try:
            korp_members    = []
            members         = session.query(Creature)\
                                     .filter(Creature.korp == pc.korp)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                korp_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** left this korp',
                    "embed": None,
                    "scope": f'Korp-{korpid}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": korp_members,
                    "route": 'mypc/{id1}/korp',
                    "scope": 'korp'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC successfully left (pcid:{pc.id},korpid:{korpid})',
                    None)
    finally:
        session.close()
