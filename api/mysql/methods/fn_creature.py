# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import Creature


def fn_creature_get(pcname, pcid):
    session = Session()

    try:
        if pcid:
            pc = session.query(Creature)\
                        .filter(Creature.id == pcid)\
                        .one_or_none()
        elif pcname:
            pc = session.query(Creature)\
                        .filter(Creature.name == pcname)\
                        .one_or_none()
        else:
            message = f'Wrong pcid/pcname (pcid:{pcid},pcname:{pcname})'
            logger.warning(message)
            return (200, False, message, None)
    except Exception as e:
        message = f'[SQL] PC query failed (pcid:{pcid},pcname:{pcname}) [{e}]'
        logger.error(message)
        return (200, False, message, None)
    else:
        if pc:
            message = f'PC successfully found (pcid:{pcid},pcname:{pcname})'
            logger.trace(message)
            return (200, True, message, pc)
        else:
            message = f'PC does not exist (pcid:{pcid},pcname:{pcname})'
            logger.trace(message)
            return (200, False, message, None)
    finally:
        session.close()
