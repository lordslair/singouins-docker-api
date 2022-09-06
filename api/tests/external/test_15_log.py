# -*- coding: utf8 -*-

import json
import requests

from variables import API_URL


def test_singouins_log_trace():
    url       = f'{API_URL}/log'
    payload   = {
        "level": 7,
        "short_message":
            "http-service.class.ts/postman | Dummy error | LEVEL:7:TRACE"
    }
    response  = requests.post(url, json=payload)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_debug():
    url       = f'{API_URL}/log'
    payload   = {
        "level": 6,
        "short_message":
            "http-service.class.ts/postman | Dummy error | LEVEL:6:DEBUG"
    }
    response  = requests.post(url, json=payload)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_info():
    url       = f'{API_URL}/log'
    payload   = {
        "level": 5,
        "short_message":
            "http-service.class.ts/postman | Dummy error | LEVEL:5:INFO"
    }
    response  = requests.post(url, json=payload)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_success():
    url       = f'{API_URL}/log'
    payload   = {
        "level": 4,
        "short_message":
            "http-service.class.ts/postman | Dummy error | LEVEL:4:SUCCESS"
    }
    response  = requests.post(url, json=payload)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_warn():
    url       = f'{API_URL}/log'
    payload   = {
        "level": 3,
        "short_message":
            "http-service.class.ts/postman | Dummy error | LEVEL:3:WARN"
    }
    response  = requests.post(url, json=payload)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_error():
    url       = f'{API_URL}/log'
    payload   = {
        "level": 2,
        "short_message":
            "http-service.class.ts/postman | Dummy error | LEVEL:2:ERROR"
    }
    response  = requests.post(url, json=payload)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True


def test_singouins_log_critical():
    url       = f'{API_URL}/log'
    payload   = {
        "level": 1,
        "short_message":
            "http-service.class.ts/postman | Dummy error | LEVEL:1:CRITICAL"
    }
    response  = requests.post(url, json=payload)

    assert response.status_code == 200
    assert json.loads(response.text)['success'] is True
