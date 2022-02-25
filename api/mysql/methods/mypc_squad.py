# -*- coding: utf8 -*-

import dataclasses

from ..session           import Session
from ..models            import Creature,Squad

from .fn_creature        import *
from .fn_user            import fn_user_get

#
# Queries /mypc/<int:pcid>/squad/*
#

# API: GET /mypc/<int:pcid>/squad/<int:squadid>
def get_squad(username,pcid,squadid):
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
    if pc.squad != squadid:
        return (200,
                False,
                f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                None)

    # Let's get the squad from DB
    try:
        squad = session.query(Squad).\
                        filter(Squad.id == pc.squad).\
                        filter(Creature.id == pc.id)

        pc_is_member  = squad.filter(Creature.squad_rank != 'Pending').one_or_none()
        pc_is_pending = squad.filter(Creature.squad_rank == 'Pending').one_or_none()

        if pc_is_member:
            squad   = squad.session.query(Squad).filter(Squad.id == pc.squad).one_or_none()
            members = session.query(Creature)\
                             .filter(Creature.squad == squad.id)\
                             .filter(Creature.squad_rank != 'Pending')\
                             .all()
            pending = session.query(Creature)\
                             .filter(Creature.squad == squad.id)\
                             .filter(Creature.squad_rank == 'Pending')\
                             .all()
        elif pc_is_pending:
            squad   = squad.session.query(Squad).filter(Squad.id == pc.squad).one_or_none()

    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                f'[SQL] Squad query failed (pcid:{pcid},squadid:{squadid}) [{e}]',
                None)
    else:
        if pc_is_member:
            if squad:
                if isinstance(members, list):
                    if isinstance(pending, list):
                        return (200,
                                True,
                                f'Squad query successed (pcid:{pcid},squadid:{squadid})',
                                {"squad": squad, "members": members, "pending": pending})
        elif pc_is_pending:
            return (200,
                    True,
                    f'PC is pending in a squad (pcid:{pcid},squadid:{squadid})',
                    {"squad": squad})
        else:
            return (200,
                    False,
                    f'PC is not in a squad (pcid:{pcid},squadid:{squadid})',
                    None)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/squad
def add_squad(username,pcid):
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
    if pc.squad is not None:
        return (200,
                False,
                f'Squad leader already in a squad (pcid:{pc.id},squadid:{pc.squad})',
                None)

    # Let's create the Squad in DB
    try:
        squad = Squad(leader  = pc.id)
        session.add(squad)
        session.commit()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Squad creation failed (pcid:{pc.id}) [{e}]',
                None)

    # Squad created, let's assign the team creator in the squad
    pc            = session.query(Creature)\
                           .filter(Creature.id == pcid)\
                           .one_or_none()
    squad         = session.query(Squad)\
                           .filter(Squad.leader == pc.id)\
                           .one_or_none()
    pc.squad      = squad.id
    pc.squad_rank = 'Leader'

    try:
        session.commit()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Squad leader assignation failed (pcid:{pc.id},squadid:{squad.id}) [{e}]',
                None)
    else:
        try:
            squad_members   = []
            members         = session.query(Creature)\
                                     .filter(Creature.squad == pc.squad)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                squad_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** created this squad',
                    "embed": None,
                    "scope": f'Squad-{pc.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad_members,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', qmsg)
            return (201,
                    True,
                    f'Squad successfully created (pcid:{pc.id},squadid:{squad.id})',
                    squad_members)

