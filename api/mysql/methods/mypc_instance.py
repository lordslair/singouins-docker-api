# -*- coding: utf8 -*-

from ..session           import Session
from ..models            import Creature

from .fn_creature        import *
from .fn_user            import fn_user_get

#
# Queries /mypc/<int:pcid>/instance/*
#

# API: PUT /mypc/<int:creatureid>/instance
def mypc_instance_create(username,creatureid,hardcore,fast,mapid,public):
    creature    = fn_creature_get(None,creatureid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if creature is None:
        return (200,
                False,
                f'PC not found (creatureid:{creatureid})',
                None)
    if creature.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (creatureid:{creature.id},username:{username})',
                None)
    if creature.instance is not None:
        return (200,
                False,
                f'PC is already in an instance (creatureid:{creatureid},instanceid:{creature.instance})',
                None)
    if not isinstance(mapid, int):
        return (200,
                False,
                f'Map ID should be an integer (mapid:{mapid})',
                None)
    if not isinstance(hardcore, bool):
        return (200,
                False,
                f'Hardcore param should be a boolean (hardcore:{hardcore})',
                None)
    if not isinstance(fast, bool):
        return (200,
                False,
                f'Fast param should be a boolean (fast:{fast})',
                None)
    if not isinstance(public, bool):
        return (200,
                False,
                f'Public param should be a boolean (public:{public})',
                None)

    # Check if map related to mapid exists
    try:
        map = maps.get_map(mapid)
    except Exception as e:
        return (200,
                False,
                f'[Redis] Map query failed (mapid:{mapid}) [{e}]',
                None)

    # Create the new instance
    try:
        instance = instances.add_instance(creature,fast,hardcore,mapid,public)
    except Exception as e:
        return (200,
                False,
                f'[Redis] Instance creation failed [{e}]',
                None)
    else:
        if instance:
            # Everything went well so far
            try:
                # Assign the PC into the instance
                pc          = session.query(Creature).filter(Creature.id == creature.id).one_or_none()
                pc.instance = instance['id']
                session.commit()
            except Exception as e:
                session.rollback()
                return (200,
                        False,
                        f"[SQL] Instance association failed (creatureid:{creature.id},instanceid:{instance['id']}) [{e}]",
                        None)
            # Everything went well, creation DONE
            # We put the info in queue for Discord
            if pc.korp is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{creature.id}] {creature.name}** opened an Instance ({pc.instance})',
                        "embed": None,
                        "scope": f'Korp-{pc.korp}'}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except:
                    pass
            if pc.squad is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{creature.id}] {creature.name}** opened an Instance ({pc.instance})',
                        "embed": None,
                        "scope": f'Squad-{pc.squad}'}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except:
                    pass
            # We put the info in queue for IA to populate the instance
            try:
                queue.yqueue_put('yarqueue:instances', {"action": 'create', "instance": instance})
            except:
                pass
            # Finally everything is done
            return (201,
                    True,
                    f'Instance creation successed (creatureid:{creature.id})',
                    instance)
        else:
            return (200,
                    False,
                    f'Instance creation failed (creatureid:{creature.id})',
                    None)
    finally:
        session.close()

# API: GET /mypc/<int:creatureid>/instance/<int:instanceid>
def mypc_instance_get(username,creatureid,instanceid):
    creature    = fn_creature_get(None,creatureid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if creature is None:
        return (200,
                False,
                f'PC not found (creatureid:{creatureid})',
                None)
    if creature.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (creatureid:{creature.id},username:{username})',
                None)
    if not isinstance(instanceid, int):
        return (200,
                False,
                f'Instance ID should be an integer (instanceid:{instanceid})',
                None)
    if creature.instance != instanceid:
        return (200,
                False,
                f'PC is not in this instance (creatureid:{creature.id},instanceid:{creature.instance})',
                None)

    # Check if the instance exists
    try:
        instance = instances.get_instance(instanceid)
    except Exception as e:
        return (200,
                False,
                f'[Redis] Instance query failed (creatureid:{creature.id},instanceid:{instanceid}) [{e}]',
                None)
    else:
        if instance is False:
            return (200,
                    False,
                    f'[Redis] Instance not found (creatureid:{creature.id},instanceid:{instanceid})',
                    None)
        else:
            return (200,
                    True,
                    f"Instance found (creatureid:{creature.id},instanceid:{instance['id']})",
                    instance)

