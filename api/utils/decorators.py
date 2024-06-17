# -*- coding: utf8 -*-

from flask import g, jsonify, request
from flask_jwt_extended import get_jwt_identity
from loguru import logger

from nosql.models.RedisPa         import RedisPa

from mongo.models.Creature import CreatureDocument
from mongo.models.Instance import InstanceDocument
from mongo.models.Item import ItemDocument
from mongo.models.Korp import KorpDocument
from mongo.models.Squad import SquadDocument
from mongo.models.User import UserDocument


def check_creature_exists(func):
    """ Decorator to check if a Creature exists in DB or not. """
    def wrapper(*args, **kwargs):
        creatureuuid = kwargs.get('creatureuuid')
        if CreatureDocument.objects(_id=creatureuuid).count() > 0:
            g.Creature = CreatureDocument.objects(_id=creatureuuid).get()
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
        try:
            if hasattr(g.Creature, 'instance'):
                logger.trace(f'[Creature.id:{g.Creature.id}] Creature in an Instance')
            else:
                msg = f'[Creature.id:{g.Creature.id}] Creature not in an Instance'
                logger.warning(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        except Exception as e:
            msg = f'[Creature.id:{g.Creature.id}] Query KO [{e}]'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

        try:
            if InstanceDocument.objects(_id=g.Creature.instance):
                g.Instance = InstanceDocument.objects(_id=g.Creature.instance).get()
                logger.trace(f'[Instance.id:{g.Instance.id}] InstanceDocument FOUND')
                return func(*args, **kwargs)
            else:
                msg = f'[Instance.id:None] InstanceUUID({g.Creature.instance}) NOTFOUND'
                logger.warning(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
        except Exception as e:
            msg = f'[Creature.id:{g.Creature.id}] Query KO [{e}]'
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


def check_creature_in_korp(func):
    """ Decorator to check if g.Creature is in g.Korp """
    def wrapper(*args, **kwargs):
        if hasattr(g.Creature.korp, 'id') is False:
            msg = f'[Creature.id:{g.Creature.id}] Creature not in a Korp'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

        if g.Creature.korp.id != g.Korp.id:
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
        if hasattr(g.Creature.squad, 'id') is False:
            msg = f'[Creature.id:{g.Creature.id}] Creature not in a Squad'
            logger.warning(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200

        if g.Creature.squad.id != g.Squad.id:
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

            if g.Creature.account != g.User._id:
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


def check_creature_pa(red=0, blue=0):
    """ Decorator to check if g.Creature has an amount of PA(red, blue) """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if RedisPa(creatureuuid=g.Creature.id).bluepa < blue:
                msg = f'{g.h} Not enough PA(blue) for this action'
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": RedisPa(creatureuuid=g.Creature.id).as_dict(),
                    }
                ), 200
            elif RedisPa(creatureuuid=g.Creature.id).redpa < red:
                msg = f'{g.h} Not enough PA(red) for this action'
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": RedisPa(creatureuuid=g.Creature.id).as_dict(),
                    }
                ), 200
            else:
                return func(*args, **kwargs)

        # Renaming the function name:
        wrapper.__name__ = func.__name__
        return wrapper

    return decorator


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

        if InstanceDocument.objects(_id=instanceuuid):
            g.Instance = InstanceDocument.objects(_id=instanceuuid).get()
            logger.trace(f'[Instance.id:{g.Instance.id}] InstanceDocument FOUND')
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
        itemuuid = str(kwargs.get('itemuuid'))

        if ItemDocument.objects(_id=itemuuid):
            g.Item = ItemDocument.objects.get(_id=itemuuid)
            logger.trace(f'[Item.id:{g.Item.id}] ItemDocument FOUND')
            g.h = f'[Item.id:{g.Item.id}]'
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

        if KorpDocument.objects(_id=korpuuid):
            g.Korp = KorpDocument.objects(_id=korpuuid).get()
            logger.trace(f'[Korp.id:{g.Korp.id}] Korp FOUND')
            g.h = f'[Korp.id:{g.Korp.id}]'
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

        if SquadDocument.objects(_id=squaduuid):
            g.Squad = SquadDocument.objects(_id=squaduuid).get()
            logger.trace(f'[Squad.id:{g.Squad.id}] Squad FOUND')
            g.h = f'[Squad.id:{g.Squad.id}]'
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
        if UserDocument.objects(name=get_jwt_identity()).count() > 0:
            g.User = UserDocument.objects(name=get_jwt_identity()).get()
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