# API: DELETE /mypc/<int:pcid>/squad/<int:squadid>
def del_squad(username,leaderid,squadid):
    leader  = fn_creature_get(None,leaderid)[3]
    user    = fn_user_get(username)
    session = Session()

    # Pre-flight checks
    if leader is None:
        return (200,
                False,
                f'PC not found (leaderid:{leaderid})',
                None)
    if leader.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{leaderid},username:{username})',
                None)
    if leader.squad != squadid:
        return (200,
                False,
                f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                None)
    if leader.squad_rank != 'Leader':
        return (200,
                False,
                f'PC is not the squad Leader (pcid:{pc.id},squadid:{squadid},rank:{leader.squad_rank})',
                None)

    try:
        squad = session.query(Squad)\
                       .filter(Squad.leader == leader.id)\
                       .one_or_none()
        if not squad:
            return (200,
                    False,
                    f'Squad not found (pcid:{leader.id})',
                    None)

        count = session.query(Creature)\
                       .filter(Creature.squad == squad.id)\
                       .count()
        if count > 1:
            return (200,
                    False,
                    f'Squad not empty (squadid:{squad.id},count:{count})',
                    None)

        session.delete(squad)
        pc            = session.query(Creature)\
                               .filter(Creature.id == leader.id)\
                               .one_or_none()
        pc.squad      = None
        pc.squad_rank = None
        session.commit()
        members       = session.query(Creature)\
                               .filter(Creature.squad == leader.squad)\
                               .all()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Squad deletion failed (squadid:{squad.id}) [{e}]',
                None)
    else:
        # We put the info in queue for ws
        qmsg = {"ciphered": False,
                "payload": f':information_source: **[{pc.id}] {pc.name}** deleted this squad',
                "embed": None,
                "scope": f'Squad-{squadid}'}
        queue.yqueue_put('yarqueue:discord', qmsg)
        # We put the info in queue for ws Front
        qmsg = {"ciphered": False,
                "payload": None,
                "route": 'mypc/{id1}/squad',
                "scope": 'squad'}
        queue.yqueue_put('broadcast', qmsg)

        return (200,
                True,
                f'Squad deletion successed (squadid:{squadid})',
                None)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/invite/<int:targetid>
def invite_squad_member(username,leaderid,squadid,targetid):
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
    if leader.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)
    if leader.squad is None:
        return (200,
                False,
                f'PC not in a squad (pcid:{leaderid})',
                None)
    if leader.squad != squadid:
        return (200,
                False,
                f'Squad request outside of your scope (pcid:{leader.id},squadid:{squadid})',
                None)
    if leader.squad_rank != 'Leader':
        return (200,
                False,
                f'PC is not the squad Leader (pcid:{leader.id},squadid:{squadid},rank:{leader.squad_rank})',
                None)
    if target is None:
        return (200,
                False,
                f'PC not found (targetid:{targetid})',
                None)
    if target.squad is not None:
        return (200,
                False,
                f'PC invited is already in a squad (pcid:{target.id},squadid:{squadid})',
                None)

    # Let's get Squad members
    members    = session.query(Creature)\
                        .filter(Creature.squad == leader.squad)\
                        .all()
    maxmembers = 10
    if len(members) == maxmembers:
        return (200,
                False,
                f'Squad is already full (slots:{len(members)}/{maxmembers})',
                None)

    # Let's associate the target into the Squad in DB
    try:
        pc = session.query(Creature)\
                    .filter(Creature.id == target.id)\
                    .one_or_none()
        pc.squad      = leader.squad
        pc.squad_rank = 'Pending'
        session.commit()
    except Exception as e:
        return (200,
                False,
                f'[SQL] PC Invite failed (slots:{len(members)}/{maxmembers}) [{e}]',
                None)
    else:
        try:
            squad_members   = []
            members         = session.query(Creature)\
                                     .filter(Creature.squad == pc.squad)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                squad_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{leader.id}] {leader.name}** invited **[{target.id}] {target.name}** in this squad',
                    "embed": None,
                    "scope": f'Squad-{leader.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad_members,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC successfully invited (slots:{len(squad_members)+1}/{maxmembers})',
                    fn_creature_get(None,target.id)[3])
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/kick/<int:targetid>
def kick_squad_member(username,leaderid,squadid,targetid):
    target     = fn_creature_get(None,targetid)[3]
    leader     = fn_creature_get(None,leaderid)[3]
    user       = fn_user_get(username)
    maxmembers = 10
    session    = Session()

    # Pre-flight checks
    if leader is None:
        return (200,
                False,
                f'PC not found (leaderid:{leaderid})',
                None)
    if leader.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)
    if leader.squad is None:
        return (200,
                False,
                f'PC not in a squad (pcid:{leaderid})',
                None)
    if leader.squad != squadid:
        return (200,
                False,
                f'Squad request outside of your scope (pcid:{leader.id},squadid:{squadid})',
                None)
    if leader.squad_rank != 'Leader':
        return (200,
                False,
                f'PC is not the squad Leader (pcid:{leader.id},squadid:{squadid},rank:{leader.squad_rank})',
                None)
    if target is None:
        return (200,
                False,
                f'PC not found (targetid:{targetid})',
                None)
    if target.squad is None:
        return (200,
                False,
                f'PC have to be in a squad (pcid:{target.id},squadid:{squadid})',
                None)

    try:
        pc = session.query(Creature)\
                    .filter(Creature.id == target.id)\
                    .one_or_none()
        pc.squad      = None
        pc.squad_rank = None
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                f'[SQL] PC Kick failed (pcid:{target.id},squadid:{target.squad}) [{e}]',
                None)
    else:
        try:
            squad_members   = []
            members         = session.query(Creature)\
                                     .filter(Creature.squad == leader.squad)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                squad_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws Discord
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{leader.id}] {leader.name}** kicked **[{target.id}] {target.name}** from this squad',
                    "embed": None,
                    "scope": f'Squad-{leader.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad_members,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC successfully kicked (slots:{len(squad_members)}/{maxmembers})',
                    squad_members)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/accept
