# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.ext import commands

from subcommands.grant._embeds import embed_user_grant


def grant(group_user, bot):
    @group_user.command(
        description='[@everyone] Update your Discord roles (Squad/Korp)',
        default_permission=False,
        name='grant',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    async def grant(
        ctx,
    ):
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'/{group_user} grant'
            )

        embed = await embed_user_grant(bot, ctx)
        if embed:
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> Query OK'
                )
            await ctx.respond(embed=embed)
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'└──> Answer sent'
                )
        else:
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'└──> Query KO'
                )
            embed = discord.Embed(
                description='User Singouins grant KO',
                colour=discord.Colour.red()
            )
            await ctx.respond(embed=embed)
            return
