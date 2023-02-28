# -*- coding: utf8 -*-

import discord
import re

from discord.commands import option
from discord.ext import commands
from kubernetes import client
from loguru import logger

from subcommands.infra._autocomplete import get_k8s_pod_list
from subcommands.infra.__k8stools import load_config


def log(group_admin):
    @group_admin.command(
        description='[@Team role] Display POD logs',
        default_permission=False,
        name='log',
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
    async def log(
        ctx,
        env: str,
        pod: str,
    ):
        await ctx.defer()  # To defer answer (default: 15min)
        logger.info(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'/{group_admin} log {env} {pod}'
            )

        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> K8s Query Starting'
            )

        # K8s conf loading
        ret = load_config(env)
        if ret['success']:
            namespace = ret['namespace']
        else:
            await ctx.respond(embed=ret['embed'], ephemeral=True)
            return

        try:
            log = client.CoreV1Api().read_namespaced_pod_log(
                name=pod,
                since_seconds=1728000,
                namespace=namespace,
                )
        except Exception as e:
            logger.error(
                f'[#{ctx.channel.name}][{ctx.channel.name}] '
                f'└──> K8s Query KO [{e}]'
                )

            await ctx.respond(
                embed=discord.Embed(
                    description='Command aborted: K8s Query KO',
                    colour=discord.Colour.red()
                    ),
                )
            return

        if log != '':
            # We do this to filter out ANSI sequences (ex: colors)
            reaesc = re.compile(r'\x1b[^m]*m')
            log_purged = reaesc.sub('', log)

            # We do this to have the latest lines, not the first
            lines_first_to_last = []
            content_length = 0  # to count the final message length
            for line in reversed(log_purged.splitlines()):
                if content_length + len(line) < 2000:
                    if 'WARN' in line.upper():
                        newline = f'🟧 {line}\n'
                    elif 'ERROR' in line.upper():
                        newline = f'🟥 {line}\n'
                    elif 'INFO' in line.upper():
                        newline = f'🟩 {line}\n'
                    elif 'DEBUG' in line.upper():
                        newline = f'🟦 {line}\n'
                    elif 'TRACE' in line.upper():
                        newline = f'🟦 {line}\n'
                    else:
                        newline = f'⬜ {line}\n'

                    content_length += len(newline)
                    lines_first_to_last.append(newline)
                else:
                    break

            content = ''
            for line in reversed(lines_first_to_last):
                content += line
                await ctx.interaction.edit_original_response(
                    content=f'```{content}```',
                    )
        else:
            await ctx.respond(
                embed=discord.Embed(
                    title=f'[{env}] `{pod}` ',
                    description='No logs available',
                    colour=discord.Colour.green()
                    ),
                )

        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'└──> K8s Query OK'
            )
        return
