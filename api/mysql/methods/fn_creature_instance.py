# -*- coding: utf8 -*-

from mysql.session              import *
from mysql.models               import Creature

def fn_creature_instance_set(creature,instanceid):
    session = Session()

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
        msg = f'[SQL] Instance Query KO (creatureid:{creature.id},instanceid:{instanceid}) [{e}]'
        logger.error(msg)
    else:
        if creature_sql:
            logger.trace('Instance Query OK')
            return creature_sql
        else:
            return None
    finally:
        session.close()
