# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option

from subcommands.grant._embeds import embed_user_link


def link(group_user, bot):
    @group_user.command(
        description='[@everyone] Link your Singouin with Discord',
        name='link',
        )
    @option(
        "mail",
        description="User mail adress (The one used in the game)",
        )
    async def link(
        ctx,
        mail: str,
    ):
        # Pre-flight checks
        if ctx.channel.type is discord.ChannelType.private:
            logger.info(
                f'[#{ctx.channel.type}][{ctx.author.name}] '
                f'/{group_user} link <{mail}>'
                )
            # We are in a private DMChannel
            try:
                embed = embed_user_link(bot, ctx, mail)
            except Exception as e:
                logger.error(
                    f'[#{ctx.channel.type}][{ctx.author.name}] '
                    f'└──> Embed KO [{e}]'
                    )
            else:
                if embed:
                    logger.info(
                        f'[#{ctx.channel.type}][{ctx.author.name}] '
                        f'├──> Query OK'
                        )
                    await ctx.respond(embed=embed)
                    logger.info(
                        f'[#{ctx.channel.type}][{ctx.author.name}] '
                        f'└──> Answer sent'
                        )
                else:
                    logger.info(
                        f'[#{ctx.channel.type}][{ctx.author.name}] '
                        f'└──> Query KO'
                        )
                    embed = discord.Embed(
                        description='User Singouins register KO',
                        colour=discord.Colour.red()
                    )
                    await ctx.respond(embed=embed)
                    return
        else:
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'/{group_user} link <{mail}>'
                )
            try:
                embed = discord.Embed(
                    description=(
                        f':information_source: You tried to register '
                        f'your account here on the channel '
                        f'`#{ctx.channel.name}`\n'
                        f'---\n'
                        f'Go to {bot.user.mention} Private Messages to avoid '
                        f'showing publicly your email & retry the command.\n'
                        f'The bot should have sent you a PM right now\n'
                        f'---\n'
                        f'This message will be discarded automatically\n'
                    ),
                    colour=discord.Colour.red()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                embed = discord.Embed(
                    description=(
                        f':information_source: You tried to register '
                        f'your account on the channel `#{ctx.channel.name}`\n'
                        f'---\n'
                        f'But it will be better to do that here :smiley: \n'
                        f'---\n'
                        f'You can safely use the command `/user link` here\n'
                    ),
                    colour=discord.Colour.green()
                )
                await ctx.author.send(embed=embed)
            except Exception as e:
                await ctx.respond(f'[{e}]')
            else:
                return
