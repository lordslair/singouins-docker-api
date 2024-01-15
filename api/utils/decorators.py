# -*- coding: utf8 -*-

from flask                      import g, jsonify, request
from flask_jwt_extended         import get_jwt_identity
from loguru                     import logger

from nosql.models.RedisUser     import RedisUser
from nosql.models.RedisCreature import RedisCreature


def check_creature_exists(func):
    """ Decorator to check if a Creature exists in DB or not. """
    def wrapper(*args, **kwargs):
        creatureuuid = kwargs.get('creatureuuid')
        if RedisCreature().exists(creatureuuid=creatureuuid):
            g.Creature = RedisCreature(creatureuuid=creatureuuid)
            logger.trace(f'[Creature.id:{g.Creature.id}] Creature FOUND')
            return func(*args, **kwargs)
        else:
            msg = f'[Creature.id:None] CreatureUUID({creatureuuid}) NOTFOUND'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    return wrapper


def check_creature_in_instance(func):
    """ Decorator to check if a Creature is in an Instance. """
    def wrapper(*args, **kwargs):
        if g.Creature.instance is None:
            msg = f'[Creature.id:{g.Creature.id}] Creature not in an instance'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            return func(*args, **kwargs)

    return wrapper


def check_creature_owned(func):
    """ Decorator to check if a Creature is owned by the User. """
    def wrapper(*args, **kwargs):
        if hasattr(g, 'User') and hasattr(g, 'Creature'):
            h = f'[Creature.id:{g.Creature.id}]'

            if g.Creature.account != g.User.id:
                msg = f'{h} Creature not owned by User({g.User.name})'
                logger.warning(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 409
            else:
                logger.trace(f'{h} Creature owned')
                return func(*args, **kwargs)
        else:
            logger.error(
                'Use this decorator after '
                '@check_user_exists and @check_creature_exists'
                )

    return wrapper


def check_is_json(func):
    """ Decorator to check if received body is well formated JSON. """
    def wrapper(*args, **kwargs):
        if not request.is_json:
            msg = '[API] Missing JSON in request'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 400
        else:
            return func(*args, **kwargs)

    return wrapper


def check_user_exists(func):
    """ Decorator to check if a User exists in DB or not
    using the provided username in jwt_identity(). """
    def wrapper(*args, **kwargs):
        if RedisUser().exists(username=get_jwt_identity()):
            g.User = RedisUser(username=get_jwt_identity())
            logger.trace(f'[User.id:{g.User.id}] User FOUND')
            return func(*args, **kwargs)
        else:
            msg = '[User.id:None] User NOTFOUND'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    return wrapper
