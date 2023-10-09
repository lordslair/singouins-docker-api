# -*- coding: utf8 -*-

import discord
import json

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats import RedisStats
from nosql.publish import publish

from subcommands.godmode._autocomplete import (
    get_instances_list,
    get_monsters_in_instance_list
    )

from variables import (
    URL_ASSETS,
    rarity_monster_types_discord,
    )


def depop(group_godmode):
    @group_godmode.command(
        description='[@Team role] Kill a Monster',
        default_permission=False,
        name='depop',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "instanceuuid",
        description="Instance UUID",
        autocomplete=get_instances_list
        )
    @option(
        "creatureuuid",
        description="Creature UUID",
        autocomplete=get_monsters_in_instance_list
        )
    async def depop(
        ctx,
        instanceuuid: str,
        creatureuuid: str,
    ):
        name    = ctx.author.name
        channel = ctx.channel.name
        # As we need roles, it CANNOT be used in PrivateMessage
        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_godmode} depop {instanceuuid} {creatureuuid}'
            )

        Creature = RedisCreature(creatureuuid=creatureuuid)

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
            RedisStats(creatureuuid=Creature.id).destroy()
            # We destroy the Creature
            RedisCreature(creatureuuid=Creature.id).destroy()
            # We put the info in pubsub channel for IA to regulate the instance
            try:
                pmsg = {
                    "action": 'kill',
                    "instance": Creature.instance,
                    "creature": Creature.as_dict(),
                    }
                publish('ai-creature', json.dumps(pmsg))
            except Exception as e:
                logger.error(f'Publish(ai-creature) KO [{e}]')
        except Exception as e:
            description = f'Godmode-Depop Query KO [{e}]'
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

            URI_PNG = f'sprites/creatures/{Creature.race}.png'
            logger.debug(f"[embed.thumbnail] {URL_ASSETS}/{URI_PNG}")
            embed.set_thumbnail(url=f"{URL_ASSETS}/{URI_PNG}")

            await ctx.respond(embed=embed)
            logger.info(f'[#{channel}][{name}] └──> Godmode-Depop Query OK')
