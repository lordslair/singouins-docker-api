# -*- coding: utf8 -*-

import dataclasses

from flask                               import Flask, jsonify, request
from flask_jwt_extended                  import jwt_required,get_jwt_identity
from random                              import choices,randint

from mysql.methods.fn_creature           import (fn_creature_get,
                                                 fn_creature_add,
                                                 fn_creature_del,
                                                 fn_creature_stats_del)
from mysql.methods.fn_creatures          import fn_creatures_in_instance
from mysql.methods.fn_user               import fn_user_get
from mysql.methods.fn_creature_instance  import fn_creature_instance_set

from nosql                               import *
from nosql.publish                       import *
from nosql.models.RedisInstance          import *

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
        instance_dict = {
                            "creator":  creature.id,
                            "fast":     fast,
                            "hardcore": hardcore,
                            "map":      mapid,
                            "public":   public
                        }
        instance = RedisInstance(creature = creature)
        instance.new(instance_dict)
    except Exception as e:
        msg = f"Instance Query KO (creatureid:{creature.id}) [{e}]"
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance:
            # Everything went well so far
            try:
                # Assign the PC into the instance
                ret = fn_creature_instance_set(creature,instance.id)
            except Exception as e:
                msg = f"Instance Query KO (creatureid:{creature.id},instanceid:{instance.id}) [{e}]"
                logger.error(msg)
                return jsonify({"success": False,
                                "msg": msg,
                                "payload": None}), 200

            if ret is None:
                return jsonify({"success": False,
                                "msg": f"Instance create KO (creatureid:{creature.id},instanceid:{instance.id})",
                                "payload": None}), 200

            # Everything went well, creation DONE
            # We put the info in queue for Discord
            scopes = []
            if ret.korp is not None:  scopes.append(f'Korp-{ret.korp}')
            if ret.squad is not None: scopes.append(f'Squad-{ret.squad}')
            for scope in scopes:
                try:
                    qmsg = {"ciphered": False,
                            "payload": f':map: **[{ret.id}] {ret.name}** opened an Instance ({instanceid})',
                            "embed": None,
                            "scope": scope}
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except Exception as e:
                    msg = f'Queue Query KO (Queue:yarqueue:discord,qmsg:{qmsg}) [{e}]'
                    logger.error(msg)
                else:
                    logger.trace(f'Queue Query OK (Queue:yarqueue:discord,qmsg:{qmsg})')
            # We need to create the mobs to populate the instance
            try:
                (mapx,mapy) = map['size'].split('x')
                logger.trace(f"Map ID:{map['id']} used (mapx:{mapx}:mapy:{mapy})")
                mobs_generated = []
                mobs_nbr = 1
                rarities = ['Small','Medium','Big','Unique','Boss','God']
                while mobs_nbr < 4:
                    try:
                        #
                        race   = randint(11,14)
                        gender = randint(0,1)
                        rarity = choices(rarities,
                                         weights=(20,30,20,10,15,5),
                                         k=1)[0]
                        x = randint(1,int(mapx))
                        y = randint(1,int(mapy))
                        mob = fn_creature_add('Will be replaced later',
                                              race,
                                              gender,
                                              None,
                                              rarity,
                                              x,
                                              y,
                                              instance.id)
                    except Exception as e:
                        msg = f'Population in Instance KO for mob #{mobs_nbr} [{e}]'
                        logger.error(msg)
                    else:
                        if mob is None:
                            msg = f'Population in Instance KO for mob #{mobs_nbr}'
                            logger.error(msg)
                        else:
                            mobs_generated.append(mob)
                            msg = f'Population in Instance OK  for mob #{mobs_nbr} : [{mob.id}] {mob.name}'
                            # We put the info in pubsub channel for IA to populate the instance
                            try:
                                pmsg     = {"action":   'pop',
                                            "instance": instance._asdict(),
                                            "creature": mob}
                                pchannel = 'ai-creature'
                                publish(pchannel, jsonify(pmsg).get_data())
                            except Exception as e:
                                msg = f'Publish({pchannel}) KO [{e}]'
                                logger.error(msg)
                            else:
                                logger.trace(f'Publish({pchannel}) OK')

                    mobs_nbr += 1
            except Exception as e:
                msg = f'Population in Instance KO [{e}]'
                logger.error(msg)
            else:
                if len(mobs_generated) > 0:
                    msg = f'Population in Instance OK (mobs:{len(mobs_generated)})'
                    logger.trace(msg)
                else:
                    msg = f'Population in Instance KO'
                    logger.error(msg)
            # Finally everything is done
            msg = f"Instance create OK (creatureid:{ret.id})"
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": instance._asdict()}), 201
        else:
            msg = f"Instance create KO (creatureid:{ret.id})"
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
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
        instance = RedisInstance(creature = creature)
    except Exception as e:
        msg = f'Instance Query KO (creatureid:{creature.id},instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance:
            return jsonify({"success": True,
                            "msg": f"Instance found (creatureid:{creature.id},instanceid:{instance.id})",
                            "payload": instance._asdict()}), 200
        else:
            return jsonify({"success": False,
                            "msg": f'Instance not found (creatureid:{creature.id},instanceid:{instanceid})',
                            "payload": None}), 200

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
        instance = RedisInstance(creature = None, instanceid = instanceid)
    except Exception as e:
        msg = f'Instance Query KO (creatureid:{creature.id},instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance and instance.public is False:
            return jsonify({"success": False,
                            "msg": f'Instance not public (creatureid:{creature.id},instanceid:{instance.id})',
                            "payload": None}), 200

    # We add the Creature into the instance
    try:
        ret = fn_creature_instance_set(creature,instance.id)
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
        # We put the info in queue for Discord
        scopes = []
        if ret.korp is not None:  scopes.append(f'Korp-{ret.korp}')
        if ret.squad is not None: scopes.append(f'Squad-{ret.squad}')
        for scope in scopes:
            qmsg = {"ciphered": False,
                    "payload": f':map: **[{ret.id}] {ret.name}** joined an Instance ({instance.id})',
                    "embed": None,
                    "scope": scope}
            try:
                queue.yqueue_put('yarqueue:discord', qmsg)
            except Exception as e:
                msg = f'Queue Query KO (Queue:yarqueue:discord,qmsg:{qmsg}) [{e}]'
                logger.error(msg)
            else:
                logger.trace(f'Queue Query OK (Queue:yarqueue:discord,qmsg:{qmsg})')

        # Everything went well
        msg = f'Instance join OK (creatureid:{creature.id},instanceid:{instance.id})'
        logger.debug(msg)
        return jsonify({"success": True,
                        "msg":     msg,
                        "payload": ret}), 200

