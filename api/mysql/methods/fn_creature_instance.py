# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import Creature


def fn_creature_instance_set(creature, instanceid):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        creature_sql = session.query(Creature)\
                              .filter(Creature.id == creature.id)\
                              .one_or_none()
        if creature_sql:
            creature_sql.instance = instanceid

        session.commit()
        session.refresh(creature_sql)
    except Exception as e:
        session.rollback()
        msg = f'{h} Instance Query KO (instanceid:{instanceid}) [{e}]'
        logger.error(msg)
    else:
        if creature_sql:
            logger.trace('Instance Query OK')
            return creature_sql
        else:
            logger.warning('Instance Query KO - NotFound')
            return None
    finally:
        session.close()
