# -*- coding: utf8 -*-

import datetime
import discord

from discord.ui         import View
from loguru             import logger

from mongo.models.Auction import AuctionDocument
from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument
from mongo.models.Satchel import SatchelDocument

from variables import ritd


class buyView(View):
    def __init__(self, ctx, buyeruuid, auctionuuid):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.buyeruuid = buyeruuid
        self.auctionuuid = auctionuuid
        self.h = f'[#{ctx.channel.name}][{ctx.author.name}]'

    @discord.ui.button(
        label='Oh yeah, buy this item!',
        style=discord.ButtonStyle.green,
        emoji="✅",
        )
    async def ok_button_callback(self, button, interaction):
        try:
            Auction = AuctionDocument.objects(_id=self.auctionuuid).get()
            Item = ItemDocument.objects(_id=Auction.item.id, auctioned=True).get()
            CreatureBuyer = CreatureDocument.objects(_id=self.buyeruuid).get()
            SatchelBuyer = SatchelDocument.objects(_id=self.buyeruuid).get()
            SatchelSeller = SatchelDocument.objects(_id=Auction.seller.id).get()
        except AuctionDocument.DoesNotExist:
            msg = 'Auction NotFound'
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                view=None,
                )
            logger.info(f'{self.h} └──> Auction-Buy Query KO ({msg})')
            return
        except CreatureDocument.DoesNotExist:
            msg = 'Auction NotFound'
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                view=None,
                )
            logger.info(f'{self.h} └──> Auction-Buy Query KO ({msg})')
            return
        except ItemDocument.DoesNotExist:
            msg = 'Item NotFound'
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                view=None,
                )
            logger.info(f'{self.h} └──> Auction-Buy Query KO ({msg})')
            return

        # Creature is a Singouin, we use bananas
        if SatchelBuyer.currency.banana < Auction.price:
            # Not enough currency to buy
            msg = (
                'Not enough money to buy this!\n '
                f'You have `{SatchelBuyer.currency.banana}` and Seller price is `{Auction.price}`'
                )
            logger.trace(msg)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                view=None,
                )
            return

        try:
            # We delete the auction
            Auction.delete()
            Item.auctionned = False
            # We do the financial transaction
            SatchelBuyer.banana -= Auction.price
            SatchelBuyer.updated = datetime.datetime.utcnow()
            SatchelBuyer.save()
            SatchelSeller.banana += round(Auction.price * 0.9)
            SatchelSeller.updated = datetime.datetime.utcnow()
            SatchelSeller.save()
            # We change the Item owner
            Item.bearer = CreatureBuyer.id
            Item.updated = datetime.datetime.utcnow()
            Item.save()
        except Exception as e:
            msg = f'{self.h} Auction buy KO [{e}]'
            logger.error(msg)
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.red()
                    ),
                view=None,
                )
        else:
            embed = discord.Embed(
                title='You successfully acquired:',
                description=f"{ritd[Auction.rarity]} **{Auction.item.name}** (Price:{Auction.price})",  # noqa: E501
                colour=discord.Colour.green(),
                )
            embed.set_footer(text=f"ItemUUID: {Auction.item.id}")
            await interaction.response.edit_message(
                embed=embed,
                view=None,
                )

    @discord.ui.button(
        label='Abort mission!',
        style=discord.ButtonStyle.danger,
        emoji="❌",
        )
    async def ko_button_callback(self, button, interaction):
        msg = f'{self.h} Auction-Buy KO - Cancelled'
        logger.info(msg)
        await interaction.response.edit_message(
            embed=discord.Embed(
                description=msg,
                colour=discord.Colour.orange()
                ),
            view=None,
            )

    async def on_timeout(self):
        # This method is called when the view times out
        # (i.e., when the timeout period elapses without interaction)
        for item in self.children:
            item.disabled = True
        # Edit the message to disable the button after timeout
        await self.message.edit(view=self)
        logger.trace(f'{self.h} └──> Auction-Buy Timeout')

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
