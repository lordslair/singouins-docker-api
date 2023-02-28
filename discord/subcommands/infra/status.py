# -*- coding: utf8 -*-

import discord

from loguru import logger
from discord.commands import option
from discord.ext import commands

from subcommands.infra.__k8stools import k8s_status


def status(group_admin):
    @group_admin.command(
        description='[@Team role] Display Infra status',
        default_permission=False,
        name='status',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "env",
        description="Target environment",
        choices=['dev', 'prod'],
        )
    @option(
        "verbose",
        description="--verbose",
        choices=['True', 'False'],
        required=False,
        default='False',
        )
    async def status(
        ctx,
        env: str,
        verbose: str,
    ):
        await ctx.defer()  # To defer answer (default: 15min)
        logger.info(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'/{group_admin} status {env} --verbose={verbose}'
            )

        try:
            logger.info(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> K8s Query Starting'
                )
            pods = k8s_status(env, verbose)
            logger.debug(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'├──> K8s Query Ended'
                )
        except Exception as e:
            logger.error(
                f'[#{ctx.channel.name}][{ctx.author.name}] '
                f'└──> K8sKill View KO [{e}]'
                )
            embed = discord.Embed(
                description='Command aborted: K8s Query KO',
                colour=discord.Colour.red()
                )
            await ctx.respond(embed=embed)
            return

        # We got the pod object, we can start working
        description = ''
        embed = discord.Embed(
            title=f'K8s status [{env}]',
            description=description,
            colour=discord.Colour.green()
            )
        # We Start to update the Embed
        await ctx.interaction.edit_original_response(embed=embed)
        # We loop over pods to have detailed infos
        for pod in pods.items:
            # We skip CronJob generated pods
            if 'job-name' in pod.metadata.labels:
                continue
            # We fetch the POD name and format it
            try:
                if 'name' in pod.metadata.labels:
                    app_name = pod.metadata.labels['name'].title()
                elif 'app' in pod.metadata.labels:
                    app_name = pod.metadata.labels['app'].title()
                else:
                    app_name = None
            except Exception as e:
                logger.error(f'Unable to read POD metadata [{e}]')
                app_name = None

            if verbose == 'True':
                app_status = ''
            else:
                if pod.status.phase == 'Running':
                    app_status = '🟢'
                else:
                    app_status = '🔴'
            description += f"{app_status} {app_name}\n"
            logger.trace(f"{app_status} {app_name}")

            # We fetch the container(s) name and format it
            if verbose == 'True':
                for container in pod.status.container_statuses:
                    container_name = container.name
                    container_name.removeprefix('sep-backend-')
                    if container.ready:
                        container_status = '🟢'
                    else:
                        container_status = '🔴'
                    logger.trace(
                        f"> {container_status} {container_name} "
                        f"({container.restart_count})"
                        )
                    description += (
                        f"> {container_status} {container_name} "
                        f"({container.restart_count})\n"
                        )

            # We update the Embed with the pod result
            embed = discord.Embed(
                title=f'K8s status [{env}]',
                description=description,
                colour=discord.Colour.green()
                )
            await ctx.interaction.edit_original_response(embed=embed)

        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'└──> K8s Query OK'
            )
        return
