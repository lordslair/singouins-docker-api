# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    CREATURE_NAME,
    access_token_get,
    )


def test_singouins_mypc_create():
    payload  = {
        'name': CREATURE_NAME,
        'gender': True,
        'race': 2,
        'vocation': 3,
        'cosmetic': {
            'metaid': 8,
            'data': {
                'hasGender': True,
                'beforeArmor': False,
                'hideArmor': None,
            }
        },
        'equipment': {
            'righthand': {
                'metaid': 34,
                'metatype': 'weapon'
            },
            'lefthand': {
                'metaid': 11,
                'metatype': 'weapon'
            }
        }
    }

    response  = requests.post(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        json=payload,
        )

    assert response.status_code == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_infos():
    response  = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    assert json.loads(response.text)['payload'][0]['name'] == CREATURE_NAME


def test_singouins_mypc_view():
    response  = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/view',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_mypc_effects():
    response  = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/effects',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    assert isinstance(json.loads(response.text)['payload']['effects'], list)


def test_singouins_mypc_cds():
    response  = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/cds',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    assert isinstance(json.loads(response.text)['payload']['cds'], list)


def test_singouins_mypc_statuses():
    response  = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/statuses',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    assert isinstance(json.loads(response.text)['payload']['statuses'], list)
