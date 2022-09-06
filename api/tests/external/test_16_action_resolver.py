# -*- coding: utf8 -*-

import json
import requests
import os

from variables import (AUTH_PAYLOAD,
                       API_URL)


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

    assert json.loads(response.text)['success'] is True
    assert response.status_code                 == 200

    context    = json.loads(response.text)['payload']['internal']['context']
    assert context['creatures'][0]['name'] == 'PJTest'
    assert context['pa']['blue']['pa']     > 0
    assert isinstance(context['cd'], list)
    assert isinstance(context['effects'], list)
    assert isinstance(context['status'], list)


def test_singouins_action_resolver_move():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']
    x        = json.loads(response.text)['payload'][0]['x']
    y        = json.loads(response.text)['payload'][0]['y']

    RESOLVER_JSON = {
        "name": "RegularMovesFightClass",
        "type": 3,
        "params": {
            "type": "target",
            "destinationType": "tile",
            "destination": None,
            "options": {"path": [{"x": x + 1, "y": y - 1}]}
        },
        "actor": pcid
    }

    url        = f'{API_URL}/mypc/{pcid}/action/resolver/move'  # POST
    response   = requests.post(url, headers=headers, json=RESOLVER_JSON)

    assert json.loads(response.text)['success'] is True
    assert response.status_code                 == 200
