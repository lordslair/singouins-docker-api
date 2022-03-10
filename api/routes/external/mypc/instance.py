# -*- coding: utf8 -*-

from flask                               import Flask, jsonify, request
from flask_jwt_extended                  import jwt_required,get_jwt_identity

from mysql.methods.fn_creature           import fn_creature_get
from mysql.methods.fn_creatures          import fn_creatures_in_instance
from mysql.methods.fn_user               import fn_user_get
from mysql.methods.fn_creature_instance  import fn_creature_instance_set

from nosql                               import *

#
# Routes /mypc/{pcid}/instance/*
#
# API: PUT /mypc/{pcid}/instance
@jwt_required()
def instance_add(pcid):
    creature    = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    if not request.is_json:
        return jsonify({"success": False,
                        "msg": "Missing JSON in request",
                        "payload": None}), 400

    hardcore = request.json.get('hardcore', None)
    fast     = request.json.get('fast',     None)
    mapid    = request.json.get('mapid',    None)
    public   = request.json.get('public',   None)

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200
    if creature.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (creatureid:{creature.id},username:{user.name})',
                        "payload": None}), 409
    if creature.instance is not None:
        return jsonify({"success": False,
                        "msg": f'Creature in an instance (creatureid:{creature.id})',
                        "payload": None}), 200
    if not isinstance(mapid, int):
        return jsonify({"success": False,
                        "msg": f'Map ID should be an integer (mapid:{mapid})',
                        "payload": None}), 200
    if not isinstance(hardcore, bool):
        return jsonify({"success": False,
                        "msg": f'Hardcore param should be a boolean (hardcore:{hardcore})',
                        "payload": None}), 200
    if not isinstance(fast, bool):
        return jsonify({"success": False,
                        "msg": f'Fast param should be a boolean (fast:{fast})',
                        "payload": None}), 200
    if not isinstance(public, bool):
        return jsonify({"success": False,
                        "msg": f'Public param should be a boolean (public:{public})',
                        "payload": None}), 200

    # Check if map related to mapid exists
    try:
        map = maps.get_map(mapid)
    except Exception as e:
        msg = f'Map Query KO (mapid:{mapid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    # Create the new instance
    try:
        instance = instances.add_instance(creature,fast,hardcore,mapid,public)
    except Exception as e:
        msg = f"Instance Query KO (creatureid:{creature.id},instanceid:{instance['id']}) [{e}]"
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance:
            # Everything went well so far
            try:
                # Assign the PC into the instance
                ret = fn_creature_instance_set(creature,instance['id'])
            except Exception as e:
                msg = f"Instance Query KO (creatureid:{creature.id},instanceid:{instance['id']}) [{e}]"
                logger.error(msg)
                return jsonify({"success": False,
                                "msg": msg,
                                "payload": None}), 200

            if ret is None:
                return jsonify({"success": False,
                                "msg": f"Instance create KO (creatureid:{creature.id},instanceid:{instance['id']})",
                                "payload": None}), 200

            # Everything went well, creation DONE
            # We put the info in queue for Discord
            if ret.korp is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{ret.id}] {ret.name}** opened an Instance ({ret.instance})',
                        "embed": None,
                        "scope": f'Korp-{ret.korp}'}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except:
                    pass
            if ret.squad is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{ret.id}] {ret.name}** opened an Instance ({ret.instance})',
                        "embed": None,
                        "scope": f'Squad-{ret.squad}'}
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
            return jsonify({"success": True,
                            "msg": f"Instance create OK (creatureid:{ret.id})",
                            "payload": instance}), 201
        else:
            return jsonify({"success": False,
                            "msg": f'Instance create KO (creatureid:{ret.id})',
                            "payload": None}), 200

# API: GET /mypc/{pcid}/instance/{instanceid}
@jwt_required()
def instance_get(pcid,instanceid):
    creature    = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200
    if creature.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (creatureid:{creature.id},username:{user.name})',
                        "payload": None}), 409
    if creature.instance is None:
        return jsonify({"success": False,
                        "msg": f'Creature not in an instance (creatureid:{creature.id})',
                        "payload": None}), 200
    if creature.instance != instanceid:
        return jsonify({"success": False,
                        "msg": f'PC is not in this instance (creatureid:{creature.id},instanceid:{instanceid})',
                        "payload": None}), 200

    # Check if the instance exists
    try:
        instance = instances.get_instance(instanceid)
    except Exception as e:
        msg = f'Instance Query KO (creatureid:{creature.id},instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance is False:
            return jsonify({"success": False,
                            "msg": f'Instance not found (creatureid:{creature.id},instanceid:{instanceid})',
                            "payload": None}), 200
        else:
            return jsonify({"success": True,
                            "msg": f"Instance found (creatureid:{creature.id},instanceid:{instance['id']})",
                            "payload": instance}), 200

