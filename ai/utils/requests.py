# -*- coding: utf8 -*-

import json
import requests

from loguru import logger

from mongo.models.Creature import CreatureDocument
from nosql.models.RedisSearch import RedisSearch
from variables import RESOLVER_URL


def resolver_generic_request_get(path, code=200):
    try:
        response = requests.get(f'{RESOLVER_URL}{path}', timeout=(1, 1))
    except Exception as e:
        logger.error(f'Request Query KO [{e}]')
        return None
    else:
        return check_response(response, 200)


def resolver_move(self, targetx, targety):
    instanceuuid = self.instance.id.replace('-', ' ')
    Effects = RedisSearch().effect(query=f"@instance:{instanceuuid}")
    Statuses = RedisSearch().status(query=f"@instance:{instanceuuid}")
    Cds = RedisSearch().cd(query=f"@instance:{instanceuuid}")

    Creatures = CreatureDocument.objects(instance=self.instance.id)

    body = {
        "context": {
            "map": self.instance.map,
            "instance": self.instance.id,
            "creatures": [Creature.to_mongo() for Creature in Creatures],
            "effects": [Effect.as_dict() for Effect in Effects.results],
            "status": [Status.as_dict() for Status in Statuses.results],
            "cd": [Cd.as_dict() for Cd in Cds.results],
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
        response = requests.post(f'{RESOLVER_URL}/', json=body, timeout=(1, 1))
    except Exception as e:
        logger.error(f'Request Query KO [{e}]')
        return None
    else:
        return check_response(response, 201)


def resolver_basic_attack(self, target):
    Creatures = CreatureDocument.objects(instance=self.instance.id)

    instanceuuid = self.instance.id.replace('-', ' ')
    Effects = RedisSearch().effect(query=f"@instance:{instanceuuid}")
    Statuses = RedisSearch().status(query=f"@instance:{instanceuuid}")
    Cds = RedisSearch().cd(query=f"@instance:{instanceuuid}")

    body = {
        "context": {
            "map": self.instance.map,
            "instance": self.instance.id,
            "creatures": [Creature.to_mongo() for Creature in Creatures],
            "effects": [Effect.as_dict() for Effect in Effects.results],
            "status": [Status.as_dict() for Status in Statuses.results],
            "cd": [Cd.as_dict() for Cd in Cds.results],
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
        response = requests.post(f'{RESOLVER_URL}/', json=body, timeout=(1, 1))
    except Exception as e:
        logger.error(f'Request Query KO [{e}]')
        return None
    else:
        check_response(response, 200)

#
# Checkers
#


def check_response(response, code):
    logger.trace('HTTP response Headers:' + str(response.headers))
    logger.trace('HTTP response Code:' + str(response.status_code))
    logger.trace('HTTP response Body:' + str(response.text))

    if response:
        if response.status_code == code:
            if response.text:
                logger.trace(f'Request {response.status_code} OK ({json.loads(response.text)})')
                return json.loads(response.text)
            else:
                logger.warning(f'Request {response.status_code} KO')
                return None
        else:
            if response.text:
                logger.trace(f'Request {response.status_code} KO ({json.loads(response.text)})')
                return None
            else:
                logger.warning(f'Request {response.status_code} KO')
                return None
    else:
        logger.warning('Request Query KO')
        return None
