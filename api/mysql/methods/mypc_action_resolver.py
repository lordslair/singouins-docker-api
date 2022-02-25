# -*- coding: utf8 -*-

import json
import requests

from ..session               import Session
from ..models                import Creature

from .fn_creature            import *
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
        map                = instances.get_instance(creature.instance)['map']
        creatures          = fn_creatures_in_instance(creature.instance)
        creatures_effects  = effects.get_instance_effects(creature)
        creatures_statuses = statuses.get_instance_statuses(creature)
        creatures_cds      = cds.get_instance_cds(creature)
        pas                = pa.get_pa(creature.id)[3]
    except Exception as e:
        return (200,
                False,
                f'Information query failed [{e}]',
                None)

    # Supposedly got all infos
    payload = { "context": {
                    "map": map,
                    "instance": creature.instance,
                    "creatures": creatures,
                    "effects": creatures_effects,
                    "status": creatures_statuses,
                    "cd": creatures_cds,
                    "pa": pas
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
        cd  = cds.get_cd(creature,skillmetaid)
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
        map                = instances.get_instance(creature.instance)['map']
        creatures          = fn_creatures_in_instance(creature.instance)
        creatures_effects  = effects.get_instance_effects(creature)
        creatures_statuses = statuses.get_instance_statuses(creature)
        creatures_cds      = cds.get_instance_cds(creature)
        pas                = pa.get_pa(creature.id)[3]
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
                    "effects": creatures_effects,
                    "status": creatures_statuses,
                    "cd": creatures_cds,
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
