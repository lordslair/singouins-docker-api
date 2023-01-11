# -*- coding: utf8 -*-

import discord
import json
import os

from loguru          import logger

from nosql.metas import (
    metaNames,
    metaWeapons,
    )
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisStats    import RedisStats
from nosql.publish              import publish

from utils.variables    import (
    rarity_item_types_discord,
    rarity_monster_types_discord,
    )

#
# ENV Variables
#

PCS_URL = os.environ.get("SEP_PCS_URL")

#
# Embeds
#


def embed_godmode_spawn(
    bot,
    ctx,
    raceid,
    instanceuuid,
    posx,
    posy,
    rarity,
):
    # We create first the Creature (It will be a monster)
    try:
        Creature = RedisCreature().new(
            metaNames['race'][raceid]['name'],
            raceid,
            True,
            None,
            rarity=rarity,
            x=posx,
            y=posy,
            instanceid=instanceuuid,
            )
        Stats = RedisStats(Creature).new(classid=None)
        # We put the info in pubsub channel for IA to populate the instance
        try:
            pmsg = {
                "action": 'pop',
                "instance": None,
                "creature": Creature._asdict(),
                "stats": Stats._asdict(),
                }
            pchannel = 'ai-creature'
            publish(pchannel, json.dumps(pmsg))
        except Exception as e:
            msg = f'Publish({pchannel}) KO [{e}]'
            logger.error(msg)
    except Exception as e:
        msg = f'Creature creation KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        embed = discord.Embed(
            title="A new creature appears!",
            colour=discord.Colour.green()
            )

        position = f"({Creature.x},{Creature.y})"
        embed_field_name = (
            f"{rarity_monster_types_discord[Creature.rarity]} "
            f"{Creature.name}"
            )
        embed_field_value  = f"> Instance : `{Creature.instance}`\n"
        embed_field_value += f"> Level : `{Creature.level}`\n"
        embed_field_value += f"> Position : `{position}`\n"

        embed.add_field(
            name=f'**{embed_field_name}**',
            value=embed_field_value,
            inline=True,
            )

        embed.set_footer(text=f"CreatureUUID: {Creature.id}")

        embed.set_thumbnail(
            url=(
                f"{PCS_URL}/resources/sprites/creatures"
                f"/{Creature.race}.png"
                )
            )

        return embed


def embed_godmode_kill(bot, ctx, creatureuuid, instanceuuid):
    Creature = RedisCreature().get(creatureuuid)

    # WE WILL KILL HERE ONLY NON PLAYABLE CREATURES FOR SAFETY
    if Creature.account is not None:
        msg = 'You can only kill NPC Creatures'
        logger.warning(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed

    try:
        # It is a NON playable Creature (Monster)
        # We destroy the RedisStats
        RedisStats(Creature).destroy()
        # We destroy the Creature
        RedisCreature().destroy(Creature.id)
        # We put the info in pubsub channel for IA to regulate the instance
        try:
            pmsg = {
                "action": 'kill',
                "instance": Creature.instance,
                "creature": Creature._asdict(),
                }
            pchannel = 'ai-creature'
            publish(pchannel, json.dumps(pmsg))
        except Exception as e:
            msg = f'Publish({pchannel}) KO [{e}]'
            logger.error(msg)
    except Exception as e:
        msg = f'Creature deletion KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        embed = discord.Embed(
            title="A creature slowly dies!",
            colour=discord.Colour.green()
            )

        position = f"({Creature.x},{Creature.y})"
        embed_field_name = (
            f"{rarity_monster_types_discord[Creature.rarity]} "
            f"{Creature.name}"
            )
        embed_field_value  = f"> Instance : `{Creature.instance}`\n"
        embed_field_value += f"> Level : `{Creature.level}`\n"
        embed_field_value += f"> Position : `{position}`\n"

        embed.add_field(
            name=f'**{embed_field_name}**',
            value=embed_field_value,
            inline=True,
            )

        embed.set_footer(text=f"CreatureUUID: {Creature.id}")

        embed.set_thumbnail(
            url=(
                f"{PCS_URL}/resources/sprites/creatures"
                f"/{Creature.race}.png"
                )
            )

        return embed


