# -*- coding: utf8 -*-

import discord

from loguru import logger
from operator import itemgetter
from mongoengine import Q

from mongo.models.Creature import CreatureDocument
from mongo.models.Instance import InstanceDocument
from mongo.models.Item import ItemDocument

from variables import (
    metaIndexed,
    metaNames,
    rarity_item_types_emoji as rite,
    rarity_monster_types_emoji as rmte,
    )


async def get_instances_list(ctx: discord.AutocompleteContext):
    try:
        Instances = InstanceDocument.objects()
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
        return None
    else:
        db_list = []
        for Instance in Instances:
            db_list.append(
                discord.OptionChoice(f"{Instance.id} (map:{Instance.map})", value=str(Instance.id))
                )
        return db_list


async def get_metanames_list(ctx: discord.AutocompleteContext):
    # Get the current user input
    user_input = ctx.value.lower()
    try:
        db_list = []
        for meta in metaNames[ctx.options["metatype"]]:
            if user_input in meta['name'].lower():
                db_list.append(discord.OptionChoice(meta['name'], value=str(meta['_id'])))
    except Exception as e:
        logger.error(f'metaNames Query KO [{e}]')
        return None
    else:
        return db_list


async def get_monsters_in_instance_list(ctx: discord.AutocompleteContext):
    try:
        query = (Q(instance=ctx.options['instance_uuid']) & Q(race__gt=10))
        Creatures = CreatureDocument.objects(query)
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
        return None

    db_list = []
    for Creature in Creatures:
        metaRace = metaIndexed['race'][Creature.race]
        db_list.append(
            discord.OptionChoice(
                f"{rmte[Creature.rarity]} {metaRace['name']} (ID: {Creature.id})",
                value=str(Creature.id),
                )
            )
    return db_list


async def get_monster_race_list(ctx: discord.AutocompleteContext):
    try:
        db_list = []
        for race in sorted(metaNames['race'], key=itemgetter('name')):
            if race['_id'] > 10:
                db_list.append(discord.OptionChoice(race['name'], value=race['_id']))
    except Exception as e:
        logger.error(f'metaNames Query KO [{e}]')
        return None
    else:
        return db_list


async def get_rarity_item_list(ctx: discord.AutocompleteContext):

    db_list = []
    for k, v in rite.items():
        db_list.append(discord.OptionChoice(f"{v} {k}", value=k))
    return db_list


async def get_rarity_monsters_list(ctx: discord.AutocompleteContext):

    db_list = []
    for k, v in rmte.items():
        db_list.append(discord.OptionChoice(f"{v} {k}", value=k))
    return db_list


async def get_singouins_in_instance_list(ctx: discord.AutocompleteContext):
    try:
        query = (Q(instance=ctx.options['instance_uuid']) & Q(account__exists=True))
        Creatures = CreatureDocument.objects(query)
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
        return None

    db_list = []
    for Creature in Creatures:
        db_list.append(
            discord.OptionChoice(
                f"{rmte[Creature.rarity]} {Creature.name} (ID: {Creature.id})",
                value=str(Creature.id),
                )
            )
    return db_list


async def get_singouins_list(ctx: discord.AutocompleteContext):
    try:
        query = Q(race__gt=1) & Q(race__lt=4)
        Creatures = CreatureDocument.objects(query)
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
        return None

    db_list = []
    for Creature in Creatures:
        db_list.append(
            discord.OptionChoice(
                f"{rmte[Creature.rarity]} {Creature.name} (ID: {Creature.id})",
                value=str(Creature.id),
                )
            )
    return db_list


async def get_singouin_inventory_item_list(ctx: discord.AutocompleteContext):
    try:
        Items = ItemDocument.objects(bearer=ctx.options['singouin_uuid'])
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
    else:
        db_list = []
        for Item in Items:
            # FAT ugly query to check if an item from inventory is in Creature.slots
            query = Q(slots__feet__id=Item.id) | \
                    Q(slots__hands__id=Item.id) | \
                    Q(slots__head__id=Item.id) | \
                    Q(slots__holster__id=Item.id) | \
                    Q(slots__lefthand__id=Item.id) | \
                    Q(slots__legs__id=Item.id) | \
                    Q(slots__righthand__id=Item.id) | \
                    Q(slots__shoulders__id=Item.id) | \
                    Q(slots__torso__id=Item.id)
            if CreatureDocument.objects(query):
                # The item is equipped by someone, we don't add it in the dropdown
                logger.trace(f"Item({Item.id}) equipped, we skip it")
                continue

            name = metaIndexed[Item.metatype][Item.metaid]['name']
            db_list.append(discord.OptionChoice(f"{rite[Item.rarity]} {name}", value=str(Item.id)))
    return db_list
