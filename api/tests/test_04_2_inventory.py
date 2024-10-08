# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    CREATURE_ID,
    access_token_get,
    )


def test_singouins_inventory_item_get():
    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapon = json.loads(response.text)['payload']['weapon']
    assert [x for x in weapon if x['metaid'] == 34][0] is not None

    equipment = json.loads(response.text)['payload']['equipment']
    assert equipment['righthand']['metaid'] == 34


def test_singouins_inventory_item_equip():
    response  = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    weapon   = json.loads(response.text)['payload']['weapon']
    item     = [x for x in weapon if x['metaid'] == 34][0]

    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/inventory/item/{item['_id']}/equip/weapon/holster",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    slots = json.loads(response.text)['payload']['creature']['slots']
    assert slots['holster']['id'] == item['_id']


def test_singouins_inventory_item_unequip():
    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    itemid = json.loads(response.text)['payload']['equipment']['holster']['id']
    assert itemid is not None

    response = requests.post(
        f'{API_URL}/mypc/{CREATURE_ID}/inventory/item/{itemid}/unequip/weapon/holster',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    slots = json.loads(response.text)['payload']['creature']['slots']
    assert 'holster' not in slots

    # We need to re-equip it for some tests later
    response = requests.post(
        f'{API_URL}/mypc/{CREATURE_ID}/inventory/item/{itemid}/equip/weapon/holster',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    slots = json.loads(response.text)['payload']['creature']['slots']
    assert slots['holster']['id'] == itemid


def test_singouins_inventory_item_offset_move():
    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster
    holster = json.loads(response.text)['payload']['equipment']['holster']
    # So we need to find the weapon details
    weapon = [x for x in weapons if x['_id'] != holster][0]
    # There should not be any offset as item is equipped
    assert 'offsetx' not in weapon
    assert 'offsety' not in weapon

    # This test is pure bullshit, and can't happen in real life
    # but it's easiest way to test /offset/{x}/{y}
    itemid = weapon['_id']
    response = requests.post(
        f"{API_URL}/mypc/{CREATURE_ID}/inventory/item/{weapon['_id']}/offset/1/1",
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster
    holster = json.loads(response.text)['payload']['creature']['slots']['holster']
    # So we need to find the weapon details
    weapon = [x for x in weapons if x['_id'] == itemid][0]
    # There should offset as we moved item
    assert weapon['offsetx'] == 1
    assert weapon['offsety'] == 1


def test_singouins_inventory_item_offset_del():
    response = requests.get(
        f'{API_URL}/mypc/{CREATURE_ID}/item',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster
    holster = json.loads(response.text)['payload']['equipment']['holster']

    itemid = holster['id']
    response = requests.delete(
        f'{API_URL}/mypc/{CREATURE_ID}/inventory/item/{itemid}/offset',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons = json.loads(response.text)['payload']['weapon']
    weapon = [x for x in weapons if x['_id'] == itemid][0]
    assert 'offsetx' not in weapon
    assert 'offsety' not in weapon