# API: POST /mypc/<int:creatureid>/instance/<int:instanceid>/leave
def mypc_instance_leave(username,creatureid,instanceid):
    creature    = fn_creature_get(None,creatureid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if creature is None:
        return (200,
                False,
                f'PC not found (creatureid:{creatureid})',
                None)
    if creature.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (creatureid:{creature.id},username:{username})',
                None)
    if creature.instance is None:
        return (200,
                False,
                f'PC is not in an instance (creatureid:{creature.id},instanceid:{creature.instance})',
                None)
    if not isinstance(instanceid, int):
        return (200,
                False,
                f'Instance ID should be an integer (instanceid:{instanceid})',
                None)

    # Check if the instance exists
    try:
        instance = instances.get_instance(instanceid)
    except Exception as e:
        return (200,
                False,
                f'[Redis] Instance query failed (creatureid:{creature.id},instanceid:{instanceid}) [{e}]',
                None)
    else:
        if instance is False:
            return (200,
                    False,
                    f'[Redis] Instance not found (creatureid:{creature.id},instanceid:{instanceid})',
                    None)

    # Check if PC is the last inside the instance
    try:
        pcs = session.query(Creature)\
                     .filter(Creature.instance == instance['id'])\
                     .all()
        pc = session.query(Creature)\
                     .filter(Creature.id == creature.id)\
                     .one_or_none()
    except Exception as e:
        return (200,
                False,
                f"[SQL] PCs query failed (instanceid:{instance['id']}) [{e}]",
                None)


    if len(pcs) == 1:
        # The PC is the last inside: we delete the instance
        # SQL modifications
        try:
            # Start with Redis deletion
            count = instances.del_instance(instanceid)
            if count is None or count == 0:
                # Delete keys failes, or keys not found
                return (200,
                        False,
                        f'[Redis] Instance cleaning failed (instanceid:{instanceid}) [{e}]',
                        None)
            # SQL data deletion
            pc.instance       = None # We set the PC instance back to NULL
            creature.instance = None # Only for the returned payload
            session.commit()
        except Exception as e:
            session.rollback()
            return (200,
                    False,
                    f'[SQL] Instance cleaning failed (instanceid:{instanceid}) [{e}]',
                    None)
        else:
            # Everything went well, deletion DONE
            # We put the info in queue for Discord
            if pc.korp is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{creature.id}] {creature.name}** closed an Instance ({instanceid})',
                        "embed": None,
                        "scope": f'Korp-{pc.korp}'}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except:
                    pass
            if pc.squad is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{creature.id}] {creature.name}** closed an Instance ({instanceid})',
                        "embed": None,
                        "scope": f'Squad-{pc.squad}'}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except:
                    pass
            # We put the info in queue for IA to clean the instance
            try:
                queue.yqueue_put('yarqueue:instances', {"action": 'delete', "instance": instance})
            except:
                pass
            # Finally everything is done
            return (200,
                    True,
                    f'Instance leave successed (instanceid:{instanceid})',
                    creature)
        finally:
            session.close()
    else:
        # Other players are still in the instance
        try:
            pc.instance       = None # We set the PC instance back to NULL
            creature.instance = None # Only for the returned payload
            session.commit()
        except Exception as e:
            session.rollback()
            return (200,
                    False,
                    f'[SQL] Instance cleaning failed (instanceid:{instanceid}) [{e}]',
                    None)
        else:
            #session.refresh(pc)
            # We put the info in queue for Discord
            qmsg = {"ciphered": False,
                    "payload": f':map: **[{creature.id}] {creature.name}** left an Instance',
                    "embed": None,
                    "scope": f'Korp-{creature.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            return (200,
                    True,
                    f'Instance leave successed (instanceid:{instanceid})',
                    creature)
        finally:
            session.close()

# API: POST /mypc/<int:creatureid>/instance/<int:instanceid>/join
def mypc_instance_join(username,creatureid,instanceid):
    creature    = fn_creature_get(None,creatureid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if creature is None:
        return (200,
                False,
                f'PC not found (creatureid:{creatureid})',
                None)
    if creature.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (creatureid:{creature.id},username:{username})',
                None)
    if not isinstance(instanceid, int):
        return (200,
                False,
                f'Instance ID should be an integer (instanceid:{instanceid})',
                None)
    if creature.instance is not None:
        return (200,
                False,
                f'PC should not be in an instance (creatureid:{creature.id},instanceid:{creature.instance})',
                None)

    # Check if the instance exists
    try:
        instance = instances.get_instance(instanceid)
    except Exception as e:
        return (200,
                False,
                f'[Redis] Instance query failed (creatureid:{creature.id},instanceid:{instanceid}) [{e}]',
                None)
    else:
        if instance is False:
            return (200,
                    False,
                    f'[Redis] Instance not found (creatureid:{creature.id},instanceid:{instanceid})',
                    None)
        if instance['public'] is False:
            return (200,
                    False,
                    f"[Redis] Instance not public (creatureid:{creature.id},instanceid:{instance['id']},public:i{nstance['public']})",
                    None)

    # We add the Creature into the instance
    try:
        pc = session.query(Creature)\
                     .filter(Creature.id == creature.id)\
                     .one_or_none()
        pc.instance       = instance['id'] # We set the PC instance
        creature.instance = instance['id'] # Only for the returned payload
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f"[SQL] Instance join failed (instanceid:{instance['id']}) [{e}]",
                None)
    else:
        #session.refresh(pc)
        return (200,
                True,
                f"Instance join successed (instanceid:{instance['id']})",
                creature)
    finally:
        session.close()
