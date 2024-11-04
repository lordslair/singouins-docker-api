# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from mongo.models.Creature import CreatureDocument

from subcommands.singouin._autocomplete import get_mysingouins_list
from subcommands.singouin._tools import creature_sprite

from utils.redis import get_pa


def pa(group_singouin):
    @group_singouin.command(
        description=(
            '[@Singouins role] '
            'Display your Singouin Action Points (PA)'
            ),
        default_permission=False,
        name='pa',
        )
    @commands.has_any_role('Singouins')
    @option(
        "singouinuuid",
        description="Singouin ID",
        autocomplete=get_mysingouins_list
        )
    async def pa(
        ctx,
        singouinuuid: str,
    ):
        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_singouin} pa {singouinuuid}')

        file = None

        try:
            Creature = CreatureDocument.objects(_id=singouinuuid).get()
            PA = get_pa(creatureuuid=singouinuuid)

            embed = discord.Embed(
                title=Creature.name,
                colour=discord.Colour.blue()
            )

            redbar    = PA['red']['pa'] * ':red_square:'
            redbar   += (16 - PA['red']['pa']) * ':white_large_square:'
            bluebar   = PA['blue']['pa'] * ':blue_square:'
            bluebar  += (8 - PA['blue']['pa']) * ':white_large_square:'

            embed.add_field(
                name='PA Count:',
                value=(
                    f"> {redbar} ({PA['red']['pa']}/16)\n"
                    f"> :clock1: : {PA['red']['ttnpa']}s \n"
                    f"▬▬\n"
                    f"> {bluebar} ({PA['blue']['pa']}/8)\n"
                    f"> :clock1: : {PA['blue']['ttnpa']}s"
                    ),
                inline=False,
                )

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(Creature):
                file = discord.File(f'/tmp/{Creature.id}.png', filename=f'{Creature.id}.png')
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')
            logger.info(f'{h} ├──> Singouin-PA Query OK')
        except Exception as e:
            description = f'Singouin-PA Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return
        else:
            try:
                await ctx.respond(embed=embed, ephemeral=True, file=file)
                logger.info(f'{h} └──> Answer send OK')
            except Exception as e:
                logger.info(f'{h} └──> Answer send KO [{e}]')
