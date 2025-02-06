# -*- coding: utf8 -*-

import discord

from loguru import logger

from mongo.models.Item import ItemDocument
from mongo.models.Satchel import SatchelDocument

from variables import AMMUNITIONS, metaIndexed, RARITY_ITEM, rarity_item_types_emoji as rite


async def get_singouin_saleable_ammo_list(ctx: discord.AutocompleteContext):
    # Pre-flight check
    db_list = []

    try:
        Satchel = SatchelDocument.objects(_id=ctx.options['singouin_uuid']).get()
    except SatchelDocument.DoesNotExist:
        logger.debug("SatchelDocument Query KO (404)")
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')

    try:
        for caliber, price in AMMUNITIONS.items():
            logger.success(caliber)
            if getattr(Satchel.ammo, caliber) >= 10:
                item_name = caliber.capitalize()
                item_price = price * 10
                db_list.append(discord.OptionChoice(f"💥 10x {item_name} ({item_price})", value=caliber))  # noqa: E501
    except Exception as e:
        logger.error(f'AMMUNITIONS Query KO [{e}]')
    else:
        return db_list


async def get_singouin_saleable_item_list(ctx: discord.AutocompleteContext):
    # Pre-flight check
    db_list = []
    try:
        Items = ItemDocument.objects(auctioned=False, bearer=ctx.options['singouin_uuid'])
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
    else:
        if len(Items) == 0:
            msg = 'Item NotFound or not matching criterias'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'Query KO ({msg})')
            return db_list

    # Real stuff
    for Item in Items:
        eh = rite[Item.rarity]

        meta = metaIndexed[Item.metatype][Item.metaid]
        sizex, sizey = map(int, meta['size'].split("x"))

        item_name = meta['name']
        item_price = sizex * sizey * (meta['tier'] + 1) * RARITY_ITEM.index(Item.rarity) // 2
        db_list.append(discord.OptionChoice(f"{eh} {item_name} ({item_price})", value=str(Item.id)))  # noqa: E501

    return db_list
