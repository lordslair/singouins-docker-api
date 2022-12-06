# -*- coding: utf8 -*-

from flask                               import jsonify, request
from flask_jwt_extended                  import (jwt_required,
                                                 get_jwt_identity)
from loguru                              import logger
from random                              import choices, randint

from nosql.maps                          import get_map
from nosql.publish                       import publish
from nosql.queue                         import yqueue_put
from nosql.metas                         import metaNames
from nosql.models.RedisCreature          import RedisCreature
from nosql.models.RedisInstance          import RedisInstance
from nosql.models.RedisStats             import RedisStats
from nosql.models.RedisUser              import RedisUser

from utils.routehelper          import (
    creature_check,
    request_json_check,
    )

from variables                           import YQ_DISCORD

#
# Routes /mypc/{pcid}/instance/*
#


# API: PUT /mypc/{pcid}/instance
@jwt_required()
def instance_add(pcid):
    request_json_check(request)

    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    hardcore = request.json.get('hardcore', None)
    fast     = request.json.get('fast', None)
    mapid    = request.json.get('mapid', None)
    public   = request.json.get('public', None)

    if Creature.instance is not None:
        msg = f'{h} Creature not in an instance'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(mapid, int):
        msg = f'{h} Map ID should be an INT (mapid:{mapid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(hardcore, bool):
        msg = f'{h} Hardcore param should be a boolean (hardcore:{hardcore})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(fast, bool):
        msg = f'{h} Fast param should be a boolean (hardcore:{hardcore})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if not isinstance(public, bool):
        msg = f'{h} Public param should be a boolean (hardcore:{hardcore})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Check if map related to mapid exists
    try:
        map = get_map(mapid)
    except Exception as e:
        msg = f'{h} Map Query KO (mapid:{mapid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Create the new instance
    try:
        instance_dict = {
            "creator": Creature.id,
            "fast": fast,
            "hardcore": hardcore,
            "map": mapid,
            "public": public
        }
        instance = RedisInstance().new(instance_dict)
    except Exception as e:
        msg = f"{h} Instance Query KO [{e}]"
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Everything went well so far
    try:
        # Assign the PC into the instance
        Creature.instance = instance.id
    except Exception as e:
        msg = f'{h} Instance Query KO (instanceid:{instance.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        pass

    # Everything went well, creation DONE
    # We put the info in queue for Discord
    scopes = []
    if Creature.korp is not None:
        scopes.append(f'Korp-{Creature.korp}')
    if Creature.squad is not None:
        scopes.append(f'Squad-{Creature.squad}')
    for scope in scopes:
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':map: **[{Creature.id}] {Creature.name}** '
                    f'opened an Instance ({instance.id})'
                    ),
                "embed": None,
                "scope": scope,
                }
            )
    # We need to create the mobs to populate the instance
    try:
        (mapx, mapy) = map['size'].split('x')
        mobs_generated = []
        mobs_nbr = 1
        rarities = [
            'Small',
            'Medium',
            'Big',
            'Unique',
            'Boss',
            'God',
        ]
        while mobs_nbr < 4:
            try:
                #
                raceid = randint(11, 16)
                gender = randint(0, 1)
                rarity = choices(rarities,
                                 weights=(20, 30, 20, 10, 15, 5),
                                 k=1)[0]
                x = randint(1, int(mapx))
                y = randint(1, int(mapy))

                Monster = RedisCreature().new(
                    metaNames['race'][raceid]['name'],
                    raceid,
                    gender,
                    None,
                    rarity,
                    x,
                    y,
                    instance.id,
                    )
            except Exception as e:
                msg = (f'{h} Population in Instance KO for mob '
                       f'#{mobs_nbr} [{e}]')
                logger.error(msg)
            else:
                if Monster is None:
                    msg = (f'{h} Population in Instance KO for mob '
                           f'#{mobs_nbr}')
                    logger.warning(msg)
                else:
                    mobs_generated.append(Monster)
                    # We put the info in pubsub channel
                    # for IA to populate the instance
                    try:
                        pmsg     = {"action": 'pop',
                                    "instance": instance._asdict(),
                                    "creature": Monster._asdict()}
                        pchannel = 'ai-creature'
                        publish(pchannel, jsonify(pmsg).get_data())
                    except Exception as e:
                        msg = f'{h} Publish({pchannel}) KO [{e}]'
                        logger.error(msg)
                    else:
                        pass

            mobs_nbr += 1
    except Exception as e:
        msg = f'{h} Population in Instance KO [{e}]'
        logger.error(msg)
    else:
        if len(mobs_generated) > 0:
            msg = (f'{h} Population in Instance OK '
                   f'(mobs:{len(mobs_generated)})')
            logger.trace(msg)
        else:
            msg = f'{h} Population in Instance KO'
            logger.error(msg)
    # Finally everything is done
    msg = f'{h} Instance create OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": instance._asdict(),
        }
    ), 201


