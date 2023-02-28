# -*- coding: utf8 -*-

import discord

from loguru import logger

from nosql.metas import (
    metaArmors,
    metaWeapons,
    )
from nosql.models.RedisSearch import RedisSearch
from variables import rarity_item_types_emoji


async def get_auctioned_item_list(ctx: discord.AutocompleteContext):
    try:
        Auctions = RedisSearch().auction(
            query=f'@metatype:{ctx.options["metatype"]}'
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        if len(Auctions.results) == 0:
            return db_list

        for Auction in Auctions.results:
            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[Auction.rarity]} "
                     f"{Auction.metaname} "
                     f"(Price:{Auction.price})"),
                    value=f"{Auction.id}"
                    )
                )
        return db_list


async def get_singouin_auctionable_item_list(ctx: discord.AutocompleteContext):
    try:
        bearer = ctx.options['selleruuid'].replace('-', ' ')
        Items = RedisSearch().item(query=f'@bearer:{bearer}')
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        for Item in Items.results:
            if Item.bound_type != 'BoE':
                next

            if Item.metatype == 'weapon':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == Item.metaid,
                            metaWeapons
                            )
                        )[0]
                    )  # Gruikfix
            elif Item.metatype == 'armor':
                meta = dict(
                    list(
                        filter(
                            lambda x: x["id"] == Item.metaid,
                            metaArmors
                            )
                        )[0]
                    )  # Gruikfix
            else:
                pass

            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[Item.rarity]} "
                     f"{meta['name']}"),
                    value=f"{Item.id}"
                    )
                )
    return db_list


async def get_singouin_auctioned_item_list(ctx: discord.AutocompleteContext):
    try:
        sellerid = ctx.options["selleruuid"].replace('-', ' ')
        Auctions = RedisSearch().auction(
            query=(
                f"(@metatype:{ctx.options['metatype']}) "
                f"& (@sellerid:{sellerid})"
                )
            )
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
    else:
        db_list = []
        if len(Auctions.results) == 0:
            return db_list

        for Auction in Auctions.results:
            db_list.append(
                discord.OptionChoice(
                    (f"{rarity_item_types_emoji[Auction.rarity]} "
                     f"{Auction.metaname} "
                     f"(Price:{Auction.price})"),
                    value=f"{Auction.id}"
                    )
                )
        return db_list
