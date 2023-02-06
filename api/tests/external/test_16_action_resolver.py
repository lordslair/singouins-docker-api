# -*- coding: utf8 -*-

import json
import requests
import os
import pytest

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       CREATURE_ID,
                       CREATURE_NAME,
                       )


def test_singouins_action_resolver_context():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    if pc['instance'] is None:
        # We need to have the PJ in an instance - we open a new one
        url      = f"{API_URL}/mypc/{CREATURE_ID}/instance"  # PUT
        payload  = {"mapid": 1,
                    "hardcore": True,
                    "fast": False,
                    "public": True}
        response = requests.put(url, json=payload, headers=headers)

        assert response.status_code == 201
        assert json.loads(response.text)['success'] is True

    RESOLVER_JSON = {
        "name": "RegularMovesFightClass",
        "type": 3,
        "params": {
            "type": "target",
            "destinationType": "tile",
            "destination": None,
            "options": {"path": [{"x": 7, "y": 7}]}
        },
        "actor": CREATURE_ID
    }

    url        = f'{API_URL}/mypc/{CREATURE_ID}/action/resolver/context'  # POST # noqa
    response   = requests.post(url, headers=headers, json=RESOLVER_JSON)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    context = json.loads(response.text)['payload']['internal']['context']

    assert isinstance(context['creatures'], list)
    assert len(context['creatures']) > 0
    creature = [x for x in context['creatures'] if x['id'] == CREATURE_ID][0]
    assert creature is not None

    assert isinstance(context['cd'], list)
    assert isinstance(context['effects'], list)
    assert isinstance(context['status'], list)


def test_singouins_action_resolver_move():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcs      = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc       = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    RESOLVER_JSON = {
        "name": "RegularMovesFightClass",
        "type": 3,
        "params": {
            "type": "target",
            "destinationType": "tile",
            "destination": None,
            "options": {"path": [{"x": pc['x'] + 1, "y": pc['y'] - 1}]}
        },
        "actor": pc['id']
    }

    url        = f"{API_URL}/mypc/{CREATURE_ID}/action/resolver/move"  # POST
    response   = requests.post(url, headers=headers, json=RESOLVER_JSON)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
