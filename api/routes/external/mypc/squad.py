# -*- coding: utf8 -*-

from flask                      import jsonify
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisSquad    import RedisSquad
from nosql.queue                import yqueue_put

from utils.routehelper          import (
    creature_check,
    )

from variables                  import YQ_BROADCAST, YQ_DISCORD


#
# Routes ../squad
#
# API: POST ../squad/<uuid:squaduuid>/accept
@jwt_required()
def squad_accept(creatureuuid, squaduuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.squad != str(squaduuid):
        msg = f'{h} Squad request outside your scope (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.squad_rank != 'Pending':
        msg = f'{h} Squad pending is required (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Creature.squad = None
        Creature.squad_rank = 'Member'
    except Exception as e:
        msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            Squad = RedisSquad(squaduuid=squaduuid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'joined this Squad'
                        ),
                    "embed": None,
                    "scope": f'Squad-{Creature.squad}',
                    }
                )
            msg = f'{h} Squad accept OK (squaduuid:{squaduuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Squad.as_dict(),
                }
            ), 200


# API: POST ../squad
@jwt_required()
def squad_create(creatureuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.squad is not None:
        msg = f'{h} PC already in a Squad (squaduuid:{Creature.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Squad = RedisSquad().new(creatureuuid=Creature.id)
    except Exception as e:
        msg = f'{h} Squad Query KO [{e}]'
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
            msg = f'{h} Squad Query KO - Already exists'
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
        Creature.squad = Squad.id
        Creature.squad_rank = 'Leader'
    except Exception as e:
        msg = f'{h} Squad Query KO (squaduuid:{Squad.id}) [{e}]'
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
                    f'**{Creature.name}** '
                    f'created this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{Creature.squad}',
                }
            )

        msg = f'{h} Squad create OK (squaduuid:{Creature.squad})'
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
def squad_decline(creatureuuid, squaduuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.squad != str(squaduuid):
        msg = f'{h} Squad request outside your scope (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.squad_rank == 'Leader':
        msg = f'{h} PC cannot be the squad Leader (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Creature.squad_rank = None
        Creature.squad = None
    except Exception as e:
        msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            Squad = RedisSquad(squaduuid=squaduuid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'declined this Squad'
                        ),
                    "embed": None,
                    "scope": f'Squad-{Creature.squad}',
                    }
                )

            msg = f'{h} Squad decline OK (squaduuid:{squaduuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Squad.as_dict(),
                }
            ), 200


# API: DELETE ../squad/<uuid:squaduuid>
@jwt_required()
def squad_delete(creatureuuid, squaduuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.squad != str(squaduuid):
        msg = f'{h} Squad request outside your scope (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.squad_rank != 'Leader':
        msg = f'{h} Not the squad Leader (squaduuid:{Creature.squad_rank})'
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
            f"@squad:{Creature.squad.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'Creature Query KO (squaduuid:{squaduuid}) [{e}]'
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
        msg = f'Squad not empty (squaduuid:{squaduuid},members:{count})'
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
        Creature.squad = None
        Creature.squad_rank = None
    except Exception as e:
        msg = f'Squad Query KO (squaduuid:{squaduuid}) [{e}]'
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
                    f'**{Creature.name}** '
                    f'deleted this Squad'
                    ),
                "embed": None,
                "scope": f'Squad-{Creature.squad}',
                }
            )

        msg = f'{h} Squad delete OK (squaduuid:{squaduuid})'
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
def squad_get_one(creatureuuid, squaduuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.squad != str(squaduuid):
        msg = f'{h} Squad request outside your scope (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Squad = RedisSquad(squaduuid=squaduuid)
        SquadMembers = RedisSearch().creature(
            f"@squad:{Creature.squad.replace('-', ' ')} & "
            f"(@squad_rank:-Pending)"
            ).results
        SquadPending = RedisSearch().creature(
            f"(@squad:{Creature.squad.replace('-', ' ')}) & "
            f"(@squad_rank:Pending)"
            ).results
    except Exception as e:
        msg = f'Squad Query KO (squaduuid:{squaduuid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Squad.id:
            msg = f'{h} Squad Query OK (squaduuid:{squaduuid})'
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
                        "squad": Squad.as_dict(),
                        }
                }
            ), 200
        else:
            msg = f'{h} Squad Query KO - Failed (squaduuid:{squaduuid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST ../squad/<uuid:squaduuid>/invite/<uuid:targetuuid>
@jwt_required()
def squad_invite(creatureuuid, squaduuid, targetuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if Creature.squad != str(squaduuid):
        msg = f'{h} Squad request outside your scope (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.squad_rank != 'Leader':
        msg = f'{h} PC should be the squad Leader (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.squad is not None:
        msg = f'{h} Already in Squad (squaduuid:{CreatureTarget.squad})'
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
            f"@squad:{Creature.squad.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
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
        msg = f'{h} Squad Full (squaduuid:{squaduuid},members:{members})'
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
        msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            Squad = RedisSquad(squaduuid=squaduuid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'invited '
                        f'**{CreatureTarget.name}** '
                        f'in this Squad'
                        ),
                    "embed": None,
                    "scope": f'Squad-{Creature.squad}',
                    }
                )

            msg = f'{h} Squad invite OK (squaduuid:{squaduuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Squad.as_dict(),
                }
            ), 200


# API: POST ../squad/<uuid:squaduuid>/kick/<uuid:targetuuid>
@jwt_required()
def squad_kick(creatureuuid, squaduuid, targetuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if Creature.squad != str(squaduuid):
        msg = f'{h} Squad request outside your scope (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.squad_rank != 'Leader':
        msg = f'{h} PC should be the squad Leader (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.squad is None:
        msg = f'{h} Should be in Squad (squaduuid:{CreatureTarget.squad})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.id == Creature.id:
        msg = f'{h} Cannot kick yourself (squaduuid:{CreatureTarget.squad})'
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
        msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            Squad = RedisSquad(squaduuid=squaduuid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'kicked '
                        f'**{CreatureTarget.name}** '
                        f'from this Squad'
                        ),
                    "embed": None,
                    "scope": f'Squad-{Creature.squad}',
                    }
                )

            msg = f'{h} Squad kick OK (squaduuid:{squaduuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Squad.as_dict(),
                }
            ), 200


# API: ../squad/<uuid:squaduuid>/leave
@jwt_required()
def squad_leave(creatureuuid, squaduuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.squad != str(squaduuid):
        msg = f'{h} Squad request outside your scope (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.squad_rank == 'Leader':
        msg = f'{h} PC cannot be the squad Leader (squaduuid:{squaduuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Creature.squad = None
        Creature.squad_rank = None
    except Exception as e:
        msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            Squad = RedisSquad(squaduuid=squaduuid)
        except Exception as e:
            msg = f'{h} Squad Query KO (squaduuid:{squaduuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'left this Squad'
                        ),
                    "embed": None,
                    "scope": f'Squad-{Creature.squad}',
                    }
                )

            msg = f'{h} Squad leave OK (squaduuid:{squaduuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Squad.as_dict(),
                }
            ), 200
