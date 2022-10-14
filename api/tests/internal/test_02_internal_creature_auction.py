# -*- coding: utf8 -*-

import json
import os
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_auction_sell():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    response  = requests.put(
        url,
        headers=HEADERS,
        json={'price': 100, 'duration': 500},
        )

    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_remove():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # DELETE # noqa
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_resell():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # PUT # noqa
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    response  = requests.put(
        url,
        headers=HEADERS,
        json={'price': 100, 'duration': 500},
        )

    assert response.status_code                 == 201
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_get():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # GET # noqa
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_buy():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # POST # noqa
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    response  = requests.post(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_reremove():
    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/197'  # DELETE # noqa
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

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
