# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisStats import RedisStats

from subcommands.singouin._autocomplete import get_singouins_list
from subcommands.singouin._tools import creature_sprite


def stats(group_singouin, bot):
    @group_singouin.command(
        description='[@Singouins role] Display your Singouin Stats',
        default_permission=False,
        name='stats',
        )
    @commands.has_any_role('Singouins')
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_singouins_list
        )
    async def stats(
        ctx,
        singouinuuid: str,
    ):
        name = ctx.author.name
        channel = ctx.channel.name
        file = None

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} stats {singouinuuid}'
            )

        try:
            Creature = RedisCreature(creatureuuid=singouinuuid)
            Stats = RedisStats(creatureuuid=singouinuuid)

            embed = discord.Embed(
                title=Creature.name,
                description=(
                    f":heart_decoration: : "
                    f"`{Stats.hp}/{Stats.hpmax} HP`\n"
                    ),
                colour=discord.Colour.blue()
            )

            emojiStats = {
                'b': discord.utils.get(bot.emojis, name='statB'),
                'g': discord.utils.get(bot.emojis, name='statG'),
                'm': discord.utils.get(bot.emojis, name='statM'),
                'p': discord.utils.get(bot.emojis, name='statP'),
                'r': discord.utils.get(bot.emojis, name='statR'),
                'v': discord.utils.get(bot.emojis, name='statV'),
                }

            # We generate base Stats field
            value = ''
            for stat in emojiStats:
                value += f"> {emojiStats[stat]} : `{getattr(Stats, stat)}`\n"
            embed.add_field(name='**Base Stats**', value=value, inline=True)

            # We generate DEF Stats field
            value  = f"> :dash: : `{Stats.dodge}`\n"
            value += f"> :shield: : `{Stats.parry}`\n"
            value += "▬\n"
            value += f"> :shield: : `{Stats.arm_b}` (B/:gun:)\n"
            value += f"> :shield: : `{Stats.arm_p}` (P/:axe:)\n"
            embed.add_field(name='**DEF Stats**', value=value, inline=True)

            # We generate OFF Stats field
            value  = f"> :axe: : `{Stats.capcom}`\n"
            value += f"> :gun: : `{Stats.capsho}`\n"
            embed.add_field(name='**OFF Stats**', value=value, inline=True)

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(race=Creature.race, creatureuuid=Creature.id):
                file = discord.File(
                    f'/tmp/{Creature.id}.png',
                    filename=f'{Creature.id}.png'
                    )
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')
        except Exception as e:
            description = f'Singouin-Stats Query KO [{e}]'
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
            logger.info(f'[#{channel}][{name}] └──> Singouin-Squad Query OK')
            await ctx.respond(embed=embed, ephemeral=True, file=file)
            return
