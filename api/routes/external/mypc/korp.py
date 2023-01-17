# -*- coding: utf8 -*-

from flask                      import jsonify, request
from flask_jwt_extended         import (jwt_required,
                                        get_jwt_identity)
from loguru                     import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisKorp     import RedisKorp
from nosql.queue                import yqueue_put

from utils.routehelper          import (
    creature_check,
    request_json_check,
    )

from variables                  import YQ_BROADCAST, YQ_DISCORD

#
# Routes /mypc/{pcid}/korp
#


# API: POST /mypc/<uuid:pcid>/korp/<uuid:korpid>/accept
@jwt_required()
def korp_accept(pcid, korpid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    # We need to convert instanceid to STR as it is UUID type
    korpid = str(korpid)

    if Creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Pending':
        msg = f'{h} Korp pending is required (korpid:{korpid})'
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
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
            Korp = RedisKorp().get(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
                    "payload": Korp._asdict(),
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
            msg = f'{h} Korp accept OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp._asdict(),
                }
            ), 200


# API: POST /mypc/<uuid:pcid>/korp
@jwt_required()
def korp_create(pcid):
    request_json_check(request)

    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    korpname = request.json.get('name', None)

    if korpname is None:
        msg = f'{h} Korpname not found (korpname:{korpname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Remove everything, except alphanumeric, space, squote
    korpname = ''.join([c for c in korpname if c.isalnum() or c in [" ", "'"]])
    # Size check
    if len(korpname) > 16:
        msg = f'{h} Korp name too long (korpname:{korpname})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    if Creature.korp is not None:
        msg = f'{h} PC already in a Korp (korpid:{Creature.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Korp = RedisKorp().new(Creature, korpname)
    except Exception as e:
        msg = f'{h} Korp Query KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg": msg,
                        "payload": None}), 200
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
        msg = f'{h} Korp Query KO (korpid:{Korp.id}) [{e}]'
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
                "payload": Korp._asdict(),
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

        msg = f'{h} Korp create OK (korpid:{Creature.korp})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Korp._asdict(),
            }
        ), 201


# API: POST /mypc/<uuid:pcid>/korp/<uuid:korpid>/decline
@jwt_required()
def korp_decline(pcid, korpid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    # We need to convert instanceid to STR as it is UUID type
    korpid = str(korpid)

    if Creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank == 'Leader':
        msg = f'{h} PC cannot be the korp Leader (korpid:{korpid})'
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
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
            Korp = RedisKorp().get(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
                    "payload": Korp._asdict(),
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

            msg = f'{h} Korp decline OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp._asdict(),
                }
            ), 200


# API: DELETE /mypc/<uuid:pcid>/korp/<uuid:korpid>
@jwt_required()
def korp_delete(pcid, korpid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    # We need to convert instanceid to STR as it is UUID type
    korpid = str(korpid)

    if Creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Leader':
        msg = f'{h} PC is not the korp Leader (korpid:{Creature.korp_rank})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        korp = Creature.korp.replace('-', ' ')
        Members = RedisCreature().search(f"@korp:{korp}")
    except Exception as e:
        msg = f'Creature Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count = len(Members)
    if count > 1:
        msg = f'Korp not empty (korpid:{korpid},members:{count})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        RedisKorp().destroy(korpid)
        Creature.korp = None
        Creature.korp_rank = None
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
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

        msg = f'{h} Korp delete OK (korpid:{korpid})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200


# API: GET /mypc/{pcid}/korp/{korpid}
@jwt_required()
def korp_get_one(pcid, korpid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    # We need to convert instanceid to STR as it is UUID type
    korpid = str(korpid)

    if Creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Korp = RedisKorp().get(korpid)
        korp = Creature.korp.replace('-', ' ')
        KorpMembers = RedisCreature().search(
            f"(@korp:{korp}) & (@korp_rank:-Pending)"
            )
        KorpPending = RedisCreature().search(
            f"(@korp:{korp}) & (@korp_rank:Pending)"
            )
    except Exception as e:
        msg = f'Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if Korp:
            msg = f'{h} Korp Query OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": {
                        "members": KorpMembers,
                        "pending": KorpPending,
                        "korp": Korp._asdict(),
                        }
                }
            ), 200
        elif Korp is False:
            msg = f'{h} Korp Query KO - Not Found (korpid:{korpid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'{h} Korp Query KO - Failed (korpid:{korpid})'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200


# API: POST /mypc/<uuid:pcid>/korp/<uuid:korpid>/invite/<int:targetid>
@jwt_required()
def korp_invite(pcid, korpid, targetid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    CreatureTarget = RedisCreature(targetid)

    # We need to convert instanceid to STR as it is UUID type
    korpid = str(korpid)

    if Creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Leader':
        msg = f'{h} PC should be the korp Leader (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.korp is not None:
        msg = (
            f'{h} Already in Korp '
            f'(pcid:{CreatureTarget.id},korpid:{CreatureTarget.korp})'
            )
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
        korp = Creature.korp.replace('-', ' ')
        Members = RedisCreature().search(f"@korp:{korp}")
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    count      = len(Members)
    maxmembers = 100
    if count == maxmembers:
        members = f'{count}/{maxmembers}'
        msg = f'{h} Korp Full (korpid:{korpid},members:{members})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        CreatureTarget.korp = korpid
        CreatureTarget.korp_rank = 'Pending'
    except Exception as e:
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
            Korp = RedisKorp().get(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
                    "payload": Korp._asdict(),
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

            msg = f'{h} Korp invite OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp._asdict(),
                }
            ), 200


# API: POST /mypc/<uuid:pcid>/korp/<uuid:korpid>/kick/<int:targetid>
@jwt_required()
def korp_kick(pcid, korpid, targetid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    CreatureTarget = RedisCreature(targetid)

    # We need to convert instanceid to STR as it is UUID type
    korpid = str(korpid)

    if Creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank != 'Leader':
        msg = f'{h} PC should be the korp Leader (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.korp is None:
        msg = f'{h} Should be in Korp (korpid:{CreatureTarget.korp})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if CreatureTarget.id == Creature.id:
        msg = f'{h} Cannot kick yourself (korpid:{CreatureTarget.korp})'
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
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
            Korp = RedisKorp().get(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
                    "payload": Korp._asdict(),
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

            msg = f'{h} Korp kick OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp._asdict(),
                }
            ), 200


# API: /mypc/<uuid:pcid>/korp/<uuid:korpid>/leave
@jwt_required()
def korp_leave(pcid, korpid):
    Creature = RedisCreature(creatureuuid=pcid)
    h = creature_check(Creature, get_jwt_identity())

    # We need to convert instanceid to STR as it is UUID type
    korpid = str(korpid)

    if Creature.korp != korpid:
        msg = f'{h} Korp request outside of your scope (korpid:{korpid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    if Creature.korp_rank == 'Leader':
        msg = f'{h} PC cannot be the korp Leader (korpid:{korpid})'
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
        msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
            Korp = RedisKorp().get(korpid)
        except Exception as e:
            msg = f'{h} Korp Query KO (korpid:{korpid}) [{e}]'
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
                    "payload": Korp._asdict(),
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

            msg = f'{h} Korp leave OK (korpid:{korpid})'
            logger.debug(msg)
            return jsonify(
                {
                    "success": True,
                    "msg": msg,
                    "payload": Korp._asdict(),
                }
            ), 200
