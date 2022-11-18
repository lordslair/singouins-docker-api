# -*- coding: utf8 -*-

import json
import os
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS,
                       ITEM_ID)


def test_singouins_internal_creature_auction_sell():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

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
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # DELETE # noqa
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_resell():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

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
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # GET # noqa
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_buy():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # POST # noqa
    response  = requests.post(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_reremove():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/{ITEM_ID}'  # DELETE # noqa
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auctions_search():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auctions'  # POST # noqa
    response  = requests.post(
        url,
        headers=HEADERS,
        json={'metatype': 'weapon', 'metaid': 34}
        )

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True
