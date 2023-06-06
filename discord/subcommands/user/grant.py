# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.ext import commands

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisUser import RedisUser


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

        discordname = f'{ctx.author.name}#{ctx.author.discriminator}'
        Users = RedisUser().search(query=f'@d_name:{discordname}')

        if len(Users) == 0:
            # Discord name not found in DB
            msg = f'Unknown Discord Name:`{discordname}` in DB'
            logger.trace(msg)
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.orange()
            )
            return embed
        else:
            User = Users[0]

        # Fetch the Discord role
        try:
            singouinrole = discord.utils.get(
                ctx.author.guild.roles,
                name='Singouins'
                )
        except Exception as e:
            embed = discord.Embed(
                description=f'User Singouins get-role:Singouins failed\n[{e}]',
                colour=discord.Colour.red()
            )
            return embed

        # Check role existence
        if singouinrole not in ctx.author.roles:
            # Apply role on user
            try:
                await ctx.author.add_roles(singouinrole)
            except Exception as e:
                embed = discord.Embed(
                    description=(
                        f'User Singouins add-role:Singouins failed\n'
                        f'[{e}]'
                        ),
                    colour=discord.Colour.red()
                )
                return embed

        # Apply Squad roles if needed
        guild = ctx.guild
        account = User['id'].replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@account:{account}')

        if len(Creatures) == 0:
            # Discord found - but no Singouins in DB
            # So we can stop here
            msg = f'Unknown Discord Name:`{discordname}` in DB'
            logger.trace(msg)
            embed = discord.Embed(
                description="User Singouins grant successed",
                colour=discord.Colour.green()
            )
            return embed

        for Creature in Creatures:
            # Korp management
            if Creature['korp']:
                # Add the korp role to the user
                try:
                    korprole = discord.utils.get(
                        guild.roles,
                        name=f"Korp-{Creature['korp']}"
                        )
                except Exception as e:
                    embed = discord.Embed(
                        description=(
                            f"User Singouins "
                            f"get-role:Korp-{Creature['korp']} "
                            f"failed\n[{e}]"
                            ),
                        colour=discord.Colour.red()
                    )
                    return embed
                else:
                    if korprole not in ctx.author.roles:
                        try:
                            await ctx.author.add_roles(korprole)
                        except Exception as e:
                            embed = discord.Embed(
                                description=(
                                    f"User Singouins "
                                    f"add-role:Korp-{Creature['korp']} "
                                    f"failed\n[{e}]"
                                    ),
                                colour=discord.Colour.red()
                            )
                            return embed

            # Squad management
            if Creature['squad']:
                # Add the korp role to the user
                try:
                    squadrole = discord.utils.get(
                        guild.roles,
                        name=f"Squad-{Creature['squad']}"
                        )
                except Exception as e:
                    embed = discord.Embed(
                        description=(
                            f"User Singouins "
                            f"get-role:Squad-{Creature['squad']} "
                            f"failed\n[{e}]"
                            ),
                        colour=discord.Colour.red()
                    )
                    return embed
                else:
                    if squadrole not in ctx.author.roles:
                        try:
                            await ctx.author.add_roles(squadrole)
                        except Exception as e:
                            embed = discord.Embed(
                                description=(
                                    f"User Singouins "
                                    f"add-role:Squad-{Creature['squad']} "
                                    f"failed\n[{e}]"
                                    ),
                                colour=discord.Colour.red()
                            )
                            return embed

            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> Query OK'
                )
            await ctx.respond(
                embed=discord.Embed(
                    description="User Singouins & Squad/Korp grant successed",
                    colour=discord.Colour.green()
                    )
                )
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'└──> Answer sent'
                )
