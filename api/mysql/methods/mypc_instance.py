# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import Instance, Map, PJ

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get

#
# Queries /mypc/<int:pcid>/instance/*
#

# API: /mypc/<int:pcid>/instance
def mypc_instance_create(username,pcid,hardcore,fast,mapid,public):
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
        map = session.query(Map)\
                     .filter(Map.id == mapid)\
                     .one_or_none()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Map query failed (mapid:{mapid}) [{e}]',
                None)

    # Create the new instance
    instance = Instance(map      = mapid,
                        creator  = pc.id,
                        hardcore = hardcore,
                        public   = public,
                        tick     = 3600,
                        fast     = fast)
    session.add(instance)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Instance creation failed (pcid:{pc.id}) [{e}]',
                None)
    else:
        # Assign the PC into the instance
        pc          = session.query(PJ).filter(PJ.id == pc.id).one_or_none()
        pc.instance = instance.id
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            return (200,
                    False,
                    f'[SQL] Instance association failed (pcid:{pc.id},instanceid:{instance.id}) [{e}]',
                    None)
        else:
            # Everything went well
            session.refresh(instance)
            return (201,
                    True,
                    f'Instance creation successed (pcid:{pc.id})',
                    instance)
    finally:
        session.close()

# API: POST /mypc/<int:pcid>/instance/<int:instanceid>/leave
def mypc_instance_leave(username,pcid,instanceid):
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
    if not isinstance(instanceid, int):
        return (200,
                False,
                f'Instance ID should be an integer (instanceid:{instanceid})',
                None)

    # Check if the instance exists
    try:
        instance = session.query(Instance)\
                          .filter(Instance.id == instanceid)\
                          .one_or_none()
    except Exception as e:
        return (200,
                False,
                f'[SQL] Instance query failed (instanceid:{instanceid}) [{e}]',
                None)
    else:
        if instance is None:
            return (200,
                    False,
                    f'Instance not found (instanceid:{instanceid})',
                    None)

    # Check if PC is thelast inside the instance
    try:
        pcs = session.query(PJ)\
                     .filter(PJ.instance == instance.id)\
                     .all()
        pc = session.query(PJ)\
                     .filter(PJ.id == pc.id)\
                     .one_or_none()
    except Exception as e:
        return (200,
                False,
                f'[SQL] PCs query failed (instanceid:{instance.id}) [{e}]',
                None)

    try:
        if len(pcs) == 1:
            # The PC is the last inside: we delete the instance
            creatures = session.query(PJ)\
                         .filter(PJ.instance == instance.id)\
                         .filter(PJ.account == None)\
                         .all()
            if len(creatures) > 0:
                session.delete(creatures) # We delete the instance creatures
            session.delete(instance) # We delete the instance

        pc.instance = None # We set the PC instance back to NULL
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Instance leave failed (instanceid:{instanceid}) [{e}]',
                None)
    else:
        session.refresh(pc)
        return (200,
                True,
                f'Instance leave successed (instanceid:{instanceid})',
                pc)
    finally:
        session.close()
