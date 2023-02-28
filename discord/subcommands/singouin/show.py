# -*- coding: utf8 -*-

import discord

from discord.ext import commands
from loguru import logger

from nosql.models.RedisSearch import RedisSearch


def show(group_singouin, bot):
    @group_singouin.command(
        description=(
            '[@Singouins role] '
            'Show your Singouin(s) informations'
            ),
        default_permission=False,
        name='show',
        )
    @commands.has_any_role('Singouins')
    async def show(
        ctx,
    ):
        name         = ctx.author.name
        channel      = ctx.channel.name

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} show'
            )

        try:
            emojiRace = [
                discord.utils.get(bot.emojis, name='raceC'),
                discord.utils.get(bot.emojis, name='raceG'),
                discord.utils.get(bot.emojis, name='raceM'),
                discord.utils.get(bot.emojis, name='raceO'),
                ]

            discordname = f'{ctx.author.name}#{ctx.author.discriminator}'
            Users = RedisSearch().user(f'@d_name:{discordname}')

            if len(Users.results) == 0:
                description = f'No User linked with `{discordname}`'
                logger.error(f'[#{channel}][{name}] └──> {description}')
                await ctx.respond(
                    embed=discord.Embed(
                        description=description,
                        colour=discord.Colour.red(),
                        )
                    )
                return
        except Exception as e:
            description = f'Singouin-List Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return

        try:
            User = Users.results[0]
            Creatures = RedisSearch().creature(
                query=f"@account:{User.id.replace('-', ' ')}"
                )

            mydesc = ''
            for Creature in Creatures.results:
                emojiMyRace = emojiRace[Creature.race - 1]
                mydesc += (
                    f"{emojiMyRace} "
                    f"`{Creature.name}` "
                    f"| Level:{Creature.level}\n"
                    )

            embed = discord.Embed(
                title='Your Singouins:',
                description=mydesc,
                colour=discord.Colour.blue()
            )
        except Exception as e:
            description = f'Singouin-List Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return
        else:
            await ctx.respond(embed=embed)
            logger.info(f'[#{channel}][{name}] └──> Singouin-Korp Query OK')
