# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option
from discord.ext import commands

from subcommands.infra.__k8stools import k8s_backup_logs


def backup(group_admin):
    @group_admin.command(
        description='[@Team role] Display backup information',
        default_permission=False,
        name='backup',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "env",
        description="Target environment",
        choices=['dev', 'prod'],
        )
    @option(
        "action",
        description="Action to execute",
        choices=['status'],
        )
    async def backup(
        ctx,
        env: str,
        action: str,
    ):
        await ctx.defer()  # To defer answer (default: 15min)
        logger.info(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'/{group_admin} backup {env}'
            )

        try:
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> K8s Query Starting'
                )
            if action == 'status':
                exec_stdout = k8s_backup_logs(env)
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
                title=f'K8s backup status [{env}]',
                description=f'```{exec_stdout}```',
                colour=discord.Colour.green()
                )
            await ctx.interaction.edit_original_response(embed=embed)

        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'└──> K8s Query OK'
            )
        return
