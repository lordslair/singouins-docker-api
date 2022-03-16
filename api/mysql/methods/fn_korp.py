# -*- coding: utf8 -*-

from mysql.session              import *
from mysql.models               import Creature,Korp

def fn_korp_add_one(pc,korpname):
    session = Session()

    try:
        korp = Korp(leader = pc.id,
                    name   = korpname)

        session.add(korp)
        session.commit()
        session.refresh(korp)
    except Exception as e:
        session.rollback()
        logger.error(f'Korp Query KO [{e}]')
        return None
    else:
        if korp:
            logger.trace(f'Korp Query OK (pcid:{pc.id})')
            return korp
        else:
            logger.trace(f'Korp Query KO - Not Found (pcid:{pc.id})')
            return False
    finally:
        session.close()

def fn_korp_delete_one(korpid):
    session = Session()

    try:
        korp    = session.query(Korp)\
                         .filter(Korp.id == korpid)\
                         .one_or_none()

        session.delete(korp)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'Korp Query KO [{e}]')
        return None
    else:
        logger.trace(f'Korp Query OK')
        return True
    finally:
        session.close()

def fn_korp_get_one(korpid):
    session = Session()

    if not isinstance(korpid, int):
        logger.error(f'Korp ID should be INT (korpid:{korpid})')
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
        logger.error(f'Korp Query KO (korpid:{korpid}) [{e}]')
        return None
    else:
        if korp:
            logger.trace(f'Korp Query OK (korpid:{korpid})')
            return {"korp": korp,
                    "members": members,
                    "pending": pending}
        else:
            logger.trace(f'Korp Query KO - Not Found (korpid:{korpid})')
            return False
    finally:
        session.close()

def fn_korp_get_one_by_name(korpname):
    session = Session()

    if not isinstance(korpname, str):
        logger.error(f'Korp Name should be STR (korpname:{korpname})')
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
        logger.error(f'Korp Query KO (korpname:{korpname}) [{e}]')
        return None
    else:
        if korp:
            logger.trace(f'Korp Query OK (korpname:{korpname})')
            return {"korp": korp,
                    "members": members,
                    "pending": pending}
        else:
            logger.trace(f'Korp Query KO - Not Found (korpname:{korpname})')
            return False
    finally:
        session.close()

def fn_korp_get_all():
    session = Session()

    try:
        korps = session.query(Korp)\
                       .all()
    except Exception as e:
        logger.error(f'Korps Query KO [{e}]')
        return None
    else:
        if korps:
            logger.trace(f'Korps Query OK')
            return korps
        else:
            logger.trace(f'Korps Query KO - Not Found')
            return False
    finally:
        session.close()

def fn_korp_set_rank(creature,korpid,rank):
    session = Session()

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
        logger.error(f'Korp Query KO (korpid:{korpid}) [{e}]')
        return None
    else:
        if member:
            logger.trace(f'Korp Query OK (creatureid:{creature.id})')
            return member
        else:
            logger.trace(f'Korp Query KO - Not Found (creatureid:{creature.id})')
            return False
    finally:
        session.close()
