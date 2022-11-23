# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger
from random                     import randint, choices

from nosql.metas                import metaArmors, metaWeapons
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisWallet   import RedisWallet
from nosql.publish              import publish
from nosql.queue                import yqueue_put

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

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
def creature_kill(creatureid, victimid):
    request_internal_token_check(request)

    Creature = RedisCreature().get(creatureid)
    h = creature_check(Creature)

    CreatureVictim = RedisCreature().get(victimid)
    if CreatureVictim is None:
        msg = f'{h} Victim not found (victimid:{victimid})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # We generate the drops
    # Currency
    try:
        currency = get_currency(CreatureVictim)
    except Exception as e:
        msg = f'{h} Currency Generation KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if currency:
            msg = f'{h} Currency Generation OK (currency:{currency})'
            logger.debug(msg)
    # Loots
    try:
        loots = get_loots(CreatureVictim)
    except Exception as e:
        msg = f'{h} Loot Generation KO [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        if loots:
            msg = f'{h} Loot Generation OK (loots:{len(loots)})'
            logger.debug(msg)

    # We check if the killer is in a Squad or not
    if Creature.squad is None:
        try:
            try:
                # We add loot only to the killer
                creature_wallet = RedisWallet(Creature)
                if Creature.race <= 4:
                    # It is a Singouin, we add bananas
                    creature_wallet.incr('bananas', currency)
                else:
                    creature_wallet.incr('sausages', currency)
            except Exception as e:
                msg = f'{h} Currency Add KO [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
            else:
                if currency:
                    msg = f'{h} Currency Add OK (currency:{currency})'
                    logger.debug(msg)

            # XP is generated
            try:
                xp_gained = CreatureVictim.level
                Creature.xp += xp_gained
            except Exception as e:
                msg = f'{h} XP add KO [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
            else:
                msg = f'{h} XP add OK (xp:{xp_gained})'
                logger.debug(msg)

            for loot in loots:
                # Items are added
                try:
                    Item = RedisItem(Creature).new(loot)
                except Exception as e:
                    msg = f'{h} Loot Add KO (loot:{loot}) [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    if Item:
                        msg = f'{h} Loot Add OK (loot:{loot})'
                        logger.debug(msg)

            # Now we send the WS messages for loot/drops
            # Broadcast Queue
            queue = 'broadcast'
            qmsg = {
                "ciphered": False,
                "payload": {
                    "id": Creature.id,
                    "loot": {
                         "currency": currency,
                         "items": loots,
                         "xp": xp_gained,
                    },
                    "action": "loot",
                },
                "route": "mypc/{id1}/action/resolver/skill/{id2}",
                "scope": {
                    "id": None,
                    "scope": "broadcast"
                    }
                }
            yqueue_put(queue, qmsg)

        except Exception as e:
            msg = f'{h} Solo drops KO (victimid:{victimid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        else:
            msg = f'{h} Solo drops OK (victimid:{victimid})'
            logger.debug(msg)

    else:
        try:
            # We need to get the squad members list
            try:
                squad = Creature.squad.replace('-', ' ')
                instance = Creature.instance.replace('-', ' ')
                SquadMembers = RedisCreature().search(
                    f"(@squad:{squad}) & "
                    f"(@squad_rank:-Pending) & "
                    f"(@instance:{instance})"
                    )
            except Exception as e:
                msg = f'{h} Squad Query KO (squadid:{Creature.squad}) [{e}]'
                logger.error(msg)
                return jsonify({"success": False,
                                "msg":     msg,
                                "payload": None}), 200
            else:
                if SquadMembers:
                    msg = f'{h} Squad Query OK (members:{len(SquadMembers)})'
                    logger.debug(msg)

            # We loop over the members
            for SquadMember in SquadMembers:
                CreatureMember = RedisCreature().get(SquadMember['id'])
                h = f'[Creature.id:{CreatureMember.id}]'
                try:
                    # We add loot only to the killer
                    creature_wallet = RedisWallet(CreatureMember)
                    if Creature.race <= 4:
                        # It is a Singouin, we add bananas
                        creature_wallet.incr('bananas',
                                             int(currency/len(SquadMembers)))
                    else:
                        creature_wallet.incr('sausages',
                                             int(currency/len(SquadMembers)))
                except Exception as e:
                    msg = (
                        f'{h} Currency Add KO '
                        f'(creatureid:{CreatureMember.id}) [{e}]'
                        )
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    if currency:
                        msg = f'{h} Currency Add OK (currency:{currency})'
                        logger.debug(msg)

                # XP is generated
                try:
                    xp_gained = int(CreatureVictim.level/len(SquadMembers))
                    Creature.xp += xp_gained
                except Exception as e:
                    msg = f'{h} XP add KO (xp:{xp_gained}) [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    msg = f'{h} XP add OK (xp:{xp_gained})'
                    logger.debug(msg)

            for loot in loots:
                # Items are added
                try:
                    # We need to pick who wins the item in the squad
                    winner = choices(SquadMembers, k=1)[0]
                    CreatureWinner = RedisCreature().get(winner['id'])
                    h = f'[Creature.id:{CreatureWinner.id}]'
                    Item = RedisItem(CreatureWinner).new(loot)

                    # Now we send the WS messages for loot/drops
                    # Broadcast Queue
                    queue = 'broadcast'
                    qmsg = {
                        "ciphered": False,
                        "payload": {
                            "id": CreatureWinner.id,
                            "loot": {
                                 "currency": currency,
                                 "items": loots,
                                 "xp": xp_gained,
                            },
                            "action": "loot",
                        },
                        "route": "mypc/{id1}/action/resolver/skill/{id2}",
                        "scope": {
                            "id": None,
                            "scope": "broadcast"
                            }
                        }
                    yqueue_put(queue, qmsg)

                    # We put the info in queue for ws Discord
                    if Item.metatype == 'weapon':
                        result = filter(lambda x: x["id"] == Item.metaid,
                                        metaWeapons)
                        itemmeta = dict(list(result)[0])  # Gruikfix
                    elif Item.metatype == 'armor':
                        result = filter(lambda x: x["id"] == Item.metaid,
                                        metaArmors)
                        itemmeta = dict(list(result)[0])  # Gruikfix
                    else:
                        logger.warning(f'Metatype unknown ({Item.metatype})')

                    queue = 'yarqueue:discord'
                    qmsg = {
                        "ciphered": False,
                        "payload": {
                            "color_int": color_int[Item.rarity],
                            "item": Item._asdict(),
                            "meta": itemmeta,
                            "winner": CreatureWinner._asdict(),
                            },
                        "embed": True,
                        "scope": f'Squad-{CreatureWinner.squad}',
                        }
                    yqueue_put(queue, qmsg)

                except Exception as e:
                    msg = f'{h} Loot Add KO (loot:{loot}) [{e}]'
                    logger.error(msg)
                    return jsonify({"success": False,
                                    "msg":     msg,
                                    "payload": None}), 200
                else:
                    if Item:
                        msg = f'{h} Loot Add OK (loot:{loot})'
                        logger.debug(msg)

        except Exception as e:
            msg = f'{h} Squad drops KO (victimid:{victimid}) [{e}]'
            logger.error(msg)
            return jsonify({"success": False,
                            "msg":     msg,
                            "payload": None}), 200
        else:
            msg = f'{h} Squad drops OK (victimid:{victimid})'
            logger.debug(msg)

    # Now we can REALLY kill the victim
    try:
        RedisStats(CreatureVictim).destroy()
        RedisCreature().destroy(victimid)
        # Now we send the WS messages
        # Broadcast Queue
        queue = 'broadcast'
        qmsg = {
            "ciphered": False,
            "payload": {
                "id": Creature.id,
                "target": {
                    "id": CreatureVictim.id,
                    "name": CreatureVictim.name
                },
                "action": None
            },
            "route": "mypc/{id1}/action/resolver/skill/{id2}",
            "scope": {
                "id": None,
                "scope": 'broadcast'
            }
        }
        try:
            yqueue_put(queue, qmsg)
        except Exception as e:
            msg = f'Queue PUT KO (queue:{queue}) [{e}]'
            logger.error(msg)
        else:
            msg = f'Queue PUT OK (queue:{queue})'
            logger.trace(msg)

        # Discord Queue
        queue = 'yarqueue:discord'
        if Creature.squad is not None:
            scope = f'Squad-{Creature.squad}'
        else:
            scope = None
        qmsg = {
            "ciphered": False,
            "payload": (
                f':pirate_flag: **{Creature.name}** '
                f'killed **{CreatureVictim.name}**'
                ),
            "embed": None,
            "scope": scope,
        }
        try:
            yqueue_put(queue, qmsg)
        except Exception as e:
            msg = f'Queue PUT KO (queue:{queue}) [{e}]'
            logger.error(msg)
        else:
            msg = f'Queue PUT OK (queue:{queue})'
            logger.trace(msg)

        # We put the info in pubsub channel for IA to regulate the instance
        try:
            pmsg = {
                "action": 'kill',
                "instance": CreatureVictim.instance,
                "creature": CreatureVictim._asdict(),
                }
            pchannel = 'ai-creature'
            publish(pchannel, jsonify(pmsg).get_data())
        except Exception as e:
            msg = f'Publish({pchannel}) KO [{e}]'
            logger.error(msg)
        else:
            logger.trace(f'Publish({pchannel}) OK')

        msg = f'Creature Kill OK ([{CreatureVictim.id}] {CreatureVictim.name})'
        logger.trace(msg)
    except Exception as e:
        msg = f'{h} Kill Creature KO (victimid:{CreatureVictim.id}) [{e}]'
        logger.error(msg)
        return jsonify({"success": False,
                        "msg":     msg,
                        "payload": None}), 200
    else:
        msg = f'{h} Kill Creature OK (victimid:{CreatureVictim.id})'
        logger.debug(msg)
        return jsonify({"success": True,
                        "msg":     msg,
                        "payload": Creature._asdict()}), 200

