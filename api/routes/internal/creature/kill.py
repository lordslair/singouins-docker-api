# -*- coding: utf8 -*-

from flask                      import Flask, jsonify, request
from loguru                     import logger
from random                     import randint,choices

from mysql.methods.fn_creature  import (fn_creature_get,
                                        fn_creature_kill,
                                        fn_creature_xp_add)

from mysql.methods.fn_inventory import fn_item_add
from mysql.methods.fn_squad     import fn_squad_get_one

from nosql.metas                import *
from nosql.models.RedisWallet   import *
from nosql.queue                import *

from variables                  import API_INTERNAL_TOKEN

# We define color lists for embeds, messages, etc
color_int              = {}
color_int['Broken']    = 10197915
color_int['Common']    = 16777215
color_int['Uncommon']  = 8311585
color_int['Rare']      = 4886754
color_int['Epic']      = 9442302
color_int['Legendary'] = 16098851

color_hex              = {}
color_hex['Broken']    = '9B9B9B'
color_hex['Common']    = 'FFFFFF'
color_hex['Uncommon']  = '7ED321'
color_hex['Rare']      = '4A90E2'
color_hex['Epic']      = '9013FE'
color_hex['Legendary'] = 'F5A623'

color_dis              = {}
color_dis['Broken']    = ':brown_square:'
color_dis['Common']    = ':white_medium_square:'
color_dis['Uncommon']  = ':green_square:'
color_dis['Rare']      = ':blue_square:'
color_dis['Epic']      = ':purple_square:'
color_dis['Legendary'] = ':purple_square:'

