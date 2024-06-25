# -*- coding: utf8 -*-

import json
import requests

from variables import API_URL


def test_singouins_log_trace():
    response = requests.post(
        f'{API_URL}/log',
        json={
            "level": 7,
            "short_message": "http-service.class.ts/postman | Dummy error | LEVEL:7:TRACE"
            },
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_debug():
    response = requests.post(
        f'{API_URL}/log',
        json={
            "level": 6,
            "short_message": "http-service.class.ts/postman | Dummy error | LEVEL:6:DEBUG"
            },
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_info():
    response = requests.post(
        f'{API_URL}/log',
        json={
            "level": 5,
            "short_message": "http-service.class.ts/postman | Dummy error | LEVEL:5:INFO"
            },
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_success():
    response = requests.post(
        f'{API_URL}/log',
        json={
            "level": 4,
            "short_message": "http-service.class.ts/postman | Dummy error | LEVEL:4:SUCCESS"
            },
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_warn():
    response = requests.post(
        f'{API_URL}/log',
        json={
            "level": 3,
            "short_message": "http-service.class.ts/postman | Dummy error | LEVEL:3:WARN"
            },
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_error():
    response = requests.post(
        f'{API_URL}/log',
        json={
            "level": 2,
            "short_message": "http-service.class.ts/postman | Dummy error | LEVEL:2:ERROR"
            },
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_critical():
    response = requests.post(
        f'{API_URL}/log',
        json={
            "level": 1,
            "short_message": "http-service.class.ts/postman | Dummy error | LEVEL:1:CRITICAL"
            },
        )

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
