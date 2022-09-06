# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS,
                       SKILL_JSON,
                       SKILL_NAME)


def test_singouins_internal_creature_cd_add():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILL_NAME}'  # PUT # noqa
    response  = requests.put(url, headers=HEADERS, json=SKILL_JSON)
    cds       = json.loads(response.text)['payload']['cds']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert cds[-1]['name']                      == SKILL_NAME


def test_singouins_internal_creature_cds():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cds'  # GET
    response  = requests.get(url, headers=HEADERS)
    cds       = json.loads(response.text)['payload']['cds']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert cds[-1]['name']                      == SKILL_NAME


def test_singouins_internal_creature_cd_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILL_NAME}'  # GET # noqa
    response  = requests.get(url, headers=HEADERS)
    cd        = json.loads(response.text)['payload']['cd']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert cd['name']                           == SKILL_NAME


def test_singouins_internal_creature_cd_del():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/cd/{SKILL_NAME}'  # DELETE # noqa
    response  = requests.delete(url, headers=HEADERS)
    cds       = json.loads(response.text)['payload']['cds']

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
    assert cds                                  == []
