# -*- coding: utf8 -*-

import requests
import os
import pytest

from variables import API_URL, CREATURE_ID

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


def test_singouins_action_resolver_base(jwt_header, mypc):
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    pc = mypc['indexed'][CREATURE_ID]
    if 'instance' not in pc:
        BODY = {"mapid": 1, "hardcore": True, "fast": False, "public": True}
        # We need to have the PJ in an instance - we open a new one
        response = requests.put(f"{API_URL}/mypc/{CREATURE_ID}/instance", headers=jwt_header['access'], json=BODY)  # noqa: E501

        assert response.status_code == 201
        assert response.json().get("success") is True

    response = requests.post(f'{API_URL}/mypc/{CREATURE_ID}/action/resolver', headers=jwt_header['access'], json=RESOLVER_JSON)  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    context = response.json().get("payload")['internal']['context']

    assert isinstance(context['creatures'], list)
    assert len(context['creatures']) > 0
    creature = [x for x in context['creatures'] if x['_id'] == CREATURE_ID][0]
    assert creature is not None

    assert isinstance(context['cd'], list)
    assert isinstance(context['effects'], list)
    assert isinstance(context['status'], list)


def test_singouins_action_resolver_move(jwt_header, mypc):
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    pc = mypc['indexed'][CREATURE_ID]

    RESOLVER_JSON['params']['options'] = {"path": [{"x": pc['x'] + 1, "y": pc['y'] - 1}]}
    RESOLVER_JSON['actor'] = pc['_id']

    response = requests.post(f"{API_URL}/mypc/{CREATURE_ID}/action/resolver", headers=jwt_header['access'], json=RESOLVER_JSON)  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True
