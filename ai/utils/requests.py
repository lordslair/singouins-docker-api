# -*- coding: utf8 -*-

import json
import os
import requests

from loguru import logger

from nosql.models.RedisSearch import RedisSearch

RESOLVER_HOST = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_HOST")
RESOLVER_PORT = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_PORT")
RESOLVER_URL  = f'http://{RESOLVER_HOST}:{RESOLVER_PORT}'


def resolver_generic_request_get(path, code=200):
    try:
        response = requests.get(
            f'{RESOLVER_URL}{path}',
            timeout=(1, 1)
            )
    except Exception as e:
        logger.error(f'Request Query KO [{e}]')
        return None
    else:
        return check_response(response, 200)


def resolver_move(self, targetx, targety):
    body = {
        "context": {
            "map": self.instance.map,
            "instance": self.instance.id,
            "creatures": RedisSearch().creature(
                query=f'@instance:{self.instance.id}'
                ).results_as_dict,
            "effects": RedisSearch().effect(
                query=f'@instance:{self.instance.id}'
                ).results_as_dict,
            "status": RedisSearch().status(
                query=f'@instance:{self.instance.id}'
                ).results_as_dict,
            "cd": RedisSearch().cd(
                query=f'@instance:{self.instance.id}'
                ).results_as_dict,
            },
        "fightEvent": {
            "name": "RegularMovesFightClass",
            "type": 3,
            "actor": self.creature.id,
            "params": {
                "destinationType": "tile",
                "destination": None,
                "options": {
                    "path": [{"x": targetx, "y": targety}]
                    },
                "type": "target",
                },
            },
        }

    try:
        response = requests.post(
            f'{RESOLVER_URL}/',
            json=body,
            timeout=(1, 1),
            )
    except Exception as e:
        logger.error(f'Request Query KO [{e}]')
        return None
    else:
        return check_response(response, 201)


def resolver_basic_attack(self, target):
    body = {
        "context": {
            "map": self.instance.map,
            "instance": self.instance.id,
            "creatures": RedisSearch().creature(
                query=f'@instance:{self.instance.id}'),
            "effects": RedisSearch().effect(
                query=f'@instance:{self.instance.id}'),
            "status": RedisSearch().status(
                query=f'@instance:{self.instance.id}'),
            "cd": RedisSearch().cd(
                query=f'@instance:{self.instance.id}'),
            },
        "fightEvent": {
            "name": "RegularAttacksFightClass",
            "type": 0,
            "actor": self.creature.id,
            "params": {
                "type": "target",
                "destinationType": "creature",
                "destination": target['id'],
                "options": {
                    "weapons": [],
                    "burst": False,
                    "doubleBarrel": False,
                    "scope": False,
                    },
                },
            },
        }

    try:
        response = requests.post(
            f'{RESOLVER_URL}/',
            json=body,
            timeout=(1, 1),
            )
    except Exception as e:
        logger.error(f'Request Query KO [{e}]')
        return None
    else:
        check_response(response, 200)

#
# Checkers
#


def check_response(response, code):
    logger.info('HTTP response Headers:' + str(response.headers))
    logger.info('HTTP response Code:' + str(response.status_code))
    logger.info('HTTP response Body:' + str(response.text))

    if response:
        if response.status_code == code:
            if response.text:
                logger.trace(
                    f'Request Query {response.status_code} OK '
                    f'response:{json.loads(response.text)}'
                    )
                return json.loads(response.text)
            else:
                logger.warning(
                    f'Request Query {response.status_code} KO'
                    )
                return None
        else:
            if response.text:
                logger.trace(
                    f'Request Query {response.status_code} KO '
                    f'response:{json.loads(response.text)}'
                    )
                return None
            else:
                logger.warning(
                    f'Request Query {response.status_code} KO'
                    )
                return None
    else:
        logger.warning('Request Query KO')
        return None
