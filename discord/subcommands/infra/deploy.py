# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option
from discord.ext import commands

from subcommands.infra.__k8stools import k8s_deployer


def deploy(group_admin):
    @group_admin.command(
        description='[@Team role] Deploy latest Front build',
        default_permission=False,
        name='deploy',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "env",
        description="Target environment",
        choices=['dev', 'prod'],
        )
    async def deploy(
        ctx,
        env: str,
    ):
        await ctx.defer()  # To defer answer (default: 15min)
        logger.info(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'/{group_admin} deploy {env}'
            )

        try:
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> K8s Query Starting'
                )
            exec_stdout = k8s_deployer(env)
            logger.debug(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> K8s Query Ended'
                )
        except Exception as e:
            logger.error(
                f'[#{ctx.channel.name}][{ctx.channel.name}] '
                f'└──> K8s Query KO [{e}]'
                )
            embed = discord.Embed(
                description='Command aborted: K8s Query KO',
                colour=discord.Colour.red()
            )
            await ctx.respond(embed=embed)
            return
        else:
            # We got the logs, we can start working
            embed = discord.Embed(
                title=f'K8s deploy status [{env}]',
                description=f'```{exec_stdout}```',
                colour=discord.Colour.green()
            )
            await ctx.interaction.edit_original_response(embed=embed)

        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'└──> K8s Query OK'
            )
        return