#
# Routes /internal
#
# /internal/creature/*
# API: POST /internal/creature/{creatureid}/kill/{victimid}
def creature_kill(creatureid,victimid):
    if request.headers.get('Authorization') != f'Bearer {API_INTERNAL_TOKEN}':
        msg = f'Token not authorized'
        logger.warning(msg)
        return jsonify({"success": False, "msg": msg, "payload": None}), 403

    # Pre-flight checks
    creature    = fn_creature_get(None,creatureid)[3]
    if creature is None:
        return jsonify({"success": False,
                        "msg":     f'Creature unknown (creatureid:{creatureid})',
                        "payload": None}), 200
    victim      = fn_creature_get(None,victimid)[3]
    if victim is None:
        return jsonify({"success": False,
                        "msg":     f'Victim unknown (victimid:{victimid})',
                        "payload": None}), 200

    # We generate the drops
    # Currency
    try:
        currency = get_currency(victim)
    except Exception as e:
        msg = f'Currency Generation KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if currency:
            msg = f'Currency Generation OK (creatureid:{creature.id},currency:{currency})'
            logger.debug(msg)
    # Loots
    try:
        loots = get_loots(victim)
    except Exception as e:
        msg = f'Loot Generation KO (creatureid:{creature.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if loots:
            msg = f'Loot Generation OK (creatureid:{creature.id},loots:{len(loots)})'
            logger.debug(msg)

    # We check if the killer is in a Squad or not
    if creature.squad is None:
        try:
            try:
                # We add loot only to the killer
                redis_wallet = RedisWallet(creature)
                if creature.race <= 4:
                    # It is a Singouin, we add bananas
                    redis_wallet.bananas += currency
                else:
                    redis_wallet.sausages += currency
                # We store the Wallet
                redis_wallet.store()
            except Exception as e:
                msg = f'Currency Add KO (creatureid:{creature.id}) [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
            else:
                if currency:
                    msg = f'Currency Add OK (creatureid:{creature.id},currency:{currency})'
                    logger.debug(msg)

            # XP is generated
            try:
                xp_gained = victim.level
                xp_added  = fn_creature_xp_add(creature,xp_gained)
            except Exception as e:
                msg = f'XP add KO (creatureid:{creature.id}) [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
            else:
                msg = f'XP add OK (creatureid:{creature.id},xp:{xp_gained})'
                logger.debug(msg)

            for loot in loots:
                # Items are added
                try:
                    item = fn_item_add(creature,loot)
                except Exception as e:
                    msg = f'Loot Add KO (creatureid:{creature.id},loot:{loot}) [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    if item:
                        msg = f'Loot Add OK (creatureid:{creature.id},loot:{loot})'
                        logger.debug(msg)

            # Now we send the WS messages for loot/drops
            # Broadcast Queue
            queue = 'broadcast'
            qmsg = {
                       "ciphered":False,
                       "payload":{
                          "id":creature.id,
                          "loot":{
                             "currency":currency,
                             "items":loots,
                             "xp":xp_gained
                          },
                          "action":"loot"
                       },
                       "route":"mypc/{id1}/action/resolver/skill/{id2}",
                       "scope":{
                          "id":None,
                          "scope":"broadcast"
                       }
                    }
            try:
                yqueue_put(queue, qmsg)
            except Exception as e:
                msg = f'Queue PUT KO (queue:{queue},topic:loot) [{e}]'
                logger.error(msg)
            else:
                msg = f'Queue PUT OK (queue:{queue},topic:loot)'
                logger.trace(msg)

            """ NEED TO RECODE
            # We put the info in queue for ws Discord
            qmsg = {"ciphered": False,
            "payload": {"color_int": color_int[item.rarity],
                        "path": f'/resources/sprites/{item.metatype}s/{item.metaid}.png',
                        "title": f"{itemmeta['name']}",
                        "item": f'Looted by [{pcsquad.id}] {pcsquad.name}',
                        "footer": f'NB: This item is [{item.bound_type}]'},
            "embed": True,
            "scope": f'Squad-{pc.squad}'}
            yqueue_put('yarqueue:discord', qmsg)
            """

        except Exception as e:
            msg = f'Solo drops KO (creatureid:{creature.id},victimid:{victimid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        else:
            msg = f'Solo drops OK (creatureid:{creature.id},victimid:{victimid})'
            logger.debug(msg)

    else:
        try:
            # We need to get the squad members list
            try:
                squad = fn_squad_get_one(creature.squad)
                members = squad['members']
            except Exception as e:
                msg = f'Squad Query KO (creatureid:{creature.id},squadid:{creature.squad}) [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
            else:
                if members:
                    msg = f'Squad Query OK (creatureid:{creature.id},members:{len(members)})'
                    logger.debug(msg)

            # We loop over the members
            for member in members:
                try:
                    # We add loot only to the killer
                    redis_wallet = RedisWallet(member)
                    if creature.race <= 4:
                        # It is a Singouin, we add bananas
                        redis_wallet.bananas += int(currency/len(members))
                    else:
                        redis_wallet.sausages += int(currency/len(members))
                    # We store the Wallet
                    redis_wallet.store()
                except Exception as e:
                    msg = f'Currency Add KO (creatureid:{member.id}) [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    if currency:
                        msg = f'Currency Add OK (creatureid:{member.id},currency:{currency})'
                        logger.debug(msg)

                # XP is generated
                try:
                    xp_gained = int(victim.level/len(members))
                    xp_added  = fn_creature_xp_add(member,xp_gained)
                except Exception as e:
                    msg = f'XP add KO (creatureid:{member.id},xp:{xp_gained}) [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    msg = f'XP add OK (creatureid:{member.id},xp:{xp_gained})'
                    logger.debug(msg)

            for loot in loots:
                # Items are added
                try:
                    # We need to pick who wins the item in the squad
                    winner = choices(members,k=1)[0]
                    item = fn_item_add(winner,loot)

                    # Now we send the WS messages for loot/drops
                    # Broadcast Queue
                    queue = 'broadcast'
                    qmsg = {
                               "ciphered":False,
                               "payload":{
                                  "id":winner.id,
                                  "loot":{
                                     "currency":currency,
                                     "items":loots,
                                     "xp":xp_gained
                                  },
                                  "action":"loot"
                               },
                               "route":"mypc/{id1}/action/resolver/skill/{id2}",
                               "scope":{
                                  "id": None,
                                  "scope":"broadcast"
                               }
                            }
                    try:
                        yqueue_put(queue, qmsg)
                    except Exception as e:
                        msg = f'Queue PUT KO (queue:{queue},topic:loot) [{e}]'
                        logger.error(msg)
                    else:
                        msg = f'Queue PUT OK (queue:{queue},topic:loot)'
                        logger.trace(msg)

                except Exception as e:
                    msg = f'Loot Add KO (creatureid:{winner.id},loot:{loot}) [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    if item:
                        msg = f'Loot Add OK (creatureid:{winner.id},loot:{loot})'
                        logger.debug(msg)

        except Exception as e:
            msg = f'Squad drops KO (creatureid:{creature.id},victimid:{victimid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        else:
            msg = f'Squad drops OK (creatureid:{creature.id},victimid:{victimid})'
            logger.debug(msg)

    # Now we can REALLY kill the victim
    try:
        kill = fn_creature_kill(creature,victim,None)
    except Exception as e:
        msg = f'Kill Creature KO (creatureid:{creature.id},victimid:{victimid}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if kill:
            msg = f'Kill Creature OK (creatureid:{creature.id},victimid:{victimid})'
            logger.debug(msg)
            return jsonify({"success": True,
                            "msg":     msg,
                            "payload": creature}), 200
        else:
            msg = f'Kill Creature KO (creatureid:{creature.id},victimid:{victimid})'
            logger.error(msg)

