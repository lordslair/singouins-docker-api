# -*- coding: utf8 -*-

import json
import os
import redis
import requests

from variables import (
    AUTH_PAYLOAD,
    API_URL,
    CREATURE_ID,
    CREATURE_NAME,
    )

# Redis variables
REDIS_HOST = os.environ.get("REDIS_HOST", '127.0.0.1')
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_BASE = os.environ.get("REDIS_BASE", 0)

r = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_BASE,
    encoding='utf-8',
    )


def test_singouins_profession_skinning():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    """
    We do something quite dirty, but no other option so far
    We add directly into Redis a Corpse to be able to use skinning on it
    """

    CORPSE_ID = 'd13a30f1-c8f5-41d6-8d8c-9ae15ba93309'
    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']

    # We need the instance of the PC who's still in
    instanceuuid = [x for x in pcs if x['name'] == 'PJTestInstanceJoin'][0]['instance']
    # We join PJTestInstanceJoin instance
    url      = f'{API_URL}/mypc/{CREATURE_ID}/instance/{instanceuuid}/join'
    response = requests.post(url, headers=headers)
    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    # We need the PC (name:PJTest)
    creature = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    # We build and store the Corpse in Redis
    r.hset(
        f'corpses:{CORPSE_ID}',
        mapping={
            "account": 'None',
            "created": "2024-01-15 19:53:28",
            "date": "2024-01-15 19:53:28",
            "gender": 1,
            "id": CORPSE_ID,
            "instance": instanceuuid,
            "killer": 'None',
            "killer_squad": 'None',
            "level": 1,
            "name": "Salamandre",
            "race": 11,
            "rarity": "Small",
            "x": creature['x'] + 1,
            "y": creature['y'] + 1,
        })

    url       = f'{API_URL}/mypc/{CREATURE_ID}/action/profession/skinning/{CORPSE_ID}'  # POST
    response  = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