#
# Sub fonctions
#


def get_loots(victim):
    logger.trace(f'Generating Loots for victim: [{victim.id}] {victim.name}')
    # We initialize the global loot list
    loots    = []
    # We initialize some values lists
    rarities = [
        'Broken',
        'Common',
        'Uncommon',
        'Rare',
        'Epic',
        'Legendary'
        ]
    #
    metaItems = {
        "weapon": metaWeapons,
        "armor":  metaArmors,
        }
    # We find the weights for the rarity
    # By default, we go with rarity for Small creature
    weight     = {"b": 65, "c": 35, "u": 0, "r": 0, "e": 0, "l": 0}
    if victim.rarity == 'Medium':
        weight = {"b": 25, "c": 65, "u": 8, "r": 2, "e": 0, "l": 0}
    elif victim.rarity == 'Big':
        weight = {"b": 4, "c": 25, "u": 65, "r": 6, "e": 0, "l": 0}
    elif victim.rarity == 'Unique':
        weight = {"b": 3, "c": 4, "u": 25, "r": 65, "e": 3, "l": 0}
    elif victim.rarity == 'Boss':
        weight = {"b": 2, "c": 3, "u": 4, "r": 25, "e": 65, "l": 1}
    elif victim.rarity == 'God':
        weight = {"b": 1, "c": 2, "u": 3, "r": 4, "e": 25, "l": 65}

    for loot_id in range(1 + victim.level // 10):
        logger.trace(f'Generating Loot#{loot_id+1}')
        loot = {
            "bound": None,
            "bound_type": choices(['BoP', 'BoE'],
                                  weights=(95, 5),
                                  k=1)[0],
            "metatype": choices(['weapon', 'armor'],
                                weights=(50, 50),
                                k=1)[0],
            "metaid": None,
            "modded": False,
            "mods": None,
            "rarity": choices(rarities,
                              weights=(weight['b'],
                                       weight['c'],
                                       weight['u'],
                                       weight['r'],
                                       weight['e'],
                                       weight['l']),
                              k=1)[0],
            "state": randint(0, 100)
                }

        # We needed metatype to define the loot metaid
        loot['metaid'] = choices(metaItems[loot['metatype']], k=1)[0]['id']
        # If looted item id BoP, we need to fix it to the Creature
        if loot['bound_type'] == 'BoP':
            loot['bound'] = True
        else:
            loot['bound'] = False

        loots.append(loot)
        logger.trace(f'Generated  Loot#{loot_id+1}:{loot}')
    return loots


def get_currency(victim):
    logger.trace(f'Generating Currency for [{victim.id}] {victim.name}')
    currency = (victim.level // 10) * 100 + randint(1, 100)
    logger.trace(f'Generated  Currency:{currency}')
    return currency