#
# Sub fonctions
#

def get_loots(victim):
    logger.trace(f'Generating Loots for victim: [{victim.id}] {victim.name}')
    # We initialize the global loot list
    loots    = []
    # We initialize some values lists
    rarities = ['Broken','Common','Uncommon','Rare','Epic','Legendary']
    #
    metaWeapons = get_meta('weapon')
    metaArmors  = get_meta('armor')
    metaItems   = {
                    "weapon": metaWeapons,
                    "armor":  metaArmors,
                  }
    # We find the weights for the rarity
    # By default, we go with rarity for Small creature
    weight     = {"b": 65,"c": 35,"u": 0,"r": 0,"e": 0,"l": 0}
    if victim.rarity == 'Medium':
        weight = {"b": 25,"c": 65,"u": 8,"r": 2,"e": 0,"l": 0}
    elif victim.rarity == 'Big':
        weight = {"b": 4,"c": 25,"u": 65,"r": 6,"e": 0,"l": 0}
    elif victim.rarity == 'Unique':
        weight = {"b": 3,"c": 4,"u": 25,"r": 65,"e": 3,"l": 0}
    elif victim.rarity == 'Boss':
        weight = {"b": 2,"c": 3,"u": 4,"r": 25,"e": 65,"l": 1}
    elif victim.rarity == 'God':
        weight = {"b": 1,"c": 2,"u": 3,"r": 4,"e": 25,"l": 65}

    for loot_id in range(1 + victim.level // 10):
        logger.trace(f'Generating Loot#{loot_id+1}')
        loot =  {
                    "bound":      None,
                    "bound_type": choices(['BoP','BoE'],
                                          weights=(95, 5),
                                          k=1)[0],
                    "metatype":   choices(['weapon','armor'],
                                          weights=(50, 50),
                                          k=1)[0],
                    "metaid":     None,
                    "modded":     False,
                    "mods":       None,
                    "rarity":     choices(rarities,
                                          weights=(weight['b'],
                                                   weight['c'],
                                                   weight['u'],
                                                   weight['r'],
                                                   weight['e'],
                                                   weight['l']),
                                           k=1)[0],
                    "state":      randint(0,100)
                }

        # We needed metatype to define the loot metaid
        loot['metaid'] = choices(metaItems[loot['metatype']],k=1)[0]['id']
        # If looted item id BoP, we need to fix it to the Creature
        if loot['bound_type'] == 'BoP':
            loot['bound'] = True
        else:
            loot['bound'] = False

        loots.append(loot)
        logger.trace(f'Generated  Loot#{loot_id+1}:{loot}')
    return loots

def get_currency(victim):
    logger.trace(f'Generating Currency for victim: [{victim.id}] {victim.name}')
    currency = (victim.level // 10) * 100 + randint(1, 100)
    logger.trace(f'Generated  Currency:{currency}')
    return currency
