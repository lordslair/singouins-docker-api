# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from mongo.models.Creature import CreatureDocument

from nosql.connector import r

from subcommands.godmode._autocomplete import (
    get_instances_list,
    get_singouins_in_instance_list,
    )


def reset(group_godmode):
    @group_godmode.command(
        description='[@Team role] Reset Action Points for a Singouin',
        default_permission=False,
        name='reset',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "instanceuuid",
        description="Instance UUID",
        autocomplete=get_instances_list
        )
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_singouins_in_instance_list
        )
    async def reset(
        ctx,
        instanceuuid: str,
        singouinuuid: str,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_godmode} reset {instanceuuid} {singouinuuid}')

        try:
            Creature = CreatureDocument.objects(_id=singouinuuid).get()

            if r.exists(f'pa:{Creature.id}:blue'):
                r.delete(f'pa:{Creature.id}:blue')
            if r.exists(f'pa:{Creature.id}:red'):
                r.delete(f'pa:{Creature.id}:red')
        except Exception as e:
            description = f'Godmode-Reset Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return
        else:
            msg = 'Godmode-Reset OK'
            logger.trace(msg)
            embed = discord.Embed(
                title=f"**{Creature.name}**",
                description=msg,
                colour=discord.Colour.green()
                )
            embed.set_footer(text=f"CreatureUUID: {Creature.id}")

            await ctx.respond(embed=embed)
            logger.info(f'{h} └──> Godmode-Reset Query OK')
