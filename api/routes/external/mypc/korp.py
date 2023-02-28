# -*- coding: utf8 -*-

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch   import RedisSearch
from nosql.models.RedisKorp     import RedisKorp
from nosql.queue                import yqueue_put

from utils.routehelper          import (
    creature_check,
    request_json_check,
    )

from variables                  import YQ_BROADCAST, YQ_DISCORD


#
# Routes ../korp
#
# API: POST ../korp/<uuid:korpuuid>/accept
@jwt_required()
def korp_accept(creatureuuid, korpuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.korp != str(korpuuid):
        msg = f'{h} Korp request outside your scope (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Pending':
        msg = f'{h} Korp pending is required (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Creature.korp = None
        Creature.korp_rank = 'Member'
    except Exception as e:
        msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
            Korp = RedisKorp(korpuuid=korpuuid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'joined this Korp'
                        ),
                    "embed": None,
                    "scope": f'Korp-{Creature.korp}',
                    }
                )
            msg = f'{h} Korp accept OK (korpuuid:{korpuuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp.as_dict(),
                }
            ), 200


# API: POST ../korp
@jwt_required()
def korp_create(creatureuuid):
    request_json_check(request)

    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    korpname = request.json.get('name', None)

    if Creature.korp is not None:
        msg = f'{h} PC already in a Korp (korpuuid:{Creature.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Korp = RedisKorp().new(creatureuuid=Creature.id, korpname=korpname)
    except Exception as e:
        msg = f'{h} Korp Query KO [{e}]'
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
            msg = f'{h} Korp Query KO - Already exists'
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
        Creature.korp = Korp.id
        Creature.korp_rank = 'Leader'
    except Exception as e:
        msg = f'{h} Korp Query KO (korpuuid:{Korp.id}) [{e}]'
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
                    f'**{Creature.name}** '
                    f'created this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{Creature.korp}',
                }
            )

        msg = f'{h} Korp create OK (korpuuid:{Creature.korp})'
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
def korp_decline(creatureuuid, korpuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.korp != str(korpuuid):
        msg = f'{h} Korp request outside your scope (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank == 'Leader':
        msg = f'{h} PC cannot be the korp Leader (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Creature.korp_rank = None
        Creature.korp = None
    except Exception as e:
        msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
            Korp = RedisKorp(korpuuid=korpuuid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'declined this Korp'
                        ),
                    "embed": None,
                    "scope": f'Korp-{Creature.korp}',
                    }
                )

            msg = f'{h} Korp decline OK (korpuuid:{korpuuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp.as_dict(),
                }
            ), 200


# API: DELETE ../korp/<uuid:korpuuid>
@jwt_required()
def korp_delete(creatureuuid, korpuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.korp != str(korpuuid):
        msg = f'{h} Korp request outside your scope (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Leader':
        msg = f'{h} Not the korp Leader (korpuuid:{Creature.korp_rank})'
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
            f"@korp:{Creature.korp.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'Creature Query KO (korpuuid:{korpuuid}) [{e}]'
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
        msg = f'Korp not empty (korpuuid:{korpuuid},members:{count})'
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
        Creature.korp = None
        Creature.korp_rank = None
    except Exception as e:
        msg = f'Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
                    f'**{Creature.name}** '
                    f'deleted this Korp'
                    ),
                "embed": None,
                "scope": f'Korp-{Creature.korp}',
                }
            )

        msg = f'{h} Korp delete OK (korpuuid:{korpuuid})'
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
def korp_get_one(creatureuuid, korpuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.korp != str(korpuuid):
        msg = f'{h} Korp request outside your scope (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Korp = RedisKorp(korpuuid=korpuuid)
        KorpMembers = RedisSearch().creature(
            f"@korp:{Creature.korp.replace('-', ' ')} & "
            f"(@korp_rank:-Pending)"
            ).results
        KorpPending = RedisSearch().creature(
            f"(@korp:{Creature.korp.replace('-', ' ')}) & "
            f"(@korp_rank:Pending)"
            ).results
    except Exception as e:
        msg = f'Korp Query KO (korpuuid:{korpuuid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Korp.id:
            msg = f'{h} Korp Query OK (korpuuid:{korpuuid})'
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
                        "korp": Korp.as_dict(),
                        }
                }
            ), 200
        else:
            msg = f'{h} Korp Query KO - Failed (korpuuid:{korpuuid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST ../korp/<uuid:korpuuid>/invite/<uuid:targetuuid>
@jwt_required()
def korp_invite(creatureuuid, korpuuid, targetuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if Creature.korp != str(korpuuid):
        msg = f'{h} Korp request outside your scope (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Leader':
        msg = f'{h} PC should be the korp Leader (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.korp is not None:
        msg = f'{h} Already in Korp (korpuuid:{CreatureTarget.korp})'
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
            f"@korp:{Creature.korp.replace('-', ' ')}"
            )
    except Exception as e:
        msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
        msg = f'{h} Korp Full (korpuuid:{korpuuid},members:{members})'
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
        msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
            Korp = RedisKorp(korpuuid=korpuuid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'invited '
                        f'**{CreatureTarget.name}** '
                        f'in this Korp'
                        ),
                    "embed": None,
                    "scope": f'Korp-{Creature.korp}',
                    }
                )

            msg = f'{h} Korp invite OK (korpuuid:{korpuuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp.as_dict(),
                }
            ), 200


# API: POST ../korp/<uuid:korpuuid>/kick/<uuid:targetuuid>
@jwt_required()
def korp_kick(creatureuuid, korpuuid, targetuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    CreatureTarget = RedisCreature(creatureuuid=targetuuid)

    if Creature.korp != str(korpuuid):
        msg = f'{h} Korp request outside your scope (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Leader':
        msg = f'{h} PC should be the korp Leader (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.korp is None:
        msg = f'{h} Should be in Korp (korpuuid:{CreatureTarget.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.id == Creature.id:
        msg = f'{h} Cannot kick yourself (korpuuid:{CreatureTarget.korp})'
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
        msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
            Korp = RedisKorp(korpuuid=korpuuid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'kicked '
                        f'**{CreatureTarget.name}** '
                        f'from this Korp'
                        ),
                    "embed": None,
                    "scope": f'Korp-{Creature.korp}',
                    }
                )

            msg = f'{h} Korp kick OK (korpuuid:{korpuuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp.as_dict(),
                }
            ), 200


# API: ../korp/<uuid:korpuuid>/leave
@jwt_required()
def korp_leave(creatureuuid, korpuuid):
    Creature = RedisCreature(creatureuuid=creatureuuid)
    h = creature_check(Creature, get_jwt_identity())

    if Creature.korp != str(korpuuid):
        msg = f'{h} Korp request outside your scope (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank == 'Leader':
        msg = f'{h} PC cannot be the korp Leader (korpuuid:{korpuuid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Creature.korp = None
        Creature.korp_rank = None
    except Exception as e:
        msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
            Korp = RedisKorp(korpuuid=korpuuid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpuuid:{korpuuid}) [{e}]'
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
                        f'**{Creature.name}** '
                        f'left this Korp'
                        ),
                    "embed": None,
                    "scope": f'Korp-{Creature.korp}',
                    }
                )

            msg = f'{h} Korp leave OK (korpuuid:{korpuuid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp.as_dict(),
                }
            ), 200
