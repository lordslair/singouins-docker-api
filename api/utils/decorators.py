# -*- coding: utf8 -*-

from flask                      import g, jsonify, request
from flask_jwt_extended         import get_jwt_identity
from loguru                     import logger

from nosql.models.RedisUser     import RedisUser
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisKorp     import RedisKorp
from nosql.models.RedisSquad    import RedisSquad


def check_creature_exists(func):
    """ Decorator to check if a Creature exists in DB or not. """
    def wrapper(*args, **kwargs):
        creatureuuid = kwargs.get('creatureuuid')
        if RedisCreature().exists(creatureuuid=creatureuuid):
            g.Creature = RedisCreature(creatureuuid=creatureuuid)
            logger.trace(f'[Creature.id:{g.Creature.id}] Creature FOUND')
            g.h = f'[Creature.id:{g.Creature.id}]'
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

    # Renaming the function name:
    wrapper.__name__ = func.__name__
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

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper


def check_creature_in_korp(func):
    """ Decorator to check if g.Creature is in g.Korp """
    def wrapper(*args, **kwargs):
        if g.Creature.korp != g.Korp.id:
            msg = f'[Creature.id:{g.Creature.id}] Creature not in this Korp'
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

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper


def check_creature_in_squad(func):
    """ Decorator to check if g.Creature is in g.Squad """
    def wrapper(*args, **kwargs):
        if g.Creature.squad != g.Squad.id:
            msg = f'[Creature.id:{g.Creature.id}] Creature not in this Squad'
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

    # Renaming the function name:
    wrapper.__name__ = func.__name__
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

    # Renaming the function name:
    wrapper.__name__ = func.__name__
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

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper


def check_instance_exists(func):
    """ Decorator to check if an Instance exists in DB or not. """
    def wrapper(*args, **kwargs):
        instanceuuid = kwargs.get('instanceuuid')
        if RedisInstance().exists(instanceuuid=instanceuuid):
            g.Instance = RedisInstance(instanceuuid=instanceuuid)
            logger.trace(f'[Instance.id:{g.Instance.id}] Instance FOUND')
            return func(*args, **kwargs)
        else:
            msg = f'[Instance.id:None] InstanceUUID({instanceuuid}) NOTFOUND'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper


def check_item_exists(func):
    """ Decorator to check if an Item exists in DB or not. """
    def wrapper(*args, **kwargs):
        itemuuid = kwargs.get('itemuuid')
        if RedisItem().exists(itemuuid=itemuuid):
            g.Item = RedisItem(itemuuid=itemuuid)
            logger.trace(f'[Item.id:{g.Item.id}] Item FOUND')
            return func(*args, **kwargs)
        else:
            msg = f'[Item.id:None] ItemUUID({itemuuid}) NOTFOUND'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper


def check_korp_exists(func):
    """ Decorator to check if a Korp exists in DB or not. """
    def wrapper(*args, **kwargs):
        korpuuid = str(kwargs.get('korpuuid'))
        if RedisKorp().exists(korpuuid=korpuuid):
            g.Korp = RedisKorp(korpuuid=korpuuid)
            logger.trace(f'[Korp.id:{g.Korp.id}] Creature FOUND')
            g.h = f'[Korp.id:{g.Creature.id}]'
            return func(*args, **kwargs)
        else:
            msg = f'[Korp.id:None] KorpUUID({korpuuid}) NOTFOUND'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper


def check_squad_exists(func):
    """ Decorator to check if a Squad exists in DB or not. """
    def wrapper(*args, **kwargs):
        squaduuid = str(kwargs.get('squaduuid'))
        if RedisSquad().exists(squaduuid=squaduuid):
            g.Squad = RedisSquad(squaduuid=squaduuid)
            logger.trace(f'[Squad.id:{g.Squad.id}] Creature FOUND')
            g.h = f'[Squad.id:{g.Creature.id}]'
            return func(*args, **kwargs)
        else:
            msg = f'[Squad.id:None] SquadUUID({squaduuid}) NOTFOUND'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

    # Renaming the function name:
    wrapper.__name__ = func.__name__
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

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper
