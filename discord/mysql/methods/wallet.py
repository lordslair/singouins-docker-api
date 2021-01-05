# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import Wallet

def query_wallet_get(pc):
    session = Session()

    try:
        wallet = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()
    except Exception as e:
        print(e)
    else:
        if wallet is None: return None

        rettext   = f'Creature : [{pc.id}] {pc.name}\n'
        rettext  += f'Currency : {wallet.currency}\n'
        rettext  += f'Shards\n'
        rettext  += f'    🟠 Legendary : {wallet.legendary}\n'
        rettext  += f'    🟣 Epic      : {wallet.epic}\n'
        rettext  += f'    🔵 Rare      : {wallet.rare}\n'
        rettext  += f'    🟢 Uncommon  : {wallet.uncommon}\n'
        rettext  += f'    ⚪ Common    : {wallet.common}\n'
        rettext  += f'    🟤 Broken    : {wallet.broken}\n'
        rettext  += f'Ammos\n'
        rettext  += f'    Arrows       : {wallet.arrow}\n'
        rettext  += f'    Bolts        : {wallet.bolt}\n'
        rettext  += f'    Shells       : {wallet.shell}\n'
        rettext  += f'    Cal .22      : {wallet.cal22}\n'
        rettext  += f'    Cal .223     : {wallet.cal223}\n'
        rettext  += f'    Cal .311     : {wallet.cal311}\n'
        rettext  += f'    Cal .50      : {wallet.cal50}\n'
        rettext  += f'    Cal .55      : {wallet.cal55}\n'
        return (f'```{rettext}```')
    finally:
        session.close()
