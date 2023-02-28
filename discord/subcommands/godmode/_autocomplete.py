# -*- coding: utf8 -*-

import discord

from loguru import logger
from operator import itemgetter

from nosql.metas import (
    metaArmors,
    metaNames,
    metaRaces,
    metaWeapons,
    )
from nosql.models.RedisSearch import RedisSearch

from utils.variables import (
    rarity_item_types_emoji,
    rarity_monster_types_emoji,
    )


async def get_instances_list(ctx: discord.AutocompleteContext):
    try:
        Instances = RedisSearch().instance(query='-(@map:None)')
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None
    else:
        db_list = []
        for Instance in Instances.results:
            db_list.append(
                discord.OptionChoice(
                    f"{Instance.id} (map:{Instance.map})",
                    value=f"{Instance.id}",
                    )
                )
        return db_list


async def get_metanames_list(ctx: discord.AutocompleteContext):
    try:
        db_list = []
        if ctx.options["metatype"] == 'weapon':
            metas = metaWeapons
        elif ctx.options["metatype"] == 'armor':
            metas = metaArmors

        for meta in sorted(metas, key=itemgetter('name')):
            db_list.append(
                discord.OptionChoice(meta['name'], value=f"{meta['id']}")
                )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None
    else:
        return db_list


async def get_monsters_in_instance_list(ctx: discord.AutocompleteContext):
    try:
        Creatures = RedisSearch().creature(
            query=f"@instance:{ctx.options['instanceuuid']}"
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None

    db_list = []
    for Creature in Creatures.results:
        if Creature.account is None:
            db_list.append(
                discord.OptionChoice(
                    f"{rarity_monster_types_emoji[Creature.rarity]} "
                    f"{metaNames['race'][Creature.race]['name']} "
                    f"(ID: {Creature.id})",
                    value=Creature.id,
                    )
                )
    return db_list


async def get_monster_race_list(ctx: discord.AutocompleteContext):
    try:
        db_list = []
        for race in sorted(metaRaces, key=itemgetter('name')):
            if race['id'] > 10:
                db_list.append(
                    discord.OptionChoice(
                        race['name'],
                        value=f"{race['id']}",
                        )
                    )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None
    else:
        return db_list


async def get_rarity_item_list(ctx: discord.AutocompleteContext):

    db_list = []
    for k, v in rarity_item_types_emoji.items():
        db_list.append(
            discord.OptionChoice(
                f"{v} {k}",
                value=k,
                )
            )
    return db_list


async def get_rarity_monsters_list(ctx: discord.AutocompleteContext):

    db_list = []
    for k, v in rarity_monster_types_emoji.items():
        db_list.append(
            discord.OptionChoice(
                f"{v} {k}",
                value=k,
                )
            )
    return db_list


async def get_singouins_in_instance_list(ctx: discord.AutocompleteContext):
    try:
        Creatures = RedisSearch().creature(
            query=f"@instance:{ctx.options['instanceuuid']}"
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None

    db_list = []
    for Creature in Creatures.results:
        if Creature.race in [1, 2, 3, 4]:
            db_list.append(
                discord.OptionChoice(
                    f"{rarity_monster_types_emoji[Creature.rarity]} "
                    f"{Creature.name} "
                    f"(ID: {Creature.id})",
                    value=Creature.id,
                    )
                )
    return db_list


async def get_singouin_inventory_item_list(ctx: discord.AutocompleteContext):
    try:
        bearer = ctx.options['singouinuuid'].replace('-', ' ')
        Items = RedisSearch().item(
            query=f'@bearer:{bearer}',
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        for Item in Items.results:
            if Item.metatype == 'weapon':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == Item.metaid,
                            metaWeapons
                            )
                        )[0]
                    )  # Gruikfix
            elif Item.metatype == 'armor':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == Item.metaid,
                            metaArmors
                            )
                        )[0]
                    )  # Gruikfix
            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[Item.rarity]} "
                     f"{meta['name']}"),
                    value=f"{Item.id}"
                    )
                )
    return db_list
