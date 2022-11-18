# -*- coding: utf8 -*-

import json
import requests

from variables import (API_URL,
                       AUTH_PAYLOAD)


def test_singouins_pc_delete():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/mypc'  # GET
    response = requests.get(url, headers=headers)
    pclist   = json.loads(response.text)['payload']

    if pclist is not None:
        for pc in pclist:
            pcid       = pc['id']
            instanceid = pc['instance']
            if instanceid is not None:
                # We need to leave the instance
                url      = f'{API_URL}/mypc/{pcid}/instance/{instanceid}/leave'
                response = requests.post(url, headers=headers)

                assert response.status_code == 200
                assert json.loads(response.text)['success'] is True

            # We delete the PC
            url        = f'{API_URL}/mypc/{pcid}'  # DELETE
            response   = requests.delete(url, headers=headers)

            assert response.status_code == 200
            assert json.loads(response.text)['success'] is True


def test_singouins_auth_delete():
    url      = f'{API_URL}/auth/login'  # POST
    response = requests.post(url, json=AUTH_PAYLOAD)
    token    = json.loads(response.text)['access_token']
    headers  = {"Authorization": f"Bearer {token}"}

    url      = f'{API_URL}/auth/forgotpassword'  # POST
    response = requests.post(url,
                             json={'mail': 'user@exemple.com'},
                             headers=headers)

    assert response.status_code == 200
    assert 'Password replacement OK' in json.loads(response.text)['msg']

    url      = f'{API_URL}/auth/delete'  # DELETE
    response = requests.delete(url,
                               json={'username': 'user@exemple.com'},
                               headers=headers)

    assert response.status_code == 200
    assert 'User deletion OK' in json.loads(response.text)['msg']
