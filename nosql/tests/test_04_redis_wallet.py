# -*- coding: utf8 -*-

import os
import sys
import uuid

# Needed for local imports and simulate production paths
LOCAL_PATH = os.path.dirname(os.path.abspath('nosql'))
sys.path.append(LOCAL_PATH)

from nosql.models.RedisWallet import RedisWallet  # noqa: E402

CREATURE_NAME = 'PyTest Creature'
CREATURE_ID = str(uuid.uuid3(uuid.NAMESPACE_DNS, CREATURE_NAME))


def test_redis_wallet_new():
    """
    Creating a new RedisWallet
    """
    Wallet = RedisWallet(CREATURE_ID).new()

    assert Wallet.cal22 == 0
    assert Wallet.arrow == 0
    assert Wallet.legendary == 0
    assert Wallet.bananas == 0


def test_redis_wallet_get_ok():
    """
    Querying a RedisWallet
    """
    Wallet = RedisWallet(creatureuuid=CREATURE_ID)

    assert Wallet.cal22 == 0
    assert Wallet.arrow == 0
    assert Wallet.legendary == 0
    assert Wallet.bananas == 0


def test_redis_wallet_setters():
    """
    Querying a RedisWallet, and modifiy attributes
    """
    # 1. From a direct Query
    Wallet = RedisWallet(creatureuuid=CREATURE_ID)

    Wallet.cal22 = 11
    Wallet.bananas = 33

    assert Wallet.cal22 == 11
    assert Wallet.bananas == 33

    # Lets check by calling again a Creature if it was updated in Redis
    WalletAgain = RedisWallet(creatureuuid=CREATURE_ID)

    assert WalletAgain.cal22 == 11
    assert WalletAgain.bananas == 33


def test_redis_wallet_to_json():
    """
    Querying a RedisWallet, and dumping it as JSON
    """
    pass


def test_redis_wallet_del():
    """
    Removing a RedisWallet
    """
    ret = RedisWallet(creatureuuid=CREATURE_ID).destroy()

    assert ret is True


def test_redis_wallet_del_ko():
    """
    Removing a RedisWallet
    > Expected to fail
    """
    ret = RedisWallet().destroy()

    assert ret is False


def test_redis_wallet_get_ko():
    """
    Querying a RedisWallet
    > Expected to fail
    """
    Wallet = RedisWallet(creatureuuid=CREATURE_ID)

    assert Wallet.hkey == 'wallets'
    assert hasattr(Wallet, 'cal22') is False
    assert hasattr(Wallet, 'arrow') is False

    Wallet = RedisWallet()

    assert Wallet.hkey == 'wallets'
    assert Wallet.cal22 is None
    assert Wallet.arrow is None


def test_redis_wallet_search_empty():
    """
    Searching a RedisWallet
    > Expected to fail
    """
    pass
