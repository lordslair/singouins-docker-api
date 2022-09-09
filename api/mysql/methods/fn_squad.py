# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import Creature, Squad


def fn_squad_add_one(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        squad = Squad(leader=creature.id)

        session.add(squad)
        session.commit()
        session.refresh(squad)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Squad Query KO [{e}]')
        return None
    else:
        if squad:
            logger.trace(f'{h} Squad Query OK')
            return squad
        else:
            logger.trace(f'{h} Squad Query KO - NotFound')
            return False
    finally:
        session.close()


def fn_squad_delete_one(squadid):
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    try:
        squad    = session.query(Squad)\
                          .filter(Squad.id == squadid)\
                          .one_or_none()

        session.delete(squad)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Squad Query KO [{e}]')
        return None
    else:
        logger.trace(f'{h} Squad Query OK')
        return True
    finally:
        session.close()


def fn_squad_get_one(squadid):
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    if not isinstance(squadid, int):
        logger.error(f'{h} Squad ID should be INT (squadid:{squadid})')
        return None

    try:
        squad   = session.query(Squad)\
                         .filter(Squad.id == squadid)\
                         .one_or_none()
        members = session.query(Creature)\
                         .filter(Creature.squad == squadid)\
                         .filter(Creature.squad_rank != 'Pending')\
                         .all()
        pending = session.query(Creature)\
                         .filter(Creature.squad == squadid)\
                         .filter(Creature.squad_rank == 'Pending')\
                         .all()
    except Exception as e:
        logger.error(f'{h} Squad Query KO (squadid:{squadid}) [{e}]')
        return None
    else:
        if squad:
            logger.trace(f'{h} Squad Query OK (squadid:{squadid})')
            return {"squad": squad,
                    "members": members,
                    "pending": pending}
        else:
            logger.trace(f'{h} Squad Query KO - Not Found (squadid:{squadid})')
            return False
    finally:
        session.close()


def fn_squad_get_all():
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    try:
        squads = session.query(Squad)\
                        .all()
    except Exception as e:
        logger.error(f'{h} Squads Query KO [{e}]')
        return None
    else:
        if squads:
            logger.trace(f'{h} Squads Query OK')
            return squads
        else:
            logger.trace(f'{h} Squads Query KO - Not Found')
            return False
    finally:
        session.close()


def fn_squad_set_rank(creature, squadid, rank):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        member  = session.query(Creature)\
                         .filter(Creature.id == creature.id)\
                         .one_or_none()

        member.squad      = squadid
        member.squad_rank = rank
        session.commit()
        session.refresh(member)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Squad Query KO (squadid:{squadid}) [{e}]')
        return None
    else:
        if member:
            logger.trace(f'{h} Squad Query OK (squadid:{squadid})')
            return member
        else:
            logger.warning(f'{h} Squad Query KO - NotFound '
                           f'(squadid:{squadid})')
            return False
    finally:
        session.close()
