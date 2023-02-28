# -*- coding: utf8 -*-

import discord

from discord.ui         import View
from loguru             import logger

from nosql.models.RedisAuction  import RedisAuction
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisWallet   import RedisWallet

from variables import rarity_item_types_discord


class buyView(View):
    def __init__(self, ctx, buyeruuid, itemuuid):
        super().__init__(timeout=10)
        self.ctx = ctx
        self.buyeruuid = buyeruuid
        self.itemuuid = itemuuid

    @discord.ui.button(
        label='Oh yeah, buy this item!',
        style=discord.ButtonStyle.green,
        emoji="✅",
        )
    async def ok_button_callback(self, button, interaction):
        try:
            Auction = RedisAuction(auctionuuid=self.itemuuid)
            CreatureBuyer = RedisCreature(creatureuuid=self.buyeruuid)
            Item = RedisItem(itemuuid=self.itemuuid)

            WalletBuyer = RedisWallet(creatureuuid=self.buyeruuid)
            WalletSeller = RedisWallet(creatureuuid=Auction.sellerid)
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
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        description=msg,
                        colour=discord.Colour.orange()
                        ),
                    view=None,
                    )
                return

        # A couple of checks first
        if CreatureBuyer.race in [1, 2, 3, 4]:
            # Creature is a Singouin, we use bananas
            if WalletBuyer.bananas < Auction.price:
                # Not enough currency to buy
                msg = 'Not enough money to buy this!'
                logger.trace(msg)
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        description=msg,
                        colour=discord.Colour.orange()
                        ),
                    view=None,
                    )
                return
        elif CreatureBuyer.race in [5, 6, 7, 8]:
            # Creature is a Pourchon, we use sausages
            if WalletBuyer.sausages < Auction.price:
                # Not enough currency to buy
                msg = 'Not enough money to buy this!'
                logger.trace(msg)
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        description=msg,
                        colour=discord.Colour.orange()
                        ),
                    view=None,
                    )
        else:
            pass

        try:
            # We delete the auction
            RedisAuction(auctionuuid=self.itemuuid).destroy()
            # We do the financial transaction
            WalletBuyer.bananas -= Auction.price
            WalletSeller.bananas += round(Auction.price * 0.9)
            # We change the Item owner
            Item.bearer = CreatureBuyer.id
        except Exception as e:
            msg = f'Auction buy KO [{e}]'
            logger.error(msg)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.red()
                    ),
                view=None,
                )
        else:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title='You successfully acquired:',
                    description=(
                        f"{rarity_item_types_discord[Auction.rarity]} "
                        f"**{Auction.metaname}** "
                        f"(Price:{Auction.price})"
                        ),
                    colour=discord.Colour.green()
                ),
                view=None,
                )

    @discord.ui.button(
        label='Abord mission!',
        style=discord.ButtonStyle.danger,
        emoji="❌",
        )
    async def ko_button_callback(self, button, interaction):
        msg = f'Item `{self.itemuuid}` Auction KO - Cancelled'
        logger.info(msg)
        await interaction.response.edit_message(
            embed=discord.Embed(
                description=msg,
                colour=discord.Colour.orange()
                ),
            view=None,
            )

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
