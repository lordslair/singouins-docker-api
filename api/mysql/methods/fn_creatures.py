# -*- coding: utf8 -*-

import dataclasses
import datetime

from ..session           import Session
from ..models            import Creature

def fn_creatures_in_instance(instanceid):
    session = Session()

    try:
        view  = session.query(Creature)\
                       .filter(Creature.instance == instanceid)\
                       .all()
    except Exception as e:
        return None
    else:
        creatures   = []
        for creature in view:
            # Creatures fetching
            # If needed we convert the date
            if isinstance(creature.date, datetime.date):
                creature.date = creature.date.strftime('%Y-%m-%d %H:%M:%S')
            # We load the Creature dataclass into a python dict
            dict        = dataclasses.asdict(creature)

            if dict['hp']:     del dict['hp']
            if dict['hp_max']: del dict['hp_max']
            # We populate the creature dict in creatures array
            creatures.append(dict)

        return(creatures)
    finally:
        session.close()
