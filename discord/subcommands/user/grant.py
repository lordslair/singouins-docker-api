# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.ext import commands

from nosql.models.RedisSearch import RedisSearch


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
        Users = RedisSearch().user(
                query=f'@d_name:{discordname}'
                )

        if len(Users.results) == 0:
            # Discord name not found in DB
            msg = f'Unknown Discord Name:`{discordname}` in DB'
            logger.trace(msg)
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange(),
                    ),
                ephemeral=True,
                )
            return
        else:
            User = Users.results[0]

        # Fetch the Discord role
        try:
            singouinrole = discord.utils.get(
                ctx.author.guild.roles,
                name='Singouins'
                )
        except Exception as e:
            await ctx.respond(
                embed=discord.Embed(
                    description=(
                        f'User Singouins get-role:Singouins failed\n'
                        f'[{e}]'
                        ),
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return

        # Check role existence
        if singouinrole not in ctx.author.roles:
            # Apply role on user
            try:
                await ctx.author.add_roles(singouinrole)
            except Exception as e:
                await ctx.respond(
                    embed=discord.Embed(
                        description=(
                            f'User Singouins add-role:Singouins failed\n'
                            f'[{e}]'
                            ),
                        colour=discord.Colour.red(),
                        ),
                    ephemeral=True,
                    )
                return

        # Apply Squad roles if needed
        guild = ctx.guild
        Creatures = RedisSearch().creature(
                query=f"@account:{User.id.replace('-', ' ')}"
                )

        if len(Creatures.results) == 0:
            # Discord found - but no Singouins in DB
            # So we can stop here
            msg = f'No Singouins found in DB for `{discordname}`'
            logger.trace(msg)
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange(),
                    ),
                ephemeral=True,
                )
            return

        for Creature in Creatures.results:
            # Korp management
            if Creature.korp:
                # Add the korp role to the user
                try:
                    korprole = discord.utils.get(
                        guild.roles,
                        name=f"Korp-{Creature.korp}"
                        )
                except Exception as e:
                    await ctx.respond(
                        embed=discord.Embed(
                            description=(
                                f"User Singouins "
                                f"get-role:Korp-{Creature.korp} "
                                f"failed\n[{e}]"
                                ),
                            colour=discord.Colour.red(),
                            ),
                        ephemeral=True,
                        )
                    return
                else:
                    if korprole not in ctx.author.roles:
                        try:
                            await ctx.author.add_roles(korprole)
                        except Exception as e:
                            await ctx.respond(
                                embed=discord.Embed(
                                    description=(
                                        f"User Singouins "
                                        f"add-role:Korp-{Creature.korp} "
                                        f"failed\n[{e}]"
                                        ),
                                    colour=discord.Colour.red(),
                                    ),
                                ephemeral=True,
                                )
                            return

            # Squad management
            if Creature.squad:
                # Add the korp role to the user
                try:
                    squadrole = discord.utils.get(
                        guild.roles,
                        name=f"Squad-{Creature.squad}"
                        )
                except Exception as e:
                    await ctx.respond(
                        embed=discord.Embed(
                            description=(
                                f"User Singouins "
                                f"get-role:Squad-{Creature.squad} "
                                f"failed\n[{e}]"
                                ),
                            colour=discord.Colour.red(),
                            ),
                        ephemeral=True,
                        )
                    return
                else:
                    if squadrole not in ctx.author.roles:
                        try:
                            await ctx.author.add_roles(squadrole)
                        except Exception as e:
                            await ctx.respond(
                                embed=discord.Embed(
                                    description=(
                                        f"User Singouins "
                                        f"add-role:Squad-{Creature.squad} "
                                        f"failed\n[{e}]"
                                        ),
                                    colour=discord.Colour.red(),
                                    ),
                                ephemeral=True,
                                )
                            return

            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> Query OK'
                )
            await ctx.respond(
                embed=discord.Embed(
                    description="User Singouins & Squad/Korp grant :ok:",
                    colour=discord.Colour.green()
                    )
                )
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'└──> Answer sent'
                )
