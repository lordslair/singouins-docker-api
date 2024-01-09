# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option
from discord.ext import commands
from kubernetes import config, client
from kubernetes.stream import stream

from subcommands.infra._tools import log_pretty


def backup(group_admin):
    @group_admin.command(
        description='[@Team role] Display backup information',
        default_permission=False,
        name='backup',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "action",
        description="Action to execute",
        choices=['status', 'run'],
        )
    async def backup(
        ctx,
        action: str,
    ):
        # Header for later use
        h = f'[#{ctx.channel.name}][{ctx.channel.name}]'

        NAMESPACE = 'singouins-databases'

        await ctx.defer()  # To defer answer (default: 15min)
        logger.info(f'{h} /{group_admin} backup {action}')

        try:
            config.load_kube_config("/etc/k8s/kubeconfig.yaml")
        except Exception as e:
            msg = f'K8s conf load KO [{e}]'
            logger.error(msg)
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.red()
                )
            await ctx.respond(embed=embed)
            return

        if action == 'run':
            try:
                logger.info(f'{h} ├──> K8s Query Starting')
                pod = client.CoreV1Api().list_namespaced_pod(
                    NAMESPACE,
                    label_selector="name=backup"
                    )

                exec_stdout = stream(
                    client.CoreV1Api().connect_get_namespaced_pod_exec,
                    pod.items[0].metadata.name,
                    NAMESPACE,
                    command="/etc/periodic/hourly/cron-backup-sh",
                    stderr=True, stdin=False,
                    stdout=True, tty=False
                    )
                logger.info(f'{h} ├──> K8s Query Ended')
            except Exception as e:
                msg = f'K8s pod_exec KO [{e}]'
                logger.error(msg)
                embed = discord.Embed(
                    description=msg,
                    colour=discord.Colour.red()
                    )
                await ctx.respond(embed=embed)
                return
            else:
                content = ''
                for line in log_pretty(exec_stdout):
                    content += line
                    await ctx.interaction.edit_original_response(
                        embed=discord.Embed(
                            title=f'K8s backup {action}',
                            description=f'```{content}```',
                            colour=discord.Colour.green()
                            )
                        )
        elif action == 'status':
            try:
                logger.info(f'{h} ├──> K8s Query Starting')
                pod = client.CoreV1Api().list_namespaced_pod(
                    NAMESPACE,
                    label_selector="name=backup"
                    )

                exec_stdout = stream(
                    client.CoreV1Api().connect_get_namespaced_pod_exec,
                    pod.items[0].metadata.name,
                    NAMESPACE,
                    command="/etc/periodic/daily/cron-status-sh",
                    stderr=True, stdin=False,
                    stdout=True, tty=False
                    )
                logger.info(f'{h} ├──> K8s Query Ended')
            except Exception as e:
                msg = f'K8s pod_exec KO [{e}]'
                logger.error(msg)
                embed = discord.Embed(
                    description=msg,
                    colour=discord.Colour.red()
                    )
                await ctx.respond(embed=embed)
                return
            else:
                content = ''
                for line in log_pretty(exec_stdout):
                    content += line
                    await ctx.interaction.edit_original_response(
                        embed=discord.Embed(
                            title=f'K8s backup {action}',
                            description=f'```{content}```',
                            colour=discord.Colour.green()
                            )
                        )

        logger.info(f'{h} └──> K8s Query OK')
        return
