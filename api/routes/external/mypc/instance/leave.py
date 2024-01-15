# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                              import logger

from nosql.publish                       import publish
from nosql.queue                         import yqueue_put
from nosql.models.RedisSearch            import RedisSearch
from nosql.models.RedisStats             import RedisStats

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    check_instance_exists,
    )

from variables                           import YQ_DISCORD


#
# Routes /mypc/<uuid:creatureuuid>/instance/*
#
# API: POST /mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>/leave
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_in_instance
@check_instance_exists
def leave(creatureuuid, instanceuuid):
    if g.Creature.instance != g.Instance.id:
        msg = f'{g.h} Instance({g.Instance.id}) is not Creature.instance'
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
        Creatures = RedisSearch().creature(
            query=(
                f"(@instance:{g.Instance.id.replace('-', ' ')})"
                )
            )
        Players = [
            Creature for Creature in Creatures.results
            if g.Creature.account is not None
            ]
    except Exception as e:
        msg = f'{g.h} Instance({g.Instance.id}) Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if len(Players) == 1:
        logger.debug(f'{g.h} Instance({g.Instance.id}) Last Player inside')

        try:
            g.Creature.instance = None
        except Exception as e:
            msg = f'{g.h} Instance({g.Instance.id}) Leave KO [{e}]'
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
                    f"(@instance:{g.Instance.id.replace('-', ' ')}) & "
                    f"(@account:None)"
                    )
                )

            for Monster in Monsters.results:
                logger.debug(f'{g.h} Instance({g.Instance.id}) Cleaning')
                RedisStats(creatureuuid=Monster.id).destroy()

                # We send in pubsub channel for IA to spawn the Mobs
                try:
                    pchannel = 'ai-creature'
                    publish(
                        pchannel,
                        jsonify(
                            {
                                "action": 'kill',
                                "instance": g.Instance.as_dict(),
                                "creature": Monster.as_dict(),
                                }
                            ).get_data(),
                            )
                except Exception as e:
                    msg = f'{g.h} Publish({pchannel}) KO [{e}]'
                    logger.error(msg)

                # We kill it
                # ALWAYS KILL CREATURE THE LAST
                Monster.destroy()

            g.Instance.destroy()
        except Exception as e:
            msg = f'{g.h} Instance({g.Instance.id}) leave KO [{e}]'
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
            if g.Creature.korp is not None:
                scopes.append(f'Korp-{g.Creature.korp}')
            if g.Creature.squad is not None:
                scopes.append(f'Squad-{g.Creature.squad}')
            for scope in scopes:
                # Discord Queue
                yqueue_put(
                    YQ_DISCORD,
                    {
                        "ciphered": False,
                        "payload": (
                            f':map: **[{g.Creature.id}] {g.Creature.name}** '
                            f'closed an Instance ({g.Instance.id})'
                            ),
                        "embed": None,
                        "scope": scope,
                        }
                    )
            # Finally everything is done
            msg = f'{g.h} Instance({g.Instance.id}) leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": g.Creature.as_dict(),
                }
            ), 200
    else:
        # Other PC are still in the instance
        logger.debug(
            f'{g.h} Not the last in Instance (pcs:{len(Players)})'
            )
        try:
            g.Creature.instance = None
        except Exception as e:
            msg = f'{g.h} Instance({g.Instance.id}) leave KO [{e}]'
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
            if g.Creature.korp is not None:
                scopes.append(f'Korp-{g.Creature.korp}')
            if g.Creature.squad is not None:
                scopes.append(f'Squad-{g.Creature.squad}')
            for scope in scopes:
                # Discord Queue
                yqueue_put(
                    YQ_DISCORD,
                    {
                        "ciphered": False,
                        "payload": (
                            f':map: **[{g.Creature.id}] {g.Creature.name}** '
                            f'left an Instance ({g.Instance.id})'
                            ),
                        "embed": None,
                        "scope": scope,
                        }
                    )

            msg = f'{g.h} Instance({g.Instance.id}) Leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": g.Creature.as_dict(),
                }
            ), 200
