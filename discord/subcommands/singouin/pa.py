# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisPa import RedisPa

from subcommands.singouin._autocomplete import get_mysingouins_list
from subcommands.singouin._tools import creature_sprite


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
        name = ctx.author.name
        channel = ctx.channel.name
        file = None

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} pa {singouinuuid}'
            )

        try:
            Creature = RedisCreature(creatureuuid=singouinuuid)
            Pa = RedisPa(creatureuuid=singouinuuid)

            embed = discord.Embed(
                title=Creature.name,
                colour=discord.Colour.blue()
            )

            redbar    = Pa.redpa * ':red_square:'
            redbar   += (16 - Pa.redpa) * ':white_large_square:'
            bluebar   = Pa.bluepa * ':blue_square:'
            bluebar  += (8 - Pa.bluepa) * ':white_large_square:'

            embed.add_field(
                name='PA Count:',
                value=(
                    f"> {redbar} ({Pa.redpa}/16)\n"
                    f"> :clock1: : {Pa.redttnpa}s \n"
                    f"▬▬\n"
                    f"> {bluebar} ({Pa.bluepa}/8)\n"
                    f"> :clock1: : {Pa.bluettnpa}s"
                    ),
                inline=False,
                )

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(race=Creature.race, creatureuuid=Creature.id):
                file = discord.File(
                    f'/tmp/{Creature.id}.png',
                    filename=f'{Creature.id}.png'
                    )
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')
        except Exception as e:
            description = f'Singouin-PA Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return
        else:
            await ctx.respond(embed=embed, ephemeral=True, file=file)
            logger.info(f'[#{channel}][{name}] └──> Singouin-PA Query OK')
