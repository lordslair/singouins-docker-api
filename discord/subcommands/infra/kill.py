# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option
from discord.ext import commands

from subcommands.infra._view import killView
from subcommands.infra._autocomplete import get_k8s_pod_list


def kill(group_admin):
    @group_admin.command(
        description='[@Team role] Kill an Infra POD',
        default_permission=False,
        name='kill',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "env",
        description="Target environment",
        choices=['dev', 'prod'],
        )
    @option(
        "pod",
        description="Pod",
        autocomplete=get_k8s_pod_list
        )
    async def kill(
        ctx,
        env: str,
        pod: str,
    ):
        logger.info(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'/{group_admin} kill {env} {pod}'
            )

        try:
            view = killView(ctx, env, pod)

            embed = discord.Embed(
                title='Aknowledgement required',
                description=f'Do you want to kill `{pod}`',
                colour=discord.Colour.blue()
                )
            await ctx.respond(embed=embed, view=view)
        except Exception as e:
            logger.error(
                f'[#{ctx.channel.name}][{ctx.channel.name}] '
                f'└──> K8sKill View KO [{e}]'
                )
            embed = discord.Embed(
                description='Command aborted: K8s Query KO',
                colour=discord.Colour.red()
                )
            await ctx.respond(embed=embed)
            return
        else:
            logger.info(
                f'[#{ctx.channel.name}][{ctx.channel.name}] '
                f'└──> K8sKill View OK'
                )
            return
