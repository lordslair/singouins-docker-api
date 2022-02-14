# -*- coding: utf8 -*-

import json
import requests

from variables import (AUTH_PAYLOAD,
                       API_URL)

def test_singouins_inventory_item_get():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item' # GET
    response   = requests.get(url, headers=headers)
    itemmetaid = json.loads(response.text)['payload']['weapon'][0]['metaid']
    righthand  = json.loads(response.text)['payload']['equipment'][0]['righthand']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert itemmetaid == 34
    assert righthand  == None

def test_singouins_inventory_item_equip():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item' # GET
    response   = requests.get(url, headers=headers)
    itemid     = json.loads(response.text)['payload']['weapon'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/equip/weapon/holster' # POST
    response   = requests.post(url, headers=headers)
    equipment  = json.loads(response.text)['payload']['equipment']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert equipment['holster'] == itemid

def test_singouins_inventory_item_unequip():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item' # GET
    response   = requests.get(url, headers=headers)
    itemid     = json.loads(response.text)['payload']['equipment'][0]['holster']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert itemid is not None

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/unequip/weapon/holster' # POST
    response   = requests.post(url, headers=headers)
    equipment  = json.loads(response.text)['payload']['equipment']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert equipment['holster'] is None

def test_singouins_inventory_item_offset_move():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item' # GET
    response   = requests.get(url, headers=headers)
    weapon     = json.loads(response.text)['payload']['weapon']
    itemid     = weapon[0]['id']
    offsetx    = weapon[0]['offsetx']
    offsety    = weapon[0]['offsety']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert offsetx is None
    assert offsety is None

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/offset/1/1' # POST
    response   = requests.post(url, headers=headers)
    weapon     = json.loads(response.text)['payload']['weapon']
    offsetx    = weapon[0]['offsetx']
    offsety    = weapon[0]['offsety']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert offsetx == 1
    assert offsety == 1

def test_singouins_inventory_item_offset_del():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item' # GET
    response   = requests.get(url, headers=headers)
    weapon     = json.loads(response.text)['payload']['weapon']
    itemid     = weapon[0]['id']
    offsetx    = weapon[0]['offsetx']
    offsety    = weapon[0]['offsety']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert offsetx == 1
    assert offsety == 1

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/offset' # DELETE
    response   = requests.delete(url, headers=headers)
    weapon     = json.loads(response.text)['payload']['weapon']
    offsetx    = weapon[0]['offsetx']
    offsety    = weapon[0]['offsety']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert offsetx is None
    assert offsety is None

def test_singouins_inventory_item_dismantle():
    url      = f'{API_URL}/auth/login' # POST
    response = requests.post(url, json = AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc' # GET
    response = requests.get(url, headers=headers)
    pcid     = json.loads(response.text)['payload'][0]['id']

    url        = f'{API_URL}/mypc/{pcid}/item' # GET
    response   = requests.get(url, headers=headers)
    weapon     = json.loads(response.text)['payload']['weapon']
    itemid     = weapon[1]['id']

    url        = f'{API_URL}/mypc/{pcid}/inventory/item/{itemid}/dismantle' # POST
    response   = requests.post(url, headers=headers)
    common     = json.loads(response.text)['payload']['shards']['Common']

    assert response.status_code == 200
    assert json.loads(response.text)['success'] == True
    assert common > 0
