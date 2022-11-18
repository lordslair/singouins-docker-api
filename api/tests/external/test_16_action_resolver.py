# -*- coding: utf8 -*-

import json
import requests
import os
import pytest

from variables import (AUTH_PAYLOAD,
                       API_URL,
                       PC_NAME)


def test_singouins_action_resolver_context():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    instanceid = json.loads(response.text)['payload'][0]['instance']
    if instanceid is None:
        # We need to have the PJ in an instance - we open a new one
        url      = f'{API_URL}/mypc/{pcid}/instance'  # PUT
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
        "actor": pcid
    }

    url        = f'{API_URL}/mypc/{pcid}/action/resolver/context'  # POST
    response   = requests.post(url, headers=headers, json=RESOLVER_JSON)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    context = json.loads(response.text)['payload']['internal']['context']

    assert isinstance(context['creatures'], list)
    assert len(context['creatures']) > 0
    assert [x for x in context['creatures'] if x['id'] == pcid][0] is not None

    assert context['pa']['blue']['pa'] > 0

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

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    payload = json.loads(response.text)['payload']
    pc = [x for x in payload if x['name'] == PC_NAME][0]

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

    url        = f"{API_URL}/mypc/{pc['id']}/action/resolver/move"  # POST
    response   = requests.post(url, headers=headers, json=RESOLVER_JSON)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
