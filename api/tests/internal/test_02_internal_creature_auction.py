# -*- coding: utf8 -*-

import json
import os
import pytest
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)

# Init request to know ITEM_ID as the UUID is random in CI/CD tests
# But we know that PJTest is created handling an Item where Item.metaid == 34
url       = f'{API_URL}/internal/creature/{CREATURE_ID}/inventory'
response  = requests.get(url, headers=HEADERS)
print(json.loads(response.text))
inventory = json.loads(response.text)['payload']['inventory']
item      = [x for x in inventory if x['metaid'] == 34][0]
ITEM_ID   = item['id']


def test_singouins_internal_creature_auction_sell():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # PUT # noqa
    response  = requests.put(
        url,
        headers=HEADERS,
        json={'price': 100, 'duration': 500},
        )

    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_remove():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # DELETE # noqa
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_resell():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # PUT # noqa
    response  = requests.put(
        url,
        headers=HEADERS,
        json={'price': 100, 'duration': 500},
        )

    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_get():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # GET # noqa
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_buy():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # POST # noqa
    response  = requests.post(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_reremove():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # DELETE # noqa
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auctions_search():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        pytest.skip('For now, unable to test this in GitHub')

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auctions'  # POST # noqa
    response  = requests.post(
        url,
        headers=HEADERS,
        json={'metatype': 'weapon', 'metaid': 34}
        )

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
