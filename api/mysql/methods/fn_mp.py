# -*- coding: utf8 -*-

import textwrap

from mysql.session              import Session
from mysql.models               import MP, Creature
from mysql.methods.fn_creature  import fn_creature_get

from nosql                      import * # Custom internal module for Redis queries

def fn_mp_addressbook_get(creature):
    session = Session()

    try:
        addressbook = session.query(Creature)\
                             .filter(Creature.race < 10)\
                             .with_entities(Creature.id,Creature.name)\
                             .all()
    except Exception as e:
        logger.error(f'Addressbook Query KO [{e}]')
        return None
    else:
        if addressbook:
            logger.trace(f'Addressbook Query OK')
            return addressbook
        else:
            return None
    finally:
        session.close()

def fn_mp_add(creature,pcsrcid,dsts,subject,body):
    session = Session()

    try:
        for pcdstid in dsts:
            pcdst   = fn_creature_get(None,pcdstid)[3]
            if pcdst:
                mp = MP(src_id  = creature.id,
                        src     = creature.name,
                        dst_id  = pcdst.id,
                        dst     = pcdst.name,
                        subject = subject,
                        body    = body)
                session.add(mp)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'MPs Query KO [{e}]')
        return None
    else:
        logger.trace(f'MPs Query OK')
        return True
    finally:
        session.close()

def fn_mp_del_one(creature,mpid):
    session = Session()

    try:
        mp = session.query(MP)\
                    .filter(MP.dst_id == creature.id)\
                    .filter(MP.id == mpid)\
                    .one_or_none()

        if not mp:
            logger.trace(f'MP Query Useless - No MP to delete')

        session.delete(mp)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'MP Query KO [{e}]')
        return None
    else:
        logger.trace(f'MP Query OK')
        return True
    finally:
        session.close()

def fn_mp_get_all(creature):
    session = Session()

    try:
        mps = session.query(MP)\
                     .filter(MP.dst_id == creature.id)\
                     .all()
    except Exception as e:
        logger.error(f'MPs Query KO [{e}]')
        return None
    else:
        if mps:
            for mp in mps:
                mp.body = textwrap.shorten(mp.body, width=50, placeholder="...")
            logger.trace(f'MPs Query OK')
            return mps
        else:
            return None
    finally:
        session.close()

def fn_mp_get_one(creature,mpid):
    session = Session()

    try:
        mp = session.query(MP)\
                    .filter(MP.dst_id == creature.id)\
                    .filter(MP.id == mpid)\
                    .one_or_none()
    except Exception as e:
        logger.error(f'MP Query KO [{e}]')
        return None
    else:
        logger.trace(f'MP Query OK')
        return mp
    finally:
        session.close()