# API: POST /mypc/{pcid}/instance/{instanceid}/leave
@jwt_required()
def instance_leave(pcid,instanceid):
    creature    = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(get_jwt_identity())

    # Pre-flight checks
    if creature is None:
        msg = f'Creature({pcid}) does not exist'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        h = f'[Creature.id:{creature.id}]' # Header for logging
    if creature.account != user.id:
        msg = f'{h} Token/username mismatch (username:{user.name})'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 409
    if creature.instance is None:
        msg = f'{h} Creature not in an Instance'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    if creature.instance != instanceid:
        msg = f'{h} Creature is not in Instance({instanceid})'
        logger.warning(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    # Check if the instance exists
    try:
        instance = RedisInstance(creature = creature)
    except Exception as e:
        msg = f'{h} Instance({instanceid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if instance.id is None:
            msg = f'{h} Instance({instanceid}) not found'
            logger.warning(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200

    # Check if PC is the last inside the instance
    try:
        pcs = fn_creatures_in_instance(instanceid)

        # Check if they are players or monsters left
        if len(pcs) > 1:
            pc_in_instance = 0
            for creature_in_instance in pcs:
                if creature_in_instance['account']:
                    # This is a PC
                    pc_in_instance += 1
    except Exception as e:
        msg = f'{h} PCs query failed (instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200

    if len(pcs) == 1 or pc_in_instance == 1:
        logger.trace(f'{h} PC is the last inside OR the last player inside')
        # The PC is the last inside OR the last player inside
        # We delete the instance
        try:
            # SQL data update
            ret = fn_creature_instance_set(creature,None)
            if ret is None:
                msg = f'{h} Instance({instanceid}) leave KO'
                logger.warning(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
            # We need to kill all NPC inside the instance
            for creature_in_instance in pcs:
                if creature_in_instance['id'] == creature.id:
                    # We do nothing, it is a Player Creature
                    pass
                else:
                    logger.trace(f'{h} Leaving Instance({instanceid}) with no PC left')
                    creature_to_kill = fn_creature_get(None,creature_in_instance['id'])[3]
                    # We delete Stats
                    if fn_creature_stats_del(creature_to_kill):
                        logger.trace(f"{h} CreatureStats({creature_to_kill.id}) delete OK (MySQL)")
                    else:
                        logger.warning(f"{h} CreatureStats({creature_to_kill.id}) delete KO (MySQL)")
                    # We put the info in pubsub channel for IA to regulate the instance
                    try:
                        pmsg     = {"action":   'kill',
                                    "instance": instance._asdict(),
                                    "creature": creature_to_kill}
                        pchannel = 'ai-creature'
                        publish(pchannel, jsonify(pmsg).get_data())
                    except Exception as e:
                        msg = f'Publish({pchannel}) KO [{e}]'
                        logger.error(msg)
                    else:
                        logger.trace(f'Publish({pchannel}) OK')
                    # We kill it
                    # ALWAYS KILL CREATURE THE LAST
                    if fn_creature_del(creature_to_kill):
                        logger.trace(f"{h} Creature({creature_to_kill.id}) delete OK (MySQL)")
                    else:
                        logger.warning(f"{h} Creature({creature_to_kill.id}) delete KO (MySQL)")


            #  Redis Object deletion
            if instance.destroy() is None:
                # Delete keys failed, or keys not found
                msg = f'{h} Instance({instanceid}) clean KO'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
        except Exception as e:
            msg = f'{h} Instance({instanceid}) leave KO [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        else:
            # Everything went well, deletion DONE
            # We put the info in queue for Discord
            scopes = []
            if ret.korp is not None:  scopes.append(f'Korp-{ret.korp}')
            if ret.squad is not None: scopes.append(f'Squad-{ret.squad}')
            for scope in scopes:
                qmsg = {"ciphered": False,
                        "payload":  f':map: **[{ret.id}] {ret.name}** closed an Instance ({instanceid})',
                        "embed":    None,
                        "scope":    scope}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except Exception as e:
                    msg = f'{h} Queue(yarqueue:discord) Query KO (qmsg:{qmsg}) [{e}]'
                    logger.error(msg)
                else:
                    logger.trace(f'{h} Queue(yarqueue:discord) Query OK (qmsg:{qmsg})')
            # Finally everything is done
            msg = f"{h} Instance({instanceid}) leave OK"
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": creature}), 200
    else:
        # Other PC are still in the instance
        logger.trace(f'{h} PC is not the last player inside (pcs:{pc_in_instance})')
        try:
            # We just update Creature.instance
            ret = fn_creature_instance_set(creature,None)
            if ret is None:
                msg = f"{h} Instance({instanceid}) leave KO"
                logger.warning(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
        except Exception as e:
            msg = f'{h} Instance({instanceid}) leave KO [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        else:
            # We put the info in queue for Discord
            scopes = []
            if ret.korp is not None:  scopes.append(f'Korp-{ret.korp}')
            if ret.squad is not None: scopes.append(f'Squad-{ret.squad}')
            for scope in scopes:
                qmsg = {"ciphered": False,
                        "payload":  f':map: **[{ret.id}] {ret.name}** left an Instance ({instanceid})',
                        "embed":    None,
                        "scope":    scope}
                try:
                    queue.yqueue_put('yarqueue:discord', qmsg)
                except Exception as e:
                    msg = f'{h} Queue(yarqueue:discord) Query KO (qmsg:{qmsg}) [{e}]'
                    logger.error(msg)
                else:
                    logger.trace(f'{h} Queue(yarqueue:discord) Query OK (qmsg:{qmsg})')

            msg = f"{h} Instance({instanceid}) leave OK"
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": creature}), 200
