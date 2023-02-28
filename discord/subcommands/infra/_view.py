# -*- coding: utf8 -*-

import discord

from discord.ui         import View
from kubernetes         import client
from loguru             import logger

from .__k8stools        import load_config


class killView(View):

    def __init__(self, ctx, env, podname):
        super().__init__(timeout=10)
        self.ctx     = ctx
        self.env     = env
        self.podname = podname

    @discord.ui.button(label='Kill it with fire!',
                       style=discord.ButtonStyle.green,
                       emoji="✅")
    async def ok_button_callback(self, button, interaction):
        # K8s conf loading
        ret = load_config(self.env)
        if ret['success']:
            namespace = ret['namespace']
        else:
            return ret['embed']
        try:
            # We try to kill the found pod
            client.CoreV1Api().delete_namespaced_pod(self.podname, namespace)
        except Exception as e:
            logger.warning(f'K8s Kill KO ({namespace}:{self.podname}) [{e}]')
            return None
        else:
            logger.info(f'K8s Kill OK ({namespace}:{self.podname})')
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=f'K8s Kill OK ({namespace}:`{self.podname}`)',
                    colour=discord.Colour.green()
                    ),
                view=None,
                )

    @discord.ui.button(label='Abord mission!',
                       style=discord.ButtonStyle.danger,
                       emoji="❌")
    async def ko_button_callback(self, button, interaction):
        msg = f'K8s POD `{self.podname}` kill KO - Cancelled'
        logger.info(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        await interaction.response.edit_message(embed=embed,
                                                view=None)

    async def on_timeout(self):
        msg = f'K8s POD `{self.podname}` kill KO - Timeout'
        logger.info(msg)

    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            embed = discord.Embed(
                description='Sorry, only @Team members can click on that!',
                colour=discord.Colour.orange()
            )
            await interaction.response.send_message(embed=embed,
                                                    view=None,
                                                    ephemeral=True)
            return False
        else:
            return True
