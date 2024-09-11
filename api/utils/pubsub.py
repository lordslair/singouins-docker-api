# -*- coding: utf8 -*-

from flask import jsonify

from loguru import logger

from nosql.connector import r


def cput(channel, msg):
    """ Put a new message (dict) into a specified PubSub channel. """
    try:
        logger.trace(f'Pubsub PUBLISH >> (channel:{channel})')
        r.publish(channel, jsonify(msg).get_data(as_text=True))
    except Exception as e:
        msg = (f'Pubsub PUBLISH KO (channel:{channel}) [{e}]')
        logger.error(msg)
    else:
        logger.trace(f'Pubsub PUBLISH OK (channel:{channel})')
