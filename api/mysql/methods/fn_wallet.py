# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import Wallet

def fn_wallet_ammo_get(pc,item,caliber):
    session = Session()

    try:
        wallet = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if wallet is None:
            return False

        if   caliber == '.22':
            return wallet.cal22
        elif caliber == '.223':
            return wallet.cal223
        elif caliber == '.311':
            return wallet.cal311
        elif caliber == '.50':
            return wallet.cal50
        elif caliber == '.55':
            return wallet.cal55
        elif caliber == 'shell':
            return wallet.shell
        elif caliber == 'bolt':
            return wallet.bolt
        elif caliber == 'arrow':
            return wallet.arrow
        else:
            return 0
    finally:
        session.close()

def fn_wallet_ammo_set(pc,caliber,ammo):
    session = Session()

    try:
        wallet = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()

        if   caliber == '.22':
            wallet.cal22 += ammo
        elif caliber == '.223':
            wallet.cal223 += ammo
        elif caliber == '.311':
            wallet.cal311 += ammo
        elif caliber == '.50':
            wallet.cal50 += ammo
        elif caliber == '.55':
            wallet.cal55 += ammo
        elif caliber == 'shell':
            wallet.shell += ammo
        elif caliber == 'bolt':
            wallet.bolt += ammo
        elif caliber == 'arrow':
            wallet.arrow += ammo

        session.commit()
    except Exception as e:
        # Something went wrong during query
        session.rollback()
        return False
    else:
        return True
    finally:
        session.close()

def fn_wallet_shards_add(pc,shards):
    session = Session()

    try:
        wallet = session.query(Wallet)\
                        .filter(Wallet.id == pc.id)\
                        .one_or_none()

        wallet.broken    += shards[0]
        wallet.common    += shards[1]
        wallet.uncommon  += shards[2]
        wallet.rare      += shards[3]
        wallet.epic      += shards[4]
        wallet.legendary += shards[5]

        session.commit()
        session.refresh(wallet)
    except Exception as e:
        session.rollback()
        logger.error(f'Wallet/Shards Query KO (pcid:{pc.id}) [{e}]')
        return False
    else:
        logger.trace(f'Wallet/Shards Query OK (pcid:{pc.id})')
        return wallet
    finally:
        session.close()
