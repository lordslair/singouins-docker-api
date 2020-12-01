# -*- coding: utf8 -*-

from datetime           import datetime

from ..session          import Session
from ..models.creatures import HighScore

def fn_highscore_kill_set(pc):
    session = Session()

    try:
        hs = session.query(HighScore)\
                    .filter(HighScore.id == pc.id)\
                    .one_or_none()
        hs.kill += 1              # kill++
        hs.date  = datetime.now() # We update date
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (False,
                '[SQL] HighScore update failed (pcid:{})'.format(pc.id))
    else:
        return (True, None)
    finally:
        session.close()
