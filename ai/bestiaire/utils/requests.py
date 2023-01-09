# -*- coding: utf8 -*-

import json
import os
import requests

from loguru                      import logger

API_INTERNAL_HOST  = os.environ['SEP_BACKEND_API_INTERNAL_SVC_SERVICE_HOST']
API_INTERNAL_PORT  = os.environ['SEP_BACKEND_API_INTERNAL_SVC_SERVICE_PORT']
API_INTERNAL_URL   = f'http://{API_INTERNAL_HOST}:{API_INTERNAL_PORT}'
API_INTERNAL_TOKEN = os.environ.get("SEP_INTERNAL_TOKEN")
headers            = {"Authorization": f"Bearer {API_INTERNAL_TOKEN}"}

RESOLVER_HOST = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_HOST")
RESOLVER_PORT = os.environ.get("SEP_BACKEND_RESOLVER_SVC_SERVICE_PORT")
RESOLVER_URL  = f'http://{RESOLVER_HOST}:{RESOLVER_PORT}'


def api_internal_generic_request_get(path, code=200):
    try:
        response = requests.get(
            f'{API_INTERNAL_URL}/internal{path}',
            headers=headers,
            timeout=(1, 1)
            )
    except Exception as e:
        logger.error(f'Request Query KO [{e}]')
        return None
    else:
        return check_response(response, code)


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
    # Lets find Creature context for Resolver
    try:
        ret = api_internal_generic_request_get(
            path=f"/creature/{self.id}/context"
        )
    except Exception as e:
        logger.error(f'Internal API Request KO [{e}]')
        return None
    else:
        context = ret['payload']

    body = {
        "context": context,
        "fightEvent": {
            "name": "RegularMovesFightClass",
            "type": 3,
            "actor": self.id,
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
    # Lets find Creature context for Resolver
    try:
        ret = api_internal_generic_request_get(
            path=f"/creature/{self.id}/context"
        )
    except Exception as e:
        logger.error(f'Internal API Request KO [{e}]')
        return None
    else:
        context = ret['payload']

    body = {
        "context": context,
        "fightEvent": {
            "name": "RegularAttacksFightClass",
            "type": 0,
            "actor": self.id,
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
    if response:
        if response.status_code == code:
            if response.text:
                logger.trace(f'Request Query {code} OK '
                             f'response:{json.loads(response.text)}')
                return json.loads(response.text)
            else:
                logger.warning(f'Request Query {code} KO')
                return None
        else:
            if response.text:
                logger.trace(f'Request Query {response.status_code} KO '
                             f'response:{json.loads(response.text)}')
                return None
            else:
                logger.warning(f'Request Query {code} KO')
                return None
    else:
        logger.warning('Request Query KO')
        return None
