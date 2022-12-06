# -*- coding: utf8 -*-

from flask                      import jsonify, request
from loguru                     import logger
from random                     import randint, choices

from nosql.metas                import metaArmors, metaWeapons
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisWallet   import RedisWallet
from nosql.publish              import publish
from nosql.queue                import yqueue_put

from utils.routehelper          import (
    creature_check,
    request_internal_token_check,
    )

from variables                  import YQ_BROADCAST, YQ_DISCORD

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
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
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
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        if loots:
            msg = f'{h} Loot Generation OK (loots:{len(loots)})'
            logger.debug(msg)

    if Creature.account is not None and Creature.squad is None:
        # We want Playable Creatures NOT in Squad
        # (Solo players)
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
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
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
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
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
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
                else:
                    if Item:
                        msg = f'{h} Loot Add OK (loot:{loot})'
                        logger.debug(msg)

            # Now we send the WS messages for loot/drops
            # Broadcast Queue
            yqueue_put(
                YQ_BROADCAST,
                {
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
                        },
                    }
                )

        except Exception as e:
            msg = f'{h} Solo drops KO (victimid:{victimid}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'{h} Solo drops OK (victimid:{victimid})'
            logger.debug(msg)

    elif Creature.account is not None and Creature.squad is not None:
        # We want Playable Creatures in Squad
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
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
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
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
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
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
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
                except Exception as e:
                    msg = f'{h} Loot Add KO (loot:{loot}) [{e}]'
                    logger.error(msg)
                    return jsonify(
                        {
                            "success": False,
                            "msg": msg,
                            "payload": None,
                        }
                    ), 200
                else:
                    if Item is None:
                        msg = f'{h} Loot Add KO (loot:{loot})'
                        logger.warning(msg)

                # Now we send the WS messages
                # Broadcast Queue
                yqueue_put(
                    YQ_BROADCAST,
                    {
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
                            },
                        }
                    )
                # Discord Queue
                if CreatureWinner.squad is not None:
                    scope = f'Squad-{CreatureWinner.squad}'
                else:
                    scope = None
                yqueue_put(
                    YQ_DISCORD,
                    {
                        "ciphered": False,
                        "payload": {
                            "item": Item._asdict(),
                            "winner": CreatureWinner._asdict(),
                            },
                        "embed": True,
                        "scope": scope,
                        }
                    )

        except Exception as e:
            msg = f'{h} Squad drops KO (victimid:{victimid}) [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            msg = f'{h} Squad drops OK (victimid:{victimid})'
            logger.debug(msg)

    else:
        # Here are the Creatures (AI) who killed Players
        # They are here as they don't deserve loots
        pass

    # We set the HighScores
    # If the Victim is a Player > HighScore
    if CreatureVictim.account is not None:
        RedisHS(CreatureVictim).incr('global_deaths')
    # If the Victim is a Player > HighScore
    if Creature.account is not None:
        RedisHS(Creature).incr('global_kills')

    # Now we can REALLY kill the victim
    try:
        if CreatureVictim.account is None:
            # It is a NON playable Creature (Monster)
            # We destroy the RedisStats
            RedisStats(CreatureVictim).destroy()
            # We destroy the Creature
            RedisCreature().destroy(victimid)
        else:
            # It is a playable Creature (Singouin)
            # We DO NOT delete it
            # We set his HP to 50% of hp_max
            Stats = RedisStats(CreatureVictim)
            Stats.hp = round(Stats.hpmax / 2)
            # We push him out of the Instance
            CreatureVictim.instance = None

        # Now we send the WS messages
        # Broadcast Queue
        yqueue_put(
            YQ_BROADCAST,
            {
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
                    },
                }
            )
        # Discord Queue
        if Creature.squad is not None:
            scope = f'Squad-{Creature.squad}'
        else:
            scope = None
        yqueue_put(
            YQ_DISCORD,
            {
                "ciphered": False,
                "payload": (
                    f':pirate_flag: **{Creature.name}** '
                    f'killed **{CreatureVictim.name}**'
                    ),
                "embed": None,
                "scope": scope,
            }
            )

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
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{h} Kill Creature OK (victimid:{CreatureVictim.id})'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature._asdict(),
            }
        ), 200

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
