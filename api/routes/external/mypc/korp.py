# -*- coding: utf8 -*-

from flask                      import g, jsonify, request
from flask_jwt_extended         import jwt_required
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisKorp     import RedisKorp
from nosql.queue                import yqueue_put

from utils.decorators import (
    check_creature_exists,
    check_creature_in_korp,
    check_is_json,
    check_korp_exists,
    )

from variables                  import YQ_BROADCAST, YQ_DISCORD


#
# Routes ../korp
#
# API: POST ../korp/<uuid:korpuuid>/accept
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
@check_creature_in_korp
def korp_accept(creatureuuid, korpuuid):
    if g.Creature.korp_rank != 'Pending':
        msg = f'{g.h} Korp pending is required KorpUUID({g.Korp.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.korp = None
        g.Creature.korp_rank = 'Member'
    except Exception as e:
        msg = f'{g.h} Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
                "payload": g.Korp.as_dict(),
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
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
                    f'joined this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{g.Creature.korp}',
                }
            )
        msg = f'{g.h} Korp accept OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Korp.as_dict(),
            }
        ), 200


# API: POST ../korp
@jwt_required()
@check_is_json
# Custom decorators
@check_creature_exists
def korp_create(creatureuuid):
    korpname = request.json.get('name', None)

    if g.Creature.korp is not None:
        msg = f'{g.h} Already in a Korp'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Korp = RedisKorp().new(creatureuuid=g.Creature.id, korpname=korpname)
    except Exception as e:
        msg = f'{g.h} Korp Query KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Korp is False:
            msg = f'{g.h} Korp Query KO - Already exists'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # Korp created, let's assign the team creator in the korp
    try:
        g.Creature.korp = Korp.id
        g.Creature.korp_rank = 'Leader'
    except Exception as e:
        msg = f'{g.h} Korp Query KO (korpuuid:{Korp.id}) [{e}]'
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
                "payload": Korp.as_dict(),
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
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
                    f'created this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{g.Creature.korp}',
                }
            )

        msg = f'{g.h} Korp create OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Korp.as_dict(),
            }
        ), 201


# API: POST ../korp/<uuid:korpuuid>/decline
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
@check_creature_in_korp
def korp_decline(creatureuuid, korpuuid):
    if g.Creature.korp_rank == 'Leader':
        msg = f'{g.h} PC cannot be the korp Leader KorpUUID({g.Korp.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.korp_rank = None
        g.Creature.korp = None
    except Exception as e:
        msg = f'{g.h} Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
                "payload": g.Korp.as_dict(),
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
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
                    f'declined this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{g.Creature.korp}',
                }
            )

        msg = f'{g.h} Korp decline OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Korp.as_dict(),
            }
        ), 200


# API: DELETE ../korp/<uuid:korpuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
def korp_delete(creatureuuid, korpuuid):
    if g.Creature.korp_rank != 'Leader':
        msg = f'{g.h} Not the korp Leader ({g.Creature.korp_rank})'
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
            f"@korp:{g.Korp.id.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{g.h} Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
        msg = f'{g.h} Korp not empty (members:{count})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        RedisKorp(korpuuid=korpuuid).destroy()
        g.Creature.korp = None
        g.Creature.korp_rank = None
    except Exception as e:
        msg = f'Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
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
                    f'deleted this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{g.Korp.id}',
                }
            )

        msg = f'{g.h} Korp delete OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200


# API: GET ../korp/<uuid:korpuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
def korp_get_one(creatureuuid, korpuuid):
    try:
        KorpMembers = RedisSearch().creature(
            f"@korp:{g.Korp.id.replace('-', ' ')} & "
            f"(@korp_rank:-Pending)"
            ).results
        KorpPending = RedisSearch().creature(
            f"(@korp:{g.Korp.id.replace('-', ' ')}) & "
            f"(@korp_rank:Pending)"
            ).results
    except Exception as e:
        msg = f'Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Korp Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": {
                    "members": [
                        Creature.as_dict() for Creature in KorpMembers
                        ],
                    "pending": [
                        Creature.as_dict() for Creature in KorpPending
                        ],
                    "korp": g.Korp.as_dict(),
                    }
            }
        ), 200


# API: POST ../korp/<uuid:korpuuid>/invite/<uuid:targetuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
def korp_invite(creatureuuid, korpuuid, targetuuid):
    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if g.Creature.korp_rank != 'Leader':
        msg = f'{g.h} PC should be the korp Leader KorpUUID({g.Korp.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.korp is not None:
        msg = f'{g.h} Already in Korp (korpuuid:{CreatureTarget.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Korp population check
    try:
        Members = RedisSearch().creature(
            f"@korp:{g.Creature.korp.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{g.h} Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
        msg = f'{g.h} Korp Full (korpuuid:{korpuuid},members:{members})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        CreatureTarget.korp = str(korpuuid)
        CreatureTarget.korp_rank = 'Pending'
    except Exception as e:
        msg = f'{g.h} Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
                "payload": g.Korp.as_dict(),
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
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
                    f'in this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{g.Creature.korp}',
                }
            )

        msg = f'{g.h} Korp invite OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Korp.as_dict(),
            }
        ), 200


# API: POST ../korp/<uuid:korpuuid>/kick/<uuid:targetuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
@check_creature_in_korp
def korp_kick(creatureuuid, korpuuid, targetuuid):
    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if g.Creature.korp_rank != 'Leader':
        msg = f'{g.h} PC should be the korp Leader KorpUUID({g.Korp.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.korp is None:
        msg = f'{g.h} Should be in Korp (korpuuid:{CreatureTarget.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.id == g.Creature.id:
        msg = f'{g.h} Cannot kick yourself (korpuuid:{CreatureTarget.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        CreatureTarget.korp = None
        CreatureTarget.korp_rank = None
    except Exception as e:
        msg = f'{g.h} Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
                "payload": g.Korp.as_dict(),
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
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
                    f'from this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{g.Creature.korp}',
                }
            )

        msg = f'{g.h} Korp kick OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Korp.as_dict(),
            }
        ), 200


# API: ../korp/<uuid:korpuuid>/leave
@jwt_required()
# Custom decorators
@check_creature_exists
@check_korp_exists
@check_creature_in_korp
def korp_leave(creatureuuid, korpuuid):
    if g.Creature.korp_rank == 'Leader':
        msg = f'{g.h} PC cannot be the korp Leader KorpUUID({g.Korp.id})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        g.Creature.korp = None
        g.Creature.korp_rank = None
    except Exception as e:
        msg = f'{g.h} Korp Query KO KorpUUID({g.Korp.id}) [{e}]'
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
                "payload": g.Korp.as_dict(),
                "route": 'mypc/{id1}/korp',
                "scope": 'korp',
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
                    f'left this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{g.Creature.korp}',
                }
            )

        msg = f'{g.h} Korp leave OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": g.Korp.as_dict(),
            }
        ), 200
