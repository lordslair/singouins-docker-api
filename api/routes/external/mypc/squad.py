# -*- coding: utf8 -*-

from flask                      import g, jsonify
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSquad     import RedisSquad
from nosql.queue                import yqueue_put

from utils.decorators import (
    check_creature_exists,
    check_creature_in_squad,
    check_squad_exists,
    )

from variables                  import YQ_BROADCAST, YQ_DISCORD


#
# Routes ../squad
#
# API: POST ../squad/<uuid:squaduuid>/accept
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
@check_creature_in_squad
def squad_accept(creatureuuid, squaduuid):
    if g.Creature.squad_rank != 'Pending':
        msg = f'{g.h} Squad pending is required SquadUUID({g.Squad.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.squad = None
        g.Creature.squad_rank = 'Member'
    except Exception as e:
        msg = f'{g.h} Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": e,
            }
        ), 200
    else:
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": g.Squad.as_dict(),
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'joined this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Creature.squad}',
                }
            )
        msg = f'{g.h} Squad accept OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Squad.as_dict(),
            }
        ), 200


# API: POST ../squad
@jwt_required()
# Custom decorators
@check_creature_exists
def squad_create(creatureuuid):
    if g.Creature.squad is not None:
        msg = f'{g.h} Already in a Squad'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Squad = RedisSquad().new(creatureuuid=g.Creature.id)
    except Exception as e:
        msg = f'{g.h} Squad Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Squad is False:
            msg = f'{g.h} Squad Query KO - Already exists'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # Squad created, let's assign the team creator in the squad
    try:
        g.Creature.squad = Squad.id
        g.Creature.squad_rank = 'Leader'
    except Exception as e:
        msg = f'{g.h} Squad Query KO (squaduuid:{Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": Squad.as_dict(),
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'created this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Creature.squad}',
                }
            )

        msg = f'{g.h} Squad create OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Squad.as_dict(),
            }
        ), 201


# API: POST ../squad/<uuid:squaduuid>/decline
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
@check_creature_in_squad
def squad_decline(creatureuuid, squaduuid):
    if g.Creature.squad_rank == 'Leader':
        msg = f'{g.h} PC cannot be the squad Leader SquadUUID({g.Squad.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.squad_rank = None
        g.Creature.squad = None
    except Exception as e:
        msg = f'{g.h} Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": g.Squad.as_dict(),
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'declined this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Creature.squad}',
                }
            )

        msg = f'{g.h} Squad decline OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Squad.as_dict(),
            }
        ), 200


# API: DELETE ../squad/<uuid:squaduuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
def squad_delete(creatureuuid, squaduuid):
    if g.Creature.squad_rank != 'Leader':
        msg = f'{g.h} Not the squad Leader ({g.Creature.squad_rank})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Members = RedisSearch().creature(
            f"@squad:{g.Squad.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{g.h} Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count = len(Members.results)
    if count > 1:
        msg = f'{g.h} Squad not empty (members:{count})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        RedisSquad(squaduuid=squaduuid).destroy()
        g.Creature.squad = None
        g.Creature.squad_rank = None
    except Exception as e:
        msg = f'Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": None,
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'deleted this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Squad.id}',
                }
            )

        msg = f'{g.h} Squad delete OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200


# API: GET ../squad/<uuid:squaduuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
def squad_get_one(creatureuuid, squaduuid):
    try:
        SquadMembers = RedisSearch().creature(
            f"@squad:{g.Squad.id.replace('-', ' ')} & "
            f"(@squad_rank:-Pending)"
            ).results
        SquadPending = RedisSearch().creature(
            f"(@squad:{g.Squad.id.replace('-', ' ')}) & "
            f"(@squad_rank:Pending)"
            ).results
    except Exception as e:
        msg = f'Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Squad Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "members": [
                        Creature.as_dict() for Creature in SquadMembers
                        ],
                    "pending": [
                        Creature.as_dict() for Creature in SquadPending
                        ],
                    "squad": g.Squad.as_dict(),
                    }
            }
        ), 200


# API: POST ../squad/<uuid:squaduuid>/invite/<uuid:targetuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
def squad_invite(creatureuuid, squaduuid, targetuuid):
    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if g.Creature.squad_rank != 'Leader':
        msg = f'{g.h} PC should be the squad Leader SquadUUID({g.Squad.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.squad is not None:
        msg = f'{g.h} Already in Squad (squaduuid:{CreatureTarget.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Squad population check
    try:
        Members = RedisSearch().creature(
            f"@squad:{g.Creature.squad.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{g.h} Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count      = len(Members.results)
    maxmembers = 100
    if count == maxmembers:
        members = f'{count}/{maxmembers}'
        msg = f'{g.h} Squad Full (squaduuid:{squaduuid},members:{members})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        CreatureTarget.squad = str(squaduuid)
        CreatureTarget.squad_rank = 'Pending'
    except Exception as e:
        msg = f'{g.h} Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": g.Squad.as_dict(),
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'invited '
                    f'**{CreatureTarget.name}** '
                    f'in this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Creature.squad}',
                }
            )

        msg = f'{g.h} Squad invite OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Squad.as_dict(),
            }
        ), 200


# API: POST ../squad/<uuid:squaduuid>/kick/<uuid:targetuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
@check_creature_in_squad
def squad_kick(creatureuuid, squaduuid, targetuuid):
    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if g.Creature.squad_rank != 'Leader':
        msg = f'{g.h} PC should be the squad Leader SquadUUID({g.Squad.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.squad is None:
        msg = f'{g.h} Should be in Squad (squaduuid:{CreatureTarget.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.id == g.Creature.id:
        msg = f'{g.h} Cannot kick yourself (squaduuid:{CreatureTarget.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        CreatureTarget.squad = None
        CreatureTarget.squad_rank = None
    except Exception as e:
        msg = f'{g.h} Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": g.Squad.as_dict(),
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'kicked '
                    f'**{CreatureTarget.name}** '
                    f'from this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Creature.squad}',
                }
            )

        msg = f'{g.h} Squad kick OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Squad.as_dict(),
            }
        ), 200


# API: ../squad/<uuid:squaduuid>/leave
@jwt_required()
# Custom decorators
@check_creature_exists
@check_squad_exists
@check_creature_in_squad
def squad_leave(creatureuuid, squaduuid):
    if g.Creature.squad_rank == 'Leader':
        msg = f'{g.h} PC cannot be the squad Leader SquadUUID({g.Squad.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.squad = None
        g.Creature.squad_rank = None
    except Exception as e:
        msg = f'{g.h} Squad Query KO SquadUUID({g.Squad.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
                "ciphered": False,
                "payload": g.Squad.as_dict(),
                "route": 'mypc/{id1}/squad',
                "scope": 'squad',
                }
            )
        # Discord Queue
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':information_source: '
                    f'**{g.Creature.name}** '
                    f'left this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{g.Creature.squad}',
                }
            )

        msg = f'{g.h} Squad leave OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Squad.as_dict(),
            }
        ), 200
