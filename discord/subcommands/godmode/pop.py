# -*- coding: utf8 -*-

import discord
import json

from discord.commands import option
from discord.ext import commands
from loguru import logger
from random import randint

from nosql.metas import metaNames
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats import RedisStats
from nosql.publish import publish

from subcommands.godmode._autocomplete import (
    get_instances_list,
    get_monster_race_list,
    get_rarity_monsters_list
    )

from variables import (
    PCS_URL,
    rarity_monster_types_discord,
    )


def pop(group_godmode):
    @group_godmode.command(
        description='[@Team role] Spawn a Monster',
        default_permission=False,
        name='pop',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "monster",
        description="Monster Race",
        autocomplete=get_monster_race_list
        )
    @option(
        "instanceuuid",
        description="Instance UUID",
        autocomplete=get_instances_list
        )
    @option(
        "rarity",
        description="Monster Rarity",
        autocomplete=get_rarity_monsters_list,
        )
    @option(
        "posx",
        description="Position X",
        default=randint(2, 4),
        )
    @option(
        "posy",
        description="Position Y",
        default=randint(2, 5),
        )
    async def pop(
        ctx,
        monster: int,
        instanceuuid: str,
        rarity: str,
        posx: int,
        posy: int,
    ):
        name    = ctx.author.name
        channel = ctx.channel.name
        # As we need roles, it CANNOT be used in PrivateMessage
        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_godmode} pop {monster} {instanceuuid}'
            )

        # We create first the Creature (It will be a monster)
        try:
            Creature = RedisCreature().new(
                name=metaNames['race'][monster]['name'],
                raceid=monster,
                gender=True,
                accountuuid=None,
                rarity=rarity,
                x=posx,
                y=posy,
                instanceuuid=instanceuuid,
                )
            Stats = RedisStats().new(Creature=Creature, classid=None)
            # We put the info in pubsub channel for IA to populate the instance
            try:
                pmsg = {
                    "action": 'pop',
                    "instance": None,
                    "creature": Creature.as_dict(),
                    "stats": Stats.as_dict(),
                    }
                publish('ai-creature', json.dumps(pmsg))
            except Exception as e:
                msg = f'Publish(ai-creature) KO [{e}]'
                logger.error(msg)
        except Exception as e:
            description = f'Godmode-Pop Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return
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

            await ctx.respond(embed=embed)
            logger.info(f'[#{channel}][{name}] └──> Godmode-Pop Query OK')
