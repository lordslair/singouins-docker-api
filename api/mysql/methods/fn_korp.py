# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import Creature, Korp


def fn_korp_add_one(creature, korpname):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        korp = Korp(leader=creature.id,
                    name=korpname)

        session.add(korp)
        session.commit()
        session.refresh(korp)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Korp Query KO [{e}]')
        return None
    else:
        if korp:
            logger.trace(f'{h} Korp Query OK')
            return korp
        else:
            logger.trace(f'{h} Korp Query KO - NotFound')
            return False
    finally:
        session.close()


def fn_korp_delete_one(korpid):
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    try:
        korp    = session.query(Korp)\
                         .filter(Korp.id == korpid)\
                         .one_or_none()

        session.delete(korp)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Korp Query KO [{e}]')
        return None
    else:
        logger.trace(f'{h} Korp Query OK')
        return True
    finally:
        session.close()


def fn_korp_get_one(korpid):
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    if not isinstance(korpid, int):
        logger.error(f'{h} Korp ID should be INT (korpid:{korpid})')
        return None

    try:
        korp    = session.query(Korp)\
                         .filter(Korp.id == korpid)\
                         .one_or_none()
        members = session.query(Creature)\
                         .filter(Creature.korp == korpid)\
                         .filter(Creature.korp_rank != 'Pending')\
                         .all()
        pending = session.query(Creature)\
                         .filter(Creature.korp == korpid)\
                         .filter(Creature.korp_rank == 'Pending')\
                         .all()
    except Exception as e:
        logger.error(f'{h} Korp Query KO (korpid:{korpid}) [{e}]')
        return None
    else:
        if korp:
            logger.trace(f'{h} Korp Query OK (korpid:{korpid})')
            return {"korp": korp,
                    "members": members,
                    "pending": pending}
        else:
            logger.trace(f'{h} Korp Query KO - NotFound (korpid:{korpid})')
            return False
    finally:
        session.close()


def fn_korp_get_one_by_name(korpname):
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    if not isinstance(korpname, str):
        logger.error(f'{h} Korp Name should be STR (korpname:{korpname})')
        return None

    try:
        korp    = session.query(Korp)\
                         .filter(Korp.name == korpname)\
                         .one_or_none()
        if korp:
            members = session.query(Creature)\
                             .filter(Creature.korp == korp.id)\
                             .filter(Creature.korp_rank != 'Pending')\
                             .all()
            pending = session.query(Creature)\
                             .filter(Creature.korp == korp.id)\
                             .filter(Creature.korp_rank == 'Pending')\
                             .all()
        else:
            members = None
            pending = None
    except Exception as e:
        logger.error(f'{h} Korp Query KO (korpname:{korpname}) [{e}]')
        return None
    else:
        if korp:
            logger.trace(f'{h} Korp Query OK (korpname:{korpname})')
            return {"korp": korp,
                    "members": members,
                    "pending": pending}
        else:
            logger.trace(f'{h} Korp Query KO - NotFound (korpname:{korpname})')
            return False
    finally:
        session.close()


def fn_korp_get_all():
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    try:
        korps = session.query(Korp)\
                       .all()
    except Exception as e:
        logger.error(f'{h} Korps Query KO [{e}]')
        return None
    else:
        if korps:
            logger.trace(f'{h} Korps Query OK')
            return korps
        else:
            logger.trace(f'{h} Korps Query KO - Not Found')
            # We force an empty list as return as it could be "normal"
            return []
    finally:
        session.close()


def fn_korp_set_rank(creature, korpid, rank):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        member  = session.query(Creature)\
                         .filter(Creature.id == creature.id)\
                         .one_or_none()

        member.korp      = korpid
        member.korp_rank = rank
        session.commit()
        session.refresh(member)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Korp Query KO (korpid:{korpid}) [{e}]')
        return None
    else:
        if member:
            logger.trace(f'{h} Korp Query OK (korpid:{korpid})')
            return member
        else:
            logger.trace(f'{h} Korp Query KO - NotFound (korpid:{korpid})')
            return False
    finally:
        session.close()
