# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS,
                       STATUS_JSON,
                       STATUS_NAME)


def test_singouins_internal_creature_status_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/status/{STATUS_NAME}'  # PUT # noqa
    response  = requests.put(url, headers=HEADERS, json=STATUS_JSON)
    statuses  = json.loads(response.text)['payload']['statuses']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert statuses[-1]['name']                 == STATUS_NAME


def test_singouins_internal_creature_statuses():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/statuses'  # GET
    response  = requests.get(url, headers=HEADERS)
    statuses  = json.loads(response.text)['payload']['statuses']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert statuses[-1]['name']                 == STATUS_NAME


def test_singouins_internal_creature_status_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/status/{STATUS_NAME}'  # GET # noqa
    response  = requests.get(url, headers=HEADERS)
    status    = json.loads(response.text)['payload']['status']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert status['name']                       == STATUS_NAME


def test_singouins_internal_creature_status_del():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/status/{STATUS_NAME}'  # DELETE # noqa
    response  = requests.delete(url, headers=HEADERS)
    statuses  = json.loads(response.text)['payload']['statuses']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert statuses                             == []
