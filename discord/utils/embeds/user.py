# -*- coding: utf8 -*-

import discord
import os

from email_validator import validate_email, EmailNotValidError
from loguru          import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisUser     import RedisUser

#
# ENV Variables
#

PCS_URL = os.environ.get("SEP_PCS_URL")

#
# Embeds
#


async def embed_user_grant(bot, ctx):
    discordname = f'{ctx.author.name}#{ctx.author.discriminator}'
    Users = RedisUser().search(field='d_name', query=discordname)

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
                description=f'User Singouins add-role:Singouins failed\n[{e}]',
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

        # If we are here, everything went fine
        embed = discord.Embed(
            description="User Singouins & Squad/Korp grant successed",
            colour=discord.Colour.green()
        )
        return embed


def embed_user_link(bot, ctx, mail):
    discordname = f'{ctx.author.name}#{ctx.author.discriminator}'

    try:
        validate_email(mail)
    except EmailNotValidError as e:
        embed = discord.Embed(
            description=f'Registration failed: Weird mail address\n[{e}]',
            colour=discord.Colour.red()
        )
        return embed

    User = RedisUser().get(mail)
    if User is None or User is False:
        msg = f'No User with mail:`{mail}` in DB'
        logger.trace(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed

    try:
        User.d_name = discordname
        User.d_ack = True
    except Exception as e:
        msg = f'User Link KO [{e}]'
        logger.trace(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.green()
        )
        return embed
    else:
        msg = 'User Link OK'
        logger.trace(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.green()
        )
        return embed
