# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option
from email_validator import validate_email, EmailNotValidError

from nosql.models.RedisSearch import RedisSearch


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
        if ctx.channel.type is not discord.ChannelType.private:
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

        # OK, we are in DM, we can work
        logger.info(
                f'[#{ctx.channel.type}][{ctx.author.name}] '
                f'/{group_user} link <{mail}>'
                )
        try:
            discordname = f'{ctx.author.name}#{ctx.author.discriminator}'
            try:
                validate_email(mail)
            except EmailNotValidError as e:
                await ctx.respond(
                    embed=discord.Embed(
                        description=f'Registration KO: Mail NotValid\n[{e}]',
                        colour=discord.Colour.red(),
                        )
                    )
                return

            Users = RedisSearch().user(
                query=f'@d_name:{discordname}'
                )
            if len(Users.results) == 0:
                msg = f'No User with mail:`{mail}` in DB'
                logger.trace(msg)
                await ctx.respond(
                    embed=discord.Embed(
                        description=msg,
                        colour=discord.Colour.orange(),
                        )
                    )
                return
            else:
                User = Users.results[0]

            try:
                User.d_name = discordname
                User.d_ack = True
            except Exception as e:
                msg = f'User Link KO [{e}]'
                logger.trace(msg)
                await ctx.respond(
                    embed=discord.Embed(
                        description=msg,
                        colour=discord.Colour.red(),
                        )
                    )
                return
        except Exception as e:
            logger.error(
                f'[#{ctx.channel.type}][{ctx.author.name}] '
                f'└──> Embed KO [{e}]'
                )
        else:
            logger.info(
                f'[#{ctx.channel.type}][{ctx.author.name}] '
                f'├──> Query OK'
                )
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.green(),
                    )
                )
            return
            logger.info(
                f'[#{ctx.channel.type}][{ctx.author.name}] '
                f'└──> Answer sent'
                )
