# -*- coding: utf8 -*-

import json
import os
import requests

from variables import (API_URL,
                       CREATURE_ID,
                       HEADERS)


def test_singouins_internal_creature_auction_sell():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/8ac53305-b889-4410-a3f5-daccbeaa0f01'  # PUT # noqa
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

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/8ac53305-b889-4410-a3f5-daccbeaa0f01'  # DELETE # noqa
    response  = requests.delete(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_resell():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/8ac53305-b889-4410-a3f5-daccbeaa0f01'  # PUT # noqa
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

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/8ac53305-b889-4410-a3f5-daccbeaa0f01'  # GET # noqa
    response  = requests.get(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_buy():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/8ac53305-b889-4410-a3f5-daccbeaa0f01'  # POST # noqa
    response  = requests.post(url, headers=HEADERS)

    assert response.status_code                 == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_internal_creature_auction_reremove():
    if os.environ.get("CI"):
        # Here we are inside GitHub CI process
        # Gruik
        # For now, unable to test this in GitHub
        return True

    url       = f'{API_URL}/internal/creature/{CREATURE_ID}/auction/8ac53305-b889-4410-a3f5-daccbeaa0f01'  # DELETE # noqa
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
