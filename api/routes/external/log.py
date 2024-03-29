# -*- coding: utf8 -*-

from flask              import jsonify, request
from loguru             import logger


#
# Routes /log
#
# API: POST /log
def front():
    if not request.is_json:
        msg = 'Missing JSON in request'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 400

    log_level     = request.json.get('level', None)
    log_msg_short = request.json.get('short_message', None)

    try:
        if log_level == 1:
            logger.critical(log_msg_short)
        elif log_level == 2:
            logger.error(log_msg_short)
        elif log_level == 3:
            logger.warning(log_msg_short)
        elif log_level == 4:
            logger.success(log_msg_short)
        elif log_level == 5:
            logger.info(log_msg_short)
        elif log_level == 6:
            logger.debug(log_msg_short)
        elif log_level == 7:
            logger.trace(log_msg_short)
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "msg": f'Logging KO [{e}]',
                "payload": None,
            }
        ), 200
    else:
        return jsonify(
            {
                "success": True,
                "msg": 'Logging OK',
                "payload": None,
            }
        ), 200
