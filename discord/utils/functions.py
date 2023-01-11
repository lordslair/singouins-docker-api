# -*- coding: utf8 -*-

import discord

from loguru             import logger
from operator           import itemgetter

from nosql.metas import (
    metaArmors,
    metaNames,
    metaRaces,
    metaWeapons,
    )
from nosql.models.RedisAuction  import RedisAuction
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisInstance import RedisInstance
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisUser     import RedisUser

from utils.variables import (
    rarity_item_types_emoji,
    rarity_monster_types_emoji,
    )

#
# async functions used in autocomplete
#


async def get_auctioned_item_list(ctx: discord.AutocompleteContext):
    try:
        Auctions = RedisAuction().search(
            query=f'@metatype:{ctx.options["metatype"]}'
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        for item in Auctions:
            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[item['rarity']]} "
                     f"{item['metaname']} "
                     f"(Price:{item['price']})"),
                    value=f"{item['id']}"
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


async def get_singouins_list(ctx: discord.AutocompleteContext):
    try:
        DiscordUser = ctx.interaction.user
        discordname = f'{DiscordUser.name}#{DiscordUser.discriminator}'
        Users = RedisUser().search(field='d_name', query=discordname)

        if len(Users) == 0:
            msg = f'No User linked with `{discordname}`'
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.orange()
            )
            return embed
        else:
            User = Users[0]
            account = User['id'].replace('-', ' ')
            Creatures = RedisCreature().search(query=f'@account:{account}')
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None
    else:
        db_list = []
        for creature in Creatures:
            db_list.append(
                discord.OptionChoice(
                    creature['name'],
                    value=creature['id']
                    )
                )
        return db_list


async def get_monsters_in_instance_list(ctx: discord.AutocompleteContext):
    try:
        Creatures = RedisCreature().search(
            query=f"@instance:{ctx.options['instanceuuid']}"
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None

    db_list = []
    for creature in Creatures:
        if creature['account'] is None:
            db_list.append(
                discord.OptionChoice(
                    f"{rarity_monster_types_emoji[creature['rarity']]} "
                    f"{metaNames['race'][creature['race']]['name']} "
                    f"(ID: {creature['id']})",
                    value=creature['id'],
                    )
                )
    return db_list


async def get_singouins_in_instance_list(ctx: discord.AutocompleteContext):
    try:
        Creatures = RedisCreature().search(
            query=f"@instance:{ctx.options['instanceuuid']}"
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None

    db_list = []
    for creature in Creatures:
        if creature['race'] in [1, 2, 3, 4]:
            db_list.append(
                discord.OptionChoice(
                    f"{rarity_monster_types_emoji[creature['rarity']]} "
                    f"{creature['name']} "
                    f"(ID: {creature['id']})",
                    value=creature['id'],
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


async def get_instances_list(ctx: discord.AutocompleteContext):
    try:
        Instances = RedisInstance().search(query='-(@map:None)')
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None
    else:
        db_list = []
        for instance in Instances:
            db_list.append(
                discord.OptionChoice(
                    f"{instance['id']} (map:{instance['map']})",
                    value=f"{instance['id']}",
                    )
                )
        return db_list


async def get_singouin_auctionable_item_list(ctx: discord.AutocompleteContext):
    try:
        bearer = ctx.options['singouinuuid'].replace('-', ' ')
        Items = RedisItem().search(
            field='bearer',
            query=f'{bearer}',
            maxpaging=100,
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        for item in Items:
            if item['bound_type'] != 'BoE':
                next

            if item['metatype'] == 'weapon':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == item['metaid'],
                            metaWeapons
                            )
                        )[0]
                    )  # Gruikfix
            elif item['metatype'] == 'armor':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == item['metaid'],
                            metaArmors
                            )
                        )[0]
                    )  # Gruikfix
            else:
                pass

            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[item['rarity']]} "
                     f"{meta['name']}"),
                    value=f"{item['id']}"
                    )
                )
    return db_list


async def get_singouin_auctioned_item_list(ctx: discord.AutocompleteContext):
    try:
        sellerid = ctx.options["singouinuuid"].replace('-', ' ')
        Auctions = RedisAuction().search(
            query=(
                f"(@metatype:{ctx.options['metatype']}) "
                f"& (@sellerid:{sellerid})"
                )
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        for item in Auctions:
            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[item['rarity']]} "
                     f"{item['metaname']} "
                     f"(Price:{item['price']})"),
                    value=f"{item['id']}"
                    )
                )
        return db_list


async def get_singouin_inventory_item_list(ctx: discord.AutocompleteContext):
    try:
        bearer = ctx.options['singouinuuid'].replace('-', ' ')
        Items = RedisItem().search(
            field='bearer',
            query=f'{bearer}',
            maxpaging=100,
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        for item in Items:
            if item['metatype'] == 'weapon':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == item['metaid'],
                            metaWeapons
                            )
                        )[0]
                    )  # Gruikfix
            elif item['metatype'] == 'armor':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == item['metaid'],
                            metaArmors
                            )
                        )[0]
                    )  # Gruikfix
            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[item['rarity']]} "
                     f"{meta['name']}"),
                    value=f"{item['id']}"
                    )
                )
    return db_list
