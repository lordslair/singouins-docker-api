# -*- coding: utf8 -*-

import requests

from flask                   import jsonify

from ..session               import Session
from ..models                import Creature

from ..utils.redis.effects   import *
from ..utils.redis.cds       import *
from ..utils.redis.statuses  import *
from ..utils.redis.pa        import *
from ..utils.redis.instances import get_instance

from .fn_creature            import fn_creature_get
from .fn_user                import fn_user_get

from variables               import (RESOLVER_HOST,
                                    RESOLVER_PORT)

#
# Queries /mypc/{pcid}/action/resolver/*
#

RESOLVER_URL = f'http://{RESOLVER_HOST}:{RESOLVER_PORT}'

# API: POST /mypc/<int:creatureid>/action/resolver/move
def mypc_action_resolver_move(username,creatureid,path):
    creature    = fn_creature_get(None,creatureid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if creature is None:
        return (200,
                False,
                f'Creature not found (creatureid:{creatureid})',
                None)
    if creature.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (creatureid:{creatureid},username:{username})',
                None)
    if creature.instance is None:
        return (200,
                False,
                f'Creature not in an instance (creatureid:{creatureid})',
                None)

    try:
        view  = session.query(Creature).filter(Creature.instance == creature.instance).all()
    except Exception as e:
        return (200,
                False,
                f'[SQL] View query failed (username:{username},creatureid:{creature.id}) [{e}]',
                None)

    try:
        instance = get_instance(creature.instance)
    except Exception as e:
        return (200,
                False,
                f'[Redis get_instance()] Instance query failed (creatureid:{creature.id},instanceid:{creature.instance}) [{e}]',
                None)
    else:
        if instance == False:
            return (200,
                    False,
                    f'[Redis get_instance()] Instance query failed (creatureid:{creature.id},instanceid:{creature.instance})',
                    None)

    creatures   = []
    for creature_in_instance in view:
        # Creatures fetching
        # If needed we convert the date
        if isinstance(creature_in_instance.date, datetime):
            creature_in_instance.date = creature_in_instance.date.strftime('%Y-%m-%d %H:%M:%S')
        # We load the Creature dataclass into a python dict
        dict        = dataclasses.asdict(creature_in_instance)
        # We populate the creature dict in creatures array
        creatures.append(dict)

    # Supposedly got all infos
    payload = { "context": {
                    "map": instance['map'],
                    "instance": creature.instance,
                    "creatures": creatures,
                    "effects": get_instance_effects(creature),
                    "status": [],
                    "cd": get_instance_cds(creature),
                    "pa": get_pa(creature.id)[3]
                  },
                  "fightEvent": {
                     "name":"RegularMovesFightClass",
                     "type":3,
                     "actor":1,
                     "params":{
                        "type":"target",
                        "destinationType":"tile",
                        "destination":None,
                        "options":{
                           "path": path
                        }
                     }
                  }
              }

    try:
        response  = requests.post(f'{RESOLVER_URL}/', json = payload)
    except Exception as e:
        return (200,
                False,
                f'[Resolver] Request failed (creatureid:{creature.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'[Resolver] Request answered (creatureid:{creature.id})',
                {"resolver": json.loads(response.text),
                "internal": payload})
    finally:
        session.close()
