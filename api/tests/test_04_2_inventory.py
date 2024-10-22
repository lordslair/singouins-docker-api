# -*- coding: utf8 -*-

import requests

from variables import API_URL, CREATURE_ID

ROUTE_INVENTORY = f'{API_URL}/mypc/{CREATURE_ID}/inventory/item'


def test_singouins_inventory_item_get(jwt_header, myitems):
    assert [x for x in myitems['weapon'] if x['metaid'] == 34][0] is not None
    assert myitems['equipment']['righthand']['metaid'] == 34


def test_singouins_inventory_item_equip(jwt_header, myitems):
    item = [x for x in myitems['weapon'] if x['metaid'] == 34][0]

    response = requests.post(f"{ROUTE_INVENTORY}/{item['_id']}/equip/weapon/holster", headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    slots = response.json().get("payload")['creature']['slots']
    assert slots['holster']['id'] == item['_id']


def test_singouins_inventory_item_unequip(jwt_header, myitems):
    item_uuid = myitems['equipment']['holster']['id']
    assert item_uuid is not None

    response = requests.post(f'{ROUTE_INVENTORY}/{item_uuid}/unequip/weapon/holster', headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    slots = response.json().get("payload")['creature']['slots']
    assert 'holster' not in slots

    # We need to re-equip it for some tests later
    response = requests.post(f'{ROUTE_INVENTORY}/{item_uuid}/equip/weapon/holster', headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    slots = response.json().get("payload")['creature']['slots']
    assert slots['holster']['id'] == item_uuid


def test_singouins_inventory_item_offset_move(jwt_header, myitems):
    weapons = myitems['weapon']
    # We know one weapon is in holster
    holster = myitems['equipment']['holster']
    # So we need to find the weapon details
    weapon = [x for x in weapons if x['_id'] != holster][0]
    # There should not be any offset as item is equipped
    assert 'offsetx' not in weapon
    assert 'offsety' not in weapon

    # This test is pure bullshit, and can't happen in real life
    # but it's easiest way to test /offset/{x}/{y}
    item_uuid = weapon['_id']
    response = requests.post(f"{ROUTE_INVENTORY}/{weapon['_id']}/offset/1/1", headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    weapons = response.json().get("payload")['weapon']
    # We know one weapon is in holster
    holster = response.json().get("payload")['creature']['slots']['holster']
    # So we need to find the weapon details
    weapon = [x for x in weapons if x['_id'] == item_uuid][0]
    # There should offset as we moved item
    assert weapon['offsetx'] == 1
    assert weapon['offsety'] == 1


def test_singouins_inventory_item_offset_del(jwt_header, myitems):
    weapons = myitems['weapon']
    # We know one weapon is in holster
    holster = myitems['equipment']['holster']

    item_uuid = holster['id']
    response = requests.delete(f'{ROUTE_INVENTORY}/{item_uuid}/offset', headers=jwt_header['access'])  # noqa: E501

    assert response.status_code == 200
    assert response.json().get("success") is True

    weapons = response.json().get("payload")['weapon']
    weapon = [x for x in weapons if x['_id'] == item_uuid][0]
    assert 'offsetx' not in weapon
    assert 'offsety' not in weapon
