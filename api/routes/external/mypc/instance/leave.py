# -*- coding: utf8 -*-

import datetime
import json

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger
from mongoengine import Q

from mongo.models.Creature import CreatureDocument

from nosql.connector import r

from utils.decorators import (
    check_creature_exists,
    check_creature_in_instance,
    )
from utils.queue import qput
from variables import YQ_DISCORD


# API: POST /mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>/leave
@jwt_required()
# Custom decorators
@check_creature_exists
@check_creature_in_instance
def leave(creatureuuid, instanceuuid):

    # Check if PC is the last inside the instance
    try:
        query_players = (
            Q(instance=g.Creature.instance) &
            Q(account__ne=None)
            )
        Players = CreatureDocument.objects.filter(query_players)

        query_monsters = (
            Q(instance=g.Creature.instance) &
            Q(account=None)
            )
        Monsters = CreatureDocument.objects.filter(query_monsters)
    except Exception as e:
        msg = f'{g.h} Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if Players.count() == 1:
        logger.trace(f'{g.h} Instance({g.Instance.id}) Last Player inside')

        try:
            g.Creature.instance = None
            g.Creature.x = None
            g.Creature.y = None
            g.Creature.updated = datetime.datetime.utcnow()
            g.Creature.save()
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

        # We need to kill all NPC inside the instance
        try:
            for Monster in Monsters:
                logger.trace(f'{g.h} Instance({g.Instance.id}) Cleaning')
                # We send in pubsub channel for IA to spawn the Mobs
                try:
                    r.publish(
                        'ai-creature',
                        json.dumps({
                            "action": 'kill',
                            "instance": g.Instance.to_json(),
                            "creature": Monster.to_json(),
                            }),
                        )
                except Exception as e:
                    msg = f'{g.h} Publish(ai-creature/kill) KO [{e}]'
                    logger.error(msg)

                # We kill it
                # ALWAYS KILL CREATURE THE LAST
                Monster.delete()

            g.Instance.delete()
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
            if hasattr(g.Creature.korp, 'id'):
                scopes.append(f'Korp-{g.Creature.korp.id}')
            if hasattr(g.Creature.korp, 'id'):
                scopes.append(f'Squad-{g.Creature.squad.id}')
            for scope in scopes:
                # Discord Queue
                qput(YQ_DISCORD, {
                    "ciphered": False,
                    "payload": f':map: **{g.Creature.name}** closed an Instance',
                    "embed": None,
                    "scope": scope})
            # Finally everything is done
            msg = f'{g.h} Instance({g.Instance.id}) leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": g.Creature.to_mongo(),
                }
            ), 200
    else:
        # Other PC are still in the instance
        logger.debug(f'{g.h} Not the last in Instance (pcs:{Players.count()})')
        try:
            g.Creature.instance = None
            g.Creature.x = None
            g.Creature.y = None
            g.Creature.updated = datetime.datetime.utcnow()
            g.Creature.save()
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
            if hasattr(g.Creature.korp, 'id'):
                scopes.append(f'Korp-{g.Creature.korp.id}')
            if hasattr(g.Creature.korp, 'id'):
                scopes.append(f'Squad-{g.Creature.squad.id}')
            for scope in scopes:
                # Discord Queue
                qput(YQ_DISCORD, {
                    "ciphered": False,
                    "payload": f':map: **{g.Creature.name}** left an Instance',
                    "embed": None,
                    "scope": scope})

            msg = f'{g.h} Instance({g.Instance.id}) Leave OK'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": g.Creature.to_mongo(),
                }
            ), 200
