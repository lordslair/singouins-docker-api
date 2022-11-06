# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)


def test_singouins_inventory_item_get():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    itemmetaid = json.loads(response.text)['payload']['weapon'][0]['metaid']
    righthand  = json.loads(response.text)['payload']['equipment']['righthand']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert itemmetaid == 34
    assert righthand  is None


def test_singouins_inventory_item_equip():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    itemid     = json.loads(response.text)['payload']['weapon'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/equip/weapon/holster'  # POST # noqa
    response   = requests.post(url, headers=headers)
    equipment  = json.loads(response.text)['payload']['equipment']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert equipment['holster'] == itemid


def test_singouins_inventory_item_unequip():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    itemid     = json.loads(response.text)['payload']['equipment']['holster']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert itemid is not None

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/unequip/weapon/holster'  # POST # noqa
    response   = requests.post(url, headers=headers)
    equipment  = json.loads(response.text)['payload']['equipment']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert equipment['holster'] is None

    # We need to re-equip it for some /internal tests later
    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/equip/weapon/holster'  # POST # noqa
    response   = requests.post(url, headers=headers)
    equipment  = json.loads(response.text)['payload']['equipment']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    assert equipment['holster'] == itemid


def test_singouins_inventory_item_offset_move():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons    = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster
    holster    = json.loads(response.text)['payload']['equipment']['holster']
    # So we need the other one
    weapon     = [x for x in weapons if x['id'] != holster][0]
    itemid     = weapon['id']
    assert weapon['offsetx'] is None
    assert weapon['offsety'] is None

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/offset/1/1'  # POST # noqa
    response   = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons    = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster
    holster    = json.loads(response.text)['payload']['equipment']['holster']
    # So we need the other one
    weapon     = [x for x in weapons if x['id'] != holster][0]
    assert weapon['offsetx'] == 1
    assert weapon['offsety'] == 1


def test_singouins_inventory_item_offset_del():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    weapons    = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster
    holster    = json.loads(response.text)['payload']['equipment']['holster']
    # So we need the other one
    weapon     = [x for x in weapons if x['id'] != holster][0]
    itemid     = weapon['id']

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/offset'  # DELETE # noqa
    response   = requests.delete(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True

    weapons    = json.loads(response.text)['payload']['weapon']
    weapon     = [x for x in weapons if x['id'] == itemid][0]
    assert weapon['offsetx'] is None
    assert weapon['offsety'] is None


def test_singouins_inventory_item_dismantle():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item'  # GET
    response   = requests.get(url, headers=headers)
    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    weapons    = json.loads(response.text)['payload']['weapon']
    # We know one weapon is in holster
    holster    = json.loads(response.text)['payload']['equipment']['holster']
    # So we need the other one
    weapon     = [x for x in weapons if x['id'] != holster][0]
    itemid     = weapon['id']

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/dismantle'  # POST # noqa
    response   = requests.post(url, headers=headers)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
    shards = json.loads(response.text)['payload']['wallet']['shards']
    assert shards['common'] > 0
