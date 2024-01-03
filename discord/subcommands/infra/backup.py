# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option
from discord.ext import commands
from kubernetes import config, client
from kubernetes.stream import stream


def backup(group_admin):
    @group_admin.command(
        description='[@Team role] Display backup information',
        default_permission=False,
        name='backup',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "namespace",
        description="Target environment",
        autocomplete=discord.utils.basic_autocomplete(
            [
                discord.OptionChoice("singouins-dev", value='singouins-dev'),
                discord.OptionChoice("singouins", value='singouins'),
                ]
            )
        )
    @option(
        "action",
        description="Action to execute",
        choices=['status'],
        )
    async def backup(
        ctx,
        namespace: str,
        action: str,
    ):
        # Header for later use
        h = f'[#{ctx.channel.name}][{ctx.channel.name}]'

        await ctx.defer()  # To defer answer (default: 15min)
        logger.info(f'{h} /{group_admin} backup {namespace} {action}')

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

        try:
            logger.info(f'{h} ├──> K8s Query Starting')
            pod = client.CoreV1Api().list_namespaced_pod(
                namespace,
                label_selector="name=backup"
                )

            exec_stdout = stream(
                client.CoreV1Api().connect_get_namespaced_pod_exec,
                pod.items[0].metadata.name,
                namespace,
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
            # We got the logs, we can start working
            embed = discord.Embed(
                title=f'K8s backup status [{namespace}]',
                description=f'```{exec_stdout}```',
                colour=discord.Colour.green()
                )
            await ctx.interaction.edit_original_response(embed=embed)

        logger.info(f'{h} └──> K8s Query OK')
        return