# API: GET /mypc/{pcid}/instance/{instanceid}
@jwt_required()
def instance_get(pcid, instanceid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    if Creature.instance is None:
        msg = f'{h} Creature not in an instance'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    # We need to convert instanceid to STR as it is UUID type
    if Creature.instance != str(instanceid):
        msg = f'{h} Creature is not in this instance (instanceid:{instanceid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": Creature._asdict(),
            }
        ), 200

    # Check if the instance exists
    try:
        instance = RedisInstance().get(Creature.instance)
    except Exception as e:
        msg = f'{h} Instance Query KO (instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if instance:
            msg = f'{h} Instance Query OK (instanceid:{instance.id})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": instance._asdict(),
                }
            ), 200
        else:
            msg = f'{h} Instance Query KO - NotFound (instanceid:{instanceid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST /mypc/{pcid}/instance/{instanceid}/join
@jwt_required()
def instance_join(pcid, instanceid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    # We need to convert instanceid to STR as it is UUID type
    instanceid = str(instanceid)

    if Creature.instance is not None:
        msg = f'{h} Creature not in an instance'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Check if the instance exists
    try:
        instance = RedisInstance().get(instanceid)
    except Exception as e:
        msg = f'{h} Instance Query KO (instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        if instance and instance.public is False:
            msg = f'{h} Instance not public (instanceid:{instance.id})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # We add the Creature into the instance
    try:
        Creature.instance = instance.id
    except Exception as e:
        msg = f'{h} Instance Query KO (instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
    else:
        # We put the info in queue for Discord
        scopes = []
        if Creature.korp is not None:
            scopes.append(f'Korp-{Creature.korp}')
        if Creature.squad is not None:
            scopes.append(f'Squad-{Creature.squad}')
        for scope in scopes:
            # Discord Queue
            yqueue_put(
                YQ_DISCORD,
                {
                    "ciphered": False,
                    "payload": (
                        f':map: **[{Creature.id}] {Creature.name}** '
                        f'joined an Instance ({instance.id})'
                        ),
                    "embed": None,
                    "scope": scope,
                    }
                )
        # Everything went well
        msg = f'{h} Instance join OK (instanceid:{instance.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature._asdict(),
            }
        ), 200


