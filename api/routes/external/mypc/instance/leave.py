# -*- coding: utf8 -*-

from flask                               import jsonify
from flask_jwt_extended                  import (jwt_required,
                                                 get_jwt_identity)
from loguru                              import logger

from nosql.publish                       import publish
from nosql.queue                         import yqueue_put
from nosql.models.RedisCreature          import RedisCreature
from nosql.models.RedisSearch            import RedisSearch
from nosql.models.RedisStats             import RedisStats

from utils.routehelper          import (
    creature_check,
    )

from variables                           import YQ_DISCORD


#
# Routes /mypc/<uuid:creatureuuid>/instance/*
#
# API: POST /mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>/leave
@jwt_required()
def leave(creatureuuid, instanceuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

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

    if Creature.instance != str(instanceuuid):
        msg = f'{h} Instance({instanceuuid}) is not Creature.instance'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Check if the Instance exists
    try:
        Instances = RedisSearch().instance(
            query=(
                f"@id:{str(instanceuuid).replace('-', ' ')}"
                )
        )
    except Exception as e:
        msg = f'{h} Instance({instanceuuid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if len(Instances.results) == 0:
            msg = f'{h} Instance({instanceuuid}) Query KO - NotFound'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            Instance = Instances.results[0]

    # Check if PC is the last inside the instance
    try:
        Creatures = RedisSearch().creature(
            query=(
                f"(@instance:{Instance.id.replace('-', ' ')})"
                )
            )
        Players = [
            Creature for Creature in Creatures.results
            if Creature.account is not None
            ]
    except Exception as e:
        msg = f'{h} Instance({instanceuuid}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if len(Players) == 1:
        logger.debug(f'{h} Instance({instanceuuid}) Last Player inside')

        try:
            Creature.instance = None
        except Exception as e:
            msg = f'{h} Instance({instanceuuid}) Leave KO [{e}]'
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

        # We need to kill all NPC inside the instance
        try:
            Monsters = RedisSearch().creature(
                query=(
                    f"(@instance:{Instance.id.replace('-', ' ')}) & "
                    f"(@account:None)"
                    )
                )

            for Monster in Monsters.results:
                logger.debug(f'{h} Instance({instanceuuid}) Cleaning Monster')
                RedisStats(creatureuuid=Monster.id).destroy()

                # We send in pubsub channel for IA to spawn the Mobs
                try:
                    pchannel = 'ai-creature'
                    publish(
                        pchannel,
                        jsonify(
                            {
                                "action": 'kill',
                                "instance": Instance.as_dict(),
                                "creature": Monster.as_dict(),
                                }
                            ).get_data(),
                            )
                except Exception as e:
                    msg = f'{h} Publish({pchannel}) KO [{e}]'
                    logger.error(msg)

                # We kill it
                # ALWAYS KILL CREATURE THE LAST
                Monster.destroy()

            Instance.destroy()
        except Exception as e:
            msg = f'{h} Instance({instanceuuid}) leave KO [{e}]'
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
                            f'closed an Instance ({Instance.id})'
                            ),
                        "embed": None,
                        "scope": scope,
                        }
                    )
            # Finally everything is done
            msg = f'{h} Instance({instanceuuid}) leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Creature.as_dict(),
                }
            ), 200
    else:
        # Other PC are still in the instance
        logger.debug(
            f'{h} Not the last in Instance (pcs:{len(Players)})'
            )
        try:
            Creature.instance = None
        except Exception as e:
            msg = f'{h} Instance({instanceuuid}) leave KO [{e}]'
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

            msg = f'{h} Instance({instanceuuid}) Leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Creature.as_dict(),
                }
            ), 200
