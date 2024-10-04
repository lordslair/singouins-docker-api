# -*- coding: utf8 -*-

import json
import requests
import os
import pytest

from variables import (
    API_URL,
    CREATURE_ID,
    CREATURE_NAME,
    access_token_get,
    )

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


def test_singouins_action_resolver_base():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    if 'instance' not in pc:
        # We need to have the PJ in an instance - we open a new one
        response = requests.put(
            f"{API_URL}/mypc/{CREATURE_ID}/instance",
            headers={"Authorization": f"Bearer {access_token_get()}"},
            json={"mapid": 1, "hardcore": True, "fast": False, "public": True}
            )

        assert response.status_code == 201
        assert json.loads(response.text)['success'] is True

    response = requests.post(
        f'{API_URL}/mypc/{CREATURE_ID}/action/resolver',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json=RESOLVER_JSON,
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    context = json.loads(response.text)['payload']['internal']['context']

    assert isinstance(context['creatures'], list)
    assert len(context['creatures']) > 0
    creature = [x for x in context['creatures'] if x['_id'] == CREATURE_ID][0]
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

    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']
    # We need the PC (name:PJTest)
    pc = [x for x in pcs if x['name'] == CREATURE_NAME][0]

    RESOLVER_JSON['params']['options'] = {"path": [{"x": pc['x'] + 1, "y": pc['y'] - 1}]}
    RESOLVER_JSON['actor'] = pc['_id']

    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/action/resolver",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json=RESOLVER_JSON,
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
