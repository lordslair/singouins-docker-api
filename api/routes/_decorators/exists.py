# -*- coding: utf8 -*-

import functools

from flask import g, jsonify, request
from flask_jwt_extended import get_jwt_identity
from loguru import logger

from mongo.models.Creature import CreatureDocument
from mongo.models.Instance import InstanceDocument
from mongo.models.Item import ItemDocument
from mongo.models.Korp import KorpDocument
from mongo.models.Squad import SquadDocument
from mongo.models.User import UserDocument

from utils.redis import consume_pa, get_pa


def creature(func):
    """ Decorator to check if a Creature exists in DB or not. """
    @functools.wraps(func)
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

    return wrapper


def instance(func):
    """ Decorator to check if an Instance exists in DB or not. """
    @functools.wraps(func)
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

    return wrapper


def item(func):
    """ Decorator to check if an Item exists in DB or not. """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        itemuuid = str(kwargs.get('itemuuid'))

        if ItemDocument.objects(_id=itemuuid):
            g.Item = ItemDocument.objects.get(_id=itemuuid)
            logger.trace(f'[Item.id:{g.Item.id}] Item FOUND')
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

    return wrapper


def korp(func):
    """ Decorator to check if a Korp exists in DB or not. """
    @functools.wraps(func)
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

    return wrapper


def pa(red=0, blue=0, consume=False):
    """
    Decorator to check if g.Creature has an amount of PA(red, blue).
    If asked, it will consume the PA too.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for color, required in [('red', red), ('blue', blue)]:
                if get_pa(creatureuuid=g.Creature.id)[color]['pa'] < required:
                    return jsonify({
                        "success": False,
                        "msg": f"{g.h} Not enough PA({color}) for this action",
                        "payload": get_pa(creatureuuid=g.Creature.id),
                    }), 200

            logger.trace(f'[Creature.id:{g.Creature.id}] has enough PA for this action')

            if consume is True and g.Creature.instance:
                # We consume the PA
                consume_pa(creatureuuid=g.Creature.id, bluepa=blue, redpa=red)

            return func(*args, **kwargs)
        return wrapper
    return decorator


def squad(func):
    """ Decorator to check if a Squad exists in DB or not. """
    @functools.wraps(func)
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

    return wrapper


def user(func):
    """ Decorator to check if a User exists in DB or not
    using the provided username in jwt_identity(). """
    @functools.wraps(func)
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

    return wrapper


def json(func):
    """ Decorator to check if received body is well formated JSON. """
    @functools.wraps(func)
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
