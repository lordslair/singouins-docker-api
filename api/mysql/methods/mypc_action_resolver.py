# -*- coding: utf8 -*-

import json
import requests

from ..session               import Session
from ..models                import Creature

from ..utils.redis.effects   import get_instance_effects
from ..utils.redis.cds       import get_instance_cds,get_cd
from ..utils.redis.statuses  import get_instance_statuses
from ..utils.redis.pa        import *
from ..utils.redis.instances import get_instance

from .fn_creature            import fn_creature_get
from .fn_creatures           import fn_creatures_in_instance
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

# API: POST /mypc/<int:creatureid>/action/resolver/skill/<int:skillmetaid>
def mypc_action_resolver_skill(username,creatureid,skillmetaid):
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
    if not isinstance(skillmetaid, int):
        return (200,
                False,
                f'Bad SkillMeta id format (creatureid:{creatureid},skillmetaid:{skillmetaid})',
                None)

    try:
        cd  = get_cd(creature,skillmetaid)
    except Exception as e:
        return (200,
                False,
                f'[Redis:get_cd()] Query failed (creatureid:{creature.id}) [{e}]',
                None)
    else:
        if cd:
            # The skill was already used, and still on CD
            return (200,
                    False,
                    f'Skill already on CD (creatureid:{creature.id},skillmetaid:{skillmetaid})',
                    cd)

    try:
        map       = get_instance(creature.instance)['map']
        creatures = fn_creatures_in_instance(creature.instance)
        effects   = get_instance_effects(creature)
        statuses  = get_instance_statuses(creature)
        cds       = get_instance_cds(creature)
        pas       = get_pa(creature.id)[3]
    except Exception as e:
        return (200,
                False,
                f'Information query failed [{e}]',
                None)

    # Everythins if fine, we can build the payload
    # Supposedly got all infos
    payload = { "context": {
                    "map": map,
                    "instance": creature.instance,
                    "creatures": creatures,
                    "effects": effects,
                    "status": statuses,
                    "cd": cds,
                    "pa": pas
                  },
                  "fightEvent": {
                    "name": "WarsongActionsFightClass",
                    "type": 0,
                    "actor": 1,
                    "params": {
                      "type": "target",
                      "destinationType": "tile",
                      "destination": None
                    }
                  }
              }

    try:
        response  = requests.post(f'{RESOLVER_URL}/', json = payload)
    except Exception as e:
        return (200,
                False,
                f'[Resolver] Request failed (creatureid:{creature.id},skillmetaid:{skillmetaid}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'[Resolver] Request answered (creatureid:{creature.id},skillmetaid:{skillmetaid})',
                {"resolver": json.loads(response.text),
                "internal": payload})