# API: POST /mypc/{pcid}/instance/{instanceid}/leave
@jwt_required()
def instance_leave(pcid, instanceid):
    User = RedisUser().get(get_jwt_identity())
    Creature = RedisCreature().get(pcid)
    h = creature_check(Creature, User)

    # We need to convert instanceid to STR as it is UUID type
    instanceid = str(instanceid)

    if Creature.instance is None:
        msg = f'{h} Creature not in an instance'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if Creature.instance != instanceid:
        msg = f'{h} Creature is not in Instance({instanceid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Check if the instance exists
    try:
        Instance = RedisInstance().get(Creature.instance)
    except Exception as e:
        msg = f'{h} Instance({instanceid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Instance.id is None:
            msg = f'{h} Instance({instanceid}) not found'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # Check if PC is the last inside the instance
    try:
        instance = Instance.id.replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@instance:{instance}')

        # Check if they are players or monsters left
        if len(Creatures) > 1:
            pc_in_instance = 0
            for creature_in_instance in Creatures:
                if creature_in_instance['account'] is not None:
                    # This is a PC
                    pc_in_instance += 1
    except Exception as e:
        msg = f'{h} PCs query failed (instanceid:{instanceid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if len(Creatures) == 1 or pc_in_instance == 1:
        logger.trace(f'{h} PC is the last inside OR the last player inside')
        # The PC is the last inside OR the last player inside
        # We delete the instance
        try:
            Creature.instance = None
            Instance.destroy(Instance.id)
        except Exception as e:
            msg = f'{h} Instance({instanceid}) leave KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            pass

        try:
            # We need to kill all NPC inside the instance
            for creature_inside in Creatures:
                if creature_inside['id'] == Creature.id:
                    # We do nothing, it is a Player Creature
                    pass
                else:
                    logger.trace(f'{h} Leaving EMPTY Instance({Instance.id})')
                    Monster = RedisCreature().get(
                        creature_inside['id']
                        )
                    # We delete Stats
                    try:
                        RedisStats(Monster).destroy()
                    except Exception as e:
                        msg = f'{h} CreatureStats delete KO [{e}]'
                        logger.error(msg)
                    else:
                        msg = f'{h} CreatureStats delete OK'
                        logger.trace(msg)
                    # We put the info in pubsub channel
                    # for IA to regulate the instance
                    try:
                        pmsg     = {"action": 'kill',
                                    "instance": Instance._asdict(),
                                    "creature": Monster._asdict()}
                        pchannel = 'ai-creature'
                        publish(pchannel, jsonify(pmsg).get_data())
                    except Exception as e:
                        msg = f'{h} Publish({pchannel}) KO [{e}]'
                        logger.error(msg)
                    else:
                        pass
                    # We kill it
                    # ALWAYS KILL CREATURE THE LAST
                    try:
                        RedisCreature().destroy(Monster.id)
                    except Exception as e:
                        msg = f'{h} Creature delete KO [{e}]'
                        logger.error(msg)
                    else:
                        msg = f'{h} Creature delete OK'
                        logger.trace(msg)

            # Redis Object deletion
            try:
                RedisInstance().destroy(instanceid)
            except Exception as e:
                logger.error(f'{h} Instance({instanceid}) destroy KO [{e}]')
            else:
                logger.trace(f'{h} Instance({instanceid}) destroy OK')
        except Exception as e:
            msg = f'{h} Instance({instanceid}) leave KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # Everything went well, deletion DONE
            # We put the info in queue for Discord
            scopes = []
            if Creature.korp is not None:
                scopes.append(f'Korp-{Creature.korp}')
            if Creature.squad is not None:
                scopes.append(f'Squad-{Creature.squad}')
            for scope in scopes:
                # Discord Queue
                yqueue_put(
                    YQ_DISCORD,
                    {
                        "ciphered": False,
                        "payload": (
                            f':map: **[{Creature.id}] {Creature.name}** '
                            f'closed an Instance ({instance.id})'
                            ),
                        "embed": None,
                        "scope": scope,
                        }
                    )
            # Finally everything is done
            msg = f'{h} Instance({instanceid}) leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Creature._asdict(),
                }
            ), 200
    else:
        # Other PC are still in the instance
        logger.trace(f'{h} Not the last in Instance (pcs:{pc_in_instance})')
        try:
            Creature.instance = None
        except Exception as e:
            msg = f'{h} Instance({instanceid}) leave KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            # We put the info in queue for Discord
            scopes = []
            if Creature.korp is not None:
                scopes.append(f'Korp-{Creature.korp}')
            if Creature.squad is not None:
                scopes.append(f'Squad-{Creature.squad}')
            for scope in scopes:
                # Discord Queue
                yqueue_put(
                    YQ_DISCORD,
                    {
                        "ciphered": False,
                        "payload": (
                            f':map: **[{Creature.id}] {Creature.name}** '
                            f'left an Instance ({Instance.id})'
                            ),
                        "embed": None,
                        "scope": scope,
                        }
                    )

            msg = f'{h} Instance({instanceid}) leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Creature._asdict(),
                }
            ), 200
