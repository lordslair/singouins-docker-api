# -*- coding: utf8 -*-

import json
import requests

from variables import (
    API_URL,
    USER_NAME,
    access_token_get,
    )


def test_singouins_pc_delete():
    response = requests.get(
        f'{API_URL}/mypc',
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )
    pcs = json.loads(response.text)['payload']

    if pcs and len(pcs) > 0:
        for pc in pcs:
            if 'instance' in pc:
                # We need to leave the instance
                response = requests.post(
                    f"{API_URL}/mypc/{pc['_id']}/instance/{pc['instance']}/leave",
                    headers={"Authorization": f"Bearer {access_token_get()}"},
                    )

                assert response.status_code == 200
                assert json.loads(response.text)['success'] is True

            # We delete the PC
            response   = requests.delete(
                f"{API_URL}/mypc/{pc['_id']}",
                headers={"Authorization": f"Bearer {access_token_get()}"},
                )

            assert response.status_code == 200
            assert json.loads(response.text)['success'] is True


def test_singouins_auth_delete():
    response = requests.delete(
        f'{API_URL}/auth/delete',
        json={'username': USER_NAME},
        headers={"Authorization": f"Bearer {access_token_get()}"},
        )

    assert response.status_code == 200
    assert 'User deletion OK' in json.loads(response.text)['msg']
