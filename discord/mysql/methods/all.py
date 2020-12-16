# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models           import *

from .fn_creature       import *

def query_up():
    session = Session()

    try:
        result = session.query(User).first()
    except Exception as e:
        print(e)
    else:
        if result: return result
    finally:
        session.close()

def query_get_user(discordname):
    session = Session()

    result = session.query(User).filter(User.d_name == discordname).one_or_none()
    session.close()

    if result: return result

def query_validate_user(discordname):
    session = Session()

    try:
        user = session.query(User).filter(User.d_name == discordname).one_or_none()
        user.d_ack = True
        user.date  = datetime.now()
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return None

def query_histo(arg):
    session = Session()

    if   arg == 'CreaturesLevel' or arg == 'CL': result = session.query(Creature.level).all()
    elif arg == 'CreaturesRace'  or arg == 'CR': result = session.query(Creature.race).all()
    session.close()

    if result: return result

def query_get_creature(pcid):
    session = Session()

    result = session.query(User).filter(User.d_name == discordname).one_or_none()
    session.close()

    if result: return result

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
