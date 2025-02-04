# -*- coding: utf8 -*-

import functools

from flask import g, jsonify
from loguru import logger

from mongo.models.Instance import InstanceDocument


def creature_in_instance(func):
    """ Decorator to check if a Creature is in an Instance. """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if Creature.instance is filled
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

        # Check if Instance object exists in DB
        try:
            g.Instance = InstanceDocument.objects(_id=g.Creature.instance).get()
        except InstanceDocument.DoesNotExist:
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
        else:
            logger.trace(f'[Instance.id:{g.Instance.id}] InstanceDocument FOUND')
            return func(*args, **kwargs)

    return wrapper


def creature_in_korp(func):
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


def creature_in_squad(func):
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


def creature_in_user(func):
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
                '@user_exists and @creature_exists'
                )

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper


def item_to_creature(func):
    """ Decorator to check if an Item belongs to a Creature. """
    def wrapper(*args, **kwargs):
        if hasattr(g, 'Item') and hasattr(g, 'Creature'):
            h = f'[Item.id:{g.Item.id}]'

            if g.Creature.id != g.Item.bearer:
                msg = f'{h} Item not owned by Creature({g.Creature.id})'
                logger.warning(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 409
            else:
                logger.trace(f'{h} Item owned by Creature({g.Creature.id})')
                return func(*args, **kwargs)
        else:
            logger.error('Use this decorator after @exists.item and @exists.creature')

    # Renaming the function name:
    wrapper.__name__ = func.__name__
    return wrapper