def accept_squad_member(username,pcid,squadid):
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
    if pc.squad != squadid:
        return (200,
                False,
                f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                None)
    if pc.squad_rank != 'Pending':
        return (200,
                False,
                f'PC is not pending in a squad (pcid:{pc.id},rank:{pc.squad_rank})',
                None)

    try:
        pc            = session.query(Creature)\
                               .filter(Creature.id == pcid)\
                               .one_or_none()
        pc.squad_rank = 'Member'
        session.commit()
    except Exception as e:
        return (200,
                False,
                f'[SQL] PC squad invite accept failed (pcid:{pc.id},squadid:{squadid}) [{e}]',
                None)
    else:
        try:
            squad_members   = []
            members         = session.query(Creature)\
                                     .filter(Creature.squad == pc.squad)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                squad_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** accepted this squad',
                    "embed": None,
                    "scope": f'Squad-{pc.squad}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad_members,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    'PC successfully accepted squad invite (pcid:{pc.id},squadid:{squadid})',
                    None)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/decline
def decline_squad_member(username,pcid,squadid):
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
    if pc.squad != squadid:
        return (200,
                False,
                f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                None)
    if pc.squad_rank != 'Pending':
        return (200,
                False,
                f'PC is not pending in a squad (pcid:{pc.id},rank:{pc.squad_rank})',
                None)

    try:
        pc            = session.query(Creature)\
                               .filter(Creature.id == pcid)\
                               .one_or_none()
        pc.squad      = None
        pc.squad_rank = None
        session.commit()
    except Exception as e:
        return (200,
                False,
                f'[SQL] PC squad invite decline failed (pcid:{pc.id},squadid:{squadid}) [{e}]',
                None)
    else:
        try:
            squad_members   = []
            members         = session.query(Creature)\
                                     .filter(Creature.squad == pc.squad)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                squad_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** declined the invite',
                    "embed": None,
                    "scope": f'Squad-{squadid}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": squad_members,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC successfully declined squad invite (pcid:{pc.id},squadid:{squadid})',
                    None)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/squad/<int:squadid>/leave
def leave_squad_member(username,pcid,squadid):
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
    if pc.squad != squadid:
        return (200,
                False,
                f'Squad request outside of your scope (pcid:{pc.id},squadid:{squadid})',
                None)
    if pc.squad_rank == 'Leader':
        return (200,
                False,
                f'PC cannot be the squad Leader (pcid:{pc.id},rank:{pc.squad_rank})',
                None)

    try:
        pc            = session.query(Creature)\
                               .filter(Creature.id == pcid)\
                               .one_or_none()
        pc.squad      = None
        pc.squad_rank = None
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                f'[SQL] PC squad leave failed (pcid:{pc.id},squadid:{squadid})',
                None)
    else:
        try:
            squad_members   = []
            members         = session.query(Creature)\
                                     .filter(Creature.squad == pc.squad)\
                                     .all()
            for creature in members:
                # Lets convert to a dataclass then a dict
                creature.date  = creature.date.strftime('%Y-%m-%d %H:%M:%S')
                creature       = dataclasses.asdict(creature)
                squad_members.append(creature)
        except Exception as e:
            print(e)
        else:
            # We put the info in queue for ws
            qmsg = {"ciphered": False,
                    "payload": f':information_source: **[{pc.id}] {pc.name}** left this squad',
                    "embed": None,
                    "scope": f'Squad-{squadid}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            # We put the info in queue for ws Front
            qmsg = {"ciphered": False,
                    "payload": None,
                    "route": 'mypc/{id1}/squad',
                    "scope": 'squad'}
            queue.yqueue_put('broadcast', qmsg)
            return (200,
                    True,
                    f'PC successfully left (pcid:{pc.id},squadid:{squadid})',
                    None)
    finally:
        session.close()
