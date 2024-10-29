# -*- coding: utf8 -*-

import discord

from loguru import logger

from mongo.models.Item import ItemDocument

from variables import metaNames, rarity_item, rarity_item_types_emoji as rite


async def get_singouin_saleable_item_list(ctx: discord.AutocompleteContext):
    # Pre-flight check
    db_list = []
    try:
        Items = ItemDocument.objects(auctioned=False, bearer=ctx.options['seller_uuid'])
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

        meta = [x for x in metaNames[Item.metatype] if x['_id'] == Item.metaid][0]
        sizex, sizey = map(int, meta['size'].split("x"))

        item_price = sizex * sizey * (meta['tier'] + 1) * rarity_item.index(Item.rarity) // 2
        db_list.append(discord.OptionChoice(f"{eh} {meta['name']} ({item_price})", value=str(Item.id)))  # noqa: E501

    return db_list
