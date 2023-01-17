# -*- coding: utf8 -*-

import discord

from discord.ui         import View
from loguru             import logger

from nosql.models.RedisAuction  import RedisAuction
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisWallet   import RedisWallet

from utils.k8s          import (
    k8s_kill_pod,
    )
from utils.variables    import (
    rarity_item_types_discord,
    )


# Class definitions
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
        try:
            success = k8s_kill_pod(self.env, self.podname)
        except Exception as e:
            logger.info(f'K8s Kill KO [{e}]')
        else:
            if success:
                msg = f'K8s POD `{self.podname}` kill OK'
                logger.info(msg)
                embed = discord.Embed(
                    description=msg,
                    colour=discord.Colour.green()
                )
                await interaction.response.edit_message(embed=embed,
                                                        view=None)
            else:
                msg = f'K8s POD `{self.podname}` kill KO - Failed'
                logger.info(msg)
                embed = discord.Embed(
                    description=msg,
                    colour=discord.Colour.red()
                )
                await interaction.response.edit_message(embed=embed,
                                                        view=None)

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


class buyView(View):
    def __init__(self, ctx, singouinuuid, itemuuid):
        super().__init__(timeout=10)
        self.ctx          = ctx
        self.singouinuuid = singouinuuid
        self.itemuuid     = itemuuid

    @discord.ui.button(
        label='Oh yeah, buy this item!',
        style=discord.ButtonStyle.green,
        emoji="✅",
        )
    async def ok_button_callback(self, button, interaction):
        try:
            Auction = RedisAuction().get(self.itemuuid)
            CreatureSeller = RedisCreature(creatureuuid=Auction.sellerid)
            CreatureBuyer = RedisCreature(creatureuuid=self.singouinuuid)
            Item = RedisItem(CreatureSeller).get(self.itemuuid)

            WalletBuyer = RedisWallet(CreatureBuyer)
            WalletSeller = RedisWallet(CreatureSeller)
        except Exception as e:
            msg = f'Auction Query KO [{e}]'
            logger.error(msg)
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            if Auction is None or Item is None:
                msg = 'Item Auction KO - Item NotFound'
                logger.warning(msg)
                embed = discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                )
                await interaction.response.edit_message(embed=embed, view=None)

        # A couple of checks first
        if CreatureBuyer.race in [1, 2, 3, 4]:
            # Creature is a Singouin, we use bananas
            if WalletBuyer.bananas < Auction.price:
                # Not enough currency to buy
                msg = 'Not enough money to buy this!'
                logger.trace(msg)
                embed = discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return
        elif CreatureBuyer.race in [5, 6, 7, 8]:
            # Creature is a Pourchon, we use sausages
            if WalletBuyer.sausages < Auction.price:
                # Not enough currency to buy
                msg = 'Not enough money to buy this!'
                logger.trace(msg)
                embed = discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                )
                await interaction.response.edit_message(embed=embed, view=None)
                return
        else:
            pass

        try:
            # We delete the auction
            RedisAuction().destroy(Item.id)
            # We do the financial transaction
            WalletBuyer.bananas -= Auction.price
            WalletSeller.bananas += round(Auction.price * 0.9)
            # We change the Item owner
            Item.bearer = CreatureBuyer.id
        except Exception as e:
            msg = f'Auction buy KO [{e}]'
            logger.error(msg)
            embed = discord.Embed(
                description=msg,
                colour=discord.Colour.red()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title='You successfully acquired:',
                description=(
                    f"{rarity_item_types_discord[Auction.rarity]} "
                    f"**{Auction.metaname}** "
                    f"(Price:{Auction.price})"
                    ),
                colour=discord.Colour.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(
        label='Abord mission!',
        style=discord.ButtonStyle.danger,
        emoji="❌",
        )
    async def ko_button_callback(self, button, interaction):
        msg = f'Item `{self.itemuuid}` Auction KO - Cancelled'
        logger.info(msg)
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        msg = f'Item `{self.itemuuid}` Auction KO - Timeout'
        logger.debug(msg)

    async def interaction_check(self, interaction):
        if interaction.user != self.ctx.author:
            embed = discord.Embed(
                description='Sorry, only @Singouins members can buy Items!',
                colour=discord.Colour.orange()
            )
            await interaction.response.send_message(
                embed=embed,
                view=None,
                ephemeral=True,
                )
            return False
        else:
            return True
