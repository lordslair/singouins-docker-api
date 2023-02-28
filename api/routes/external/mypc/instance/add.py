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

from utils.routehelper          import (
    creature_check,
    request_json_check,
    )

from variables                           import YQ_DISCORD


#
# Routes /mypc/<uuid:creatureuuid>/instance/*
#
# API: PUT /mypc/<uuid:creatureuuid>/instance
@jwt_required()
def add(creatureuuid):
    request_json_check(request)

    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

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
        Instance = RedisInstance().new(instance=instance_dict)
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
        Creature.instance = Instance.id
    except Exception as e:
        msg = f'{h} Instance({Instance.id}) Query KO [{e}]'
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
                    f'opened an Instance ({Instance.id})'
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
                    name=metaNames['race'][raceid]['name'],
                    raceid=raceid,
                    gender=gender,
                    accountuuid=None,
                    rarity=rarity,
                    x=x,
                    y=y,
                    instanceuuid=Instance.id,
                    )
                RedisStats().new(Creature=Monster, classid=None)
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
                    # We send in pubsub channel for IA to spawn the Mobs
                    try:
                        pchannel = 'ai-creature'
                        publish(
                            pchannel,
                            jsonify(
                                {
                                    "action": 'pop',
                                    "instance": Instance.as_dict(),
                                    "creature": Monster.as_dict(),
                                    }
                                ).get_data(),
                                )
                    except Exception as e:
                        msg = f'{h} Publish({pchannel}) KO [{e}]'
                        logger.error(msg)
                    else:
                        pass

            mobs_nbr += 1
    except Exception as e:
        msg = f'{h} Instance({Instance.id}) Population KO [{e}]'
        logger.error(msg)
    else:
        if len(mobs_generated) > 0:
            msg = (f'{h} Instance({Instance.id}) Population OK '
                   f'(mobs:{len(mobs_generated)})')
            logger.trace(msg)
        else:
            msg = f'{h} Instance({Instance.id}) Population KO'
            logger.error(msg)
    # Finally everything is done
    msg = f'{h} Instance({Instance.id}) Create OK'
    logger.debug(msg)
    return jsonify(
        {
            "success": True,
            "msg": msg,
            "payload": Instance.as_dict(),
        }
    ), 201