def embed_godmode_give(
    bot,
    ctx,
    singouinuuid,
    metatype,
    metaid,
    rarity,
):
    Creature = RedisCreature().get(singouinuuid)
    item_caracs = {
        "metatype": metatype,
        "metaid": metaid,
        "bound": True,
        "bound_type": 'BoP',
        "modded": False,
        "mods": None,
        "state": 100,
        "rarity": rarity,
    }

    try:
        Item = RedisItem(Creature).new(item_caracs)
    except Exception as e:
        msg = f'Item give KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        if Item.metatype == 'armor':
            max_ammo = None
        elif Item.metatype == 'weapon':
            meta = dict(
                list(
                    filter(lambda x: x["id"] == Item.metaid, metaWeapons)
                    )[0]
                )  # Gruikfix
            max_ammo = meta['max_ammo']
        else:
            pass

        embed = discord.Embed(
            title="A new item appears!",
            colour=discord.Colour.green()
            )

        embed_field_name = (
            f"{rarity_item_types_discord[Item.rarity]} "
            f"{metaNames[Item.metatype][Item.metaid]['name']}"
            )
        embed_field_value  = f"> Bearer : `{Creature.name}`\n"
        embed_field_value += f"> Bearer : `UUID({Item.bearer})`\n"
        embed_field_value += (
            f"> Bound : `{Item.bound} ({Item.bound_type})`\n"
            )

        if max_ammo is not None:
            embed_field_value += f"> Ammo : `{Item.ammo}/{max_ammo}`\n"

        embed.add_field(
            name=f'**{embed_field_name}**',
            value=embed_field_value,
            inline=True,
            )

        embed.set_footer(text=f"ItemUUID: {Item.id}")

        embed.set_thumbnail(
            url=(
                f"{PCS_URL}/resources/sprites"
                f"/{Item.metatype}s/{Item.metaid}.png"
                )
            )

        return embed


def embed_godmode_reset(bot, ctx, singouinuuid):
    Creature = RedisCreature().get(singouinuuid)
    Pa = RedisPa(Creature)

    try:
        Pa.redpa = 16
        Pa.bluepa = 8
    except Exception as e:
        msg = f'PA reset KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        msg = 'PA reset OK'
        logger.trace(msg)
        embed = discord.Embed(
            title=f"**{Creature.name}**",
            description=msg,
            colour=discord.Colour.green()
        )
        embed.set_footer(text=f"CreatureUUID: {Creature.id}")
        return embed


def embed_godmode_take(bot, ctx, singouinuuid, itemuuid):
    try:
        Creature = RedisCreature().get(singouinuuid)
        Item = RedisItem(Creature).get(itemuuid)
        RedisItem(Creature).destroy(itemuuid)
    except Exception as e:
        msg = f'Item take KO [{e}]'
        logger.error(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.red()
        )
        return embed
    else:
        embed = discord.Embed(
            title="An item slowly vanishes!",
            colour=discord.Colour.green()
            )

        embed_field_name = (
            f"{rarity_item_types_discord[Item.rarity]} "
            f"{metaNames[Item.metatype][Item.metaid]['name']}"
            )
        embed_field_value  = f"> Bearer : `{Creature.name}`\n"
        embed_field_value += f"> Bearer : `UUID({Item.bearer})`\n"

        embed.add_field(
            name=f'**{embed_field_name}**',
            value=embed_field_value,
            inline=True,
            )

        embed.set_footer(text=f"ItemUUID: {Item.id}")

        embed.set_thumbnail(
            url=(
                f"{PCS_URL}/resources/sprites"
                f"/{Item.metatype}s/{Item.metaid}.png"
                )
            )

        return embed
