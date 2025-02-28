# -*- coding: utf8 -*-

from bson import json_util
import datetime
import discord
import json

from discord.ui         import View
from loguru             import logger

from mongo.models.Auction import AuctionDocument
from mongo.models.Creature import CreatureDocument
from mongo.models.Highscore import HighscoreDocument
from mongo.models.Item import ItemDocument
from mongo.models.Satchel import SatchelDocument

from utils.redis import r
from variables import env_vars, rarity_item_types_discord as ritd


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
            CreatureSeller = CreatureDocument.objects(_id=Auction.seller.id).get()
            SatchelBuyer = SatchelDocument.objects(_id=self.buyeruuid).get()
            SatchelSeller = SatchelDocument.objects(_id=Auction.seller.id).get()
            HighscoreBuyer = HighscoreDocument.objects(_id=Auction.seller.id).get()
            HighscoreSeller = HighscoreDocument.objects(_id=Auction.seller.id).get()
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
            msg = 'CreatureDocument NotFound (404)'
            await interaction.response.edit_message(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                view=None,
                )
            logger.info(f'{self.h} └──> Auction-Buy Query KO ({msg})')
            return
        except HighscoreDocument.DoesNotExist:
            msg = 'HighscoreDocument NotFound (404)'
            await interaction.response.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{self.h} └──> Bazaar-Sell Query KO ({msg})')
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
            # We do the financial transaction
            SatchelBuyer.currency.banana -= Auction.price
            SatchelBuyer.updated = datetime.datetime.utcnow()
            SatchelBuyer.save()
            SatchelSeller.currency.banana += Auction.price
            SatchelSeller.updated = datetime.datetime.utcnow()
            SatchelSeller.save()
            # We change the Item owner
            Item.auctioned = False
            Item.bearer = CreatureBuyer.id
            Item.updated = datetime.datetime.utcnow()
            Item.save()
            # Highscore
            HighscoreSeller.internal.item.sold += 1
            HighscoreSeller.updated = datetime.datetime.utcnow()
            HighscoreSeller.save()
            HighscoreBuyer.internal.item.bought += 1
            HighscoreBuyer.updated = datetime.datetime.utcnow()
            HighscoreBuyer.save()
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
                description=f"{ritd[Item.rarity]} **{Auction.item.name}** (Price:{Auction.price})",
                colour=discord.Colour.green(),
                )
            embed.set_footer(text=f"ItemUUID: {Auction.item.id}")
            await interaction.response.edit_message(
                embed=embed,
                view=None,
                )

            # Optionnal, sends a DM to a registered user
            try:
                # Convert the MongoDB document to JSON, handling datetime fields
                creature_json = json.loads(json_util.dumps(CreatureSeller.to_mongo().to_dict()))
                r.publish(
                    env_vars['PS_DISCORD'],
                    json.dumps({
                        "creature": creature_json,
                        "msg": (
                            f":scales: Someone bought for `{Auction.price:4}`:banana: the item: "
                            f"{ritd[Item.rarity]} {Auction.item.name}"
                            ),
                        "embed": False,
                        })
                )
            except Exception as e:
                logger.error(f"Discord msg publish KO [{e}]")
            else:
                logger.trace("Discord msg publish OK")

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
        for item in self.children:
            item.disabled = True
        try:
            # Edit the message to disable the button after timeout
            await self.message.edit(view=self)
        except discord.NotFound:
            pass
            # logger.warning(f'{self.h} └──> Message not found for Auction-Buy Timeout. (deleted)')

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
