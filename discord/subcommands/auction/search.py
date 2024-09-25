# -*- coding: utf8 -*-

import discord

from discord.commands import option
from loguru import logger
from mongoengine import Q

from mongo.models.Auction import AuctionDocument

from subcommands.auction._tools import auction_time_left
from subcommands.godmode._autocomplete import get_metanames_list

from variables import metaNames, rarity_item_types_discord


def search(group_auction, bot):
    @group_auction.command(
        description='[@Singouins role] Search in the Auction House',
        default_permission=False,
        name='search',
        )
    @option(
        "metatype",
        description="Item Type",
        autocomplete=discord.utils.basic_autocomplete(
            [
                discord.OptionChoice("Armor", value='armor'),
                discord.OptionChoice("Weapon", value='weapon'),
                ]
            )
        )
    @option(
        "metaid",
        description="Item Name",
        autocomplete=get_metanames_list,
        required=False,
        )
    async def search(
        ctx: discord.ApplicationContext,
        metatype: str,
        metaid: str,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_auction} search {metatype} {metaid}')

        try:
            if metaid and isinstance(metaid, str):
                metaid = int(metaid)
                search = f'*{metaNames[metatype][metaid]}*'
            else:
                metaid = None
                search = '*'
        except Exception as e:
            msg = f'Meta ID parsing failed [{e}]'
            logger.error(msg)

        # We get the Item from the Auctions
        try:
            if metatype and metaid:
                query = Q(item__metatype=metatype) & Q(item__metaid=metaid)
            elif metatype:
                query = Q(item__metatype=metatype)
            elif metaid:
                query = Q(item__metaid=metaid)
            else:
                pass

            Auctions = AuctionDocument.objects.get(query)
        except AuctionDocument.DoesNotExist:
            description = 'No items were found matching these criterias.'
            logger.debug(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.orange(),
                    ),
                ephemeral=True,
                )
            return
        except Exception as e:
            description = f'Auction-Search Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return

        # If we are here, Auctions QuerySet is not empty
        # Dirty Gruik to find the max(len(metaname))
        mw = max(len(Auction.item.name) for Auction in Auctions)
        # We need to put a floor to respect the Tableau header
        mw = max(9, mw)
        # Dirty Gruik to find the max(len(sellername))
        sw = max(len(Auction.seller.name) for Auction in Auctions)

        # We add a header for the results "Tableau"
        itemname, price, seller, end = 'Item name', 'Price', 'Seller', 'End'
        description = f"💱 `{itemname:{mw}}` | `{price:8}` | `{end:8}` | `{seller:{sw}}`\n"
        itemname, seller = '-' * (mw + 3), '-' * sw
        description += (
                f"`{itemname:{mw}}` | "
                f"`--------` | "
                f"`--------` | "
                f"`{seller:{sw}}`"
                f"\n"
                )
        # We loop on items retrieved in Auctions
        for Auction in Auctions:
            description += (
                f"{rarity_item_types_discord[Auction.item.rarity]} "
                f"`{Auction.item.name:{mw}}` | "
                f"`{Auction.price:5}` "
                f"{discord.utils.get(bot.emojis, name='moneyB')} | "
                f"`{auction_time_left(Auction.created):8}` | "
                f"`{Auction.seller.name:{sw}}`"
                "\n"
                )

        logger.info(f'{h} └──> Auction-Search Query OK')
        await ctx.respond(
                embed=discord.Embed(
                    title=f'Searched for {metatype.upper()}:{search}',
                    description=description,
                    colour=discord.Colour.green(),
                    ),
                ephemeral=True,
                )
        return