# API: POST /mypc/{pcid}/instance/{instanceid}/join
@jwt_required()
def instance_join(pcid,instanceid):
    creature    = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200
    if creature.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (creatureid:{creature.id},username:{user.name})',
                        "payload": None}), 409
    if creature.instance is not None:
        return jsonify({"success": False,
                        "msg": f'Creature in an instance (creatureid:{creature.id},instanceid:{creature.instance})',
                        "payload": None}), 200

    # Check if the instance exists
    try:
        instance = instances.get_instance(instanceid)
    except Exception as e:
        msg = f'Instance Query KO (creatureid:{creature.id},instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance is False:
            return jsonify({"success": False,
                            "msg": f'Instance not found (creatureid:{creature.id},instanceid:{instanceid})',
                            "payload": None}), 200
        if instance['public'] is False:
            return jsonify({"success": False,
                            "msg": f'Instance not public (creatureid:{creature.id},instanceid:{instanceid})',
                            "payload": None}), 200

    # We add the Creature into the instance
    try:
        ret = fn_creature_instance_set(creature,instance['id'])
        if ret is None:
            return jsonify({"success": False,
                            "msg": f"Instance join KO (creatureid:{creature.id},instanceid:{instance['id']})",
                            "payload": None}), 200
    except Exception as e:
        msg = f'Instance Query KO (creatureid:{creature.id},instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        return jsonify({"success": True,
                        "msg": f"Instance join OK (creatureid:{creature.id},instanceid:{instance['id']})",
                        "payload": ret}), 200

# API: POST /mypc/{pcid}/instance/{instanceid}/leave
@jwt_required()
def instance_leave(pcid,instanceid):
    creature    = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        return jsonify({"success": False,
                        "msg": f'Creature not found (creatureid:{creatureid})',
                        "payload": None}), 200
    if creature.account != user.id:
        return jsonify({"success": False,
                        "msg": f'Token/username mismatch (creatureid:{creature.id},username:{user.name})',
                        "payload": None}), 409
    if creature.instance is None:
        return jsonify({"success": False,
                        "msg": f'Creature not in an instance (creatureid:{creature.id},instanceid:{creature.instance})',
                        "payload": None}), 200
    if creature.instance != instanceid:
        return jsonify({"success": False,
                        "msg": f'PC is not in this instance (creatureid:{creature.id},instanceid:{instanceid})',
                        "payload": None}), 200

    # Check if the instance exists
    try:
        instance = instances.get_instance(instanceid)
    except Exception as e:
        msg = f'Instance Query KO (creatureid:{creature.id},instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance is False:
            return jsonify({"success": False,
                            "msg": f'Instance not found (creatureid:{creature.id},instanceid:{instanceid})',
                            "payload": None}), 200

    # Check if PC is the last inside the instance
    try:
        pcs = fn_creatures_in_instance(instanceid)
    except Exception as e:
        msg = f'PCs query failed (instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200

    if len(pcs) == 1:
        # The PC is the last inside: we delete the instance
        # SQL modifications
        try:
            # Start with Redis deletion
            count = instances.del_instance(instanceid)
            if count is None or count == 0:
                # Delete keys failes, or keys not found
                return jsonify({"success": False,
                                "msg": f'Instance cleaning KO (instanceid:{instanceid}) [{e}]',
                                "payload": None}), 200
            # SQL data deletion
            ret = fn_creature_instance_set(creature,None)
            if ret is None:
                return jsonify({"success": False,
                                "msg": f"Instance leave KO (creatureid:{creature.id})",
                                "payload": None}), 200
        except Exception as e:
            msg = f'Instance cleaning KO (instanceid:{instanceid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # Everything went well, deletion DONE
            # We put the info in queue for Discord
            if ret.korp is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{ret.id}] {ret.name}** closed an Instance ({instanceid})',
                        "embed": None,
                        "scope": f'Korp-{ret.korp}'}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except:
                    pass
            if ret.squad is not None:
                qmsg = {"ciphered": False,
                        "payload": f':map: **[{ret.id}] {ret.name}** closed an Instance ({instanceid})',
                        "embed": None,
                        "scope": f'Squad-{ret.squad}'}
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
            return jsonify({"success": True,
                            "msg": f"Instance leave OK (creatureid:{creature.id},instanceid:{instanceid})",
                            "payload": ret}), 200
    else:
        # Other players are still in the instance
        try:
            ret = fn_creature_instance_set(creature,None)
            if ret is None:
                return jsonify({"success": False,
                                "msg": f"Instance leave KO (creatureid:{creature.id})",
                                "payload": None}), 200
        except Exception as e:
            msg = f'Instance cleaning KO (instanceid:{instanceid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg": msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for Discord
            qmsg = {"ciphered": False,
                    "payload": f':map: **[{ret.id}] {ret.name}** left an Instance',
                    "embed": None,
                    "scope": f'Korp-{ret.korp}'}
            queue.yqueue_put('yarqueue:discord', qmsg)
            return jsonify({"success": True,
                            "msg": f"Instance leave OK (creatureid:{creature.id},instanceid:{instanceid})",
                            "payload": ret}), 200
