# -*- coding: utf8 -*-

import datetime
import discord

from discord.commands import option
from loguru import logger

from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument
from mongo.models.Satchel import SatchelDocument

from subcommands.bazaar._autocomplete import get_singouin_saleable_item_list
from subcommands.singouin._autocomplete import get_mysingouins_list

from variables import (
    item_types_discord as itd,
    metaIndexed,
    rarity_item,
    rarity_item_types_discord as ritd,
    )


def sell(group_bazaar, bot):
    @group_bazaar.command(
        description='[@Singouins role] Sell an item at the Bazaar',
        default_permission=False,
        name='sell',
        )
    @option(
        "seller_uuid",
        description="Seller UUID",
        autocomplete=get_mysingouins_list
        )
    @option(
        "item_uuid",
        description="Item UUID",
        autocomplete=get_singouin_saleable_item_list
        )
    async def sell(
        ctx: discord.ApplicationContext,
        seller_uuid: str,
        item_uuid: str,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_bazaar} sell {seller_uuid} {item_uuid}')

        try:
            Creature = CreatureDocument.objects(_id=seller_uuid).get()
        except CreatureDocument.DoesNotExist:
            msg = 'Seller NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Bazaar-Sell Query KO ({msg})')
            return

        try:
            Satchel = SatchelDocument.objects(_id=Creature.id).get()
        except SatchelDocument.DoesNotExist:
            msg = 'Satchel NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Bazaar-Sell Query KO ({msg})')
            return

        try:
            Item = ItemDocument.objects(_id=item_uuid, auctioned=False, bearer=seller_uuid).get()
        except ItemDocument.DoesNotExist:
            msg = 'Item NotFound or not matching criterias'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Bazaar-Sell Query KO ({msg})')
            return
        else:
            meta = metaIndexed[Item.metatype][Item.metaid]
            sizex, sizey = map(int, meta['size'].split("x"))
            item_price = sizex * sizey * (meta['tier'] + 1) * rarity_item.index(Item.rarity) // 2

        try:
            # We do the financial transaction
            Satchel.currency.banana += item_price
            Satchel.updated = datetime.datetime.utcnow()
            Satchel.save()
            # We delete the Item
            Item.delete()
        except Exception as e:
            description = f'Bazaar-Sell Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return

        embed = discord.Embed(
            title="Sold to the Bazaar:",
            description=f"> {itd[Item.metatype]} {ritd[Item.rarity]} **{meta['name']}** (Price:{item_price})",  # noqa: E501
            colour=discord.Colour.green(),
            )
        embed.set_footer(text=f"Account balance: {Satchel.currency.banana} 🍌")

        # We add Thumbnail
        file = discord.File('/tmp/bazaar.png', filename='bazaar.png')
        embed.set_thumbnail(url='attachment://bazaar.png')

        await ctx.respond(embed=embed, file=file, ephemeral=True)
        logger.info(f'{h} └──> Bazaar-Sell Query OK')
        return
