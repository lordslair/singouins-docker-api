# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.metas import metaNames
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem import RedisItem

from subcommands.godmode._autocomplete import (
    get_singouins_list,
    get_singouin_inventory_item_list,
    )

from variables import (
    URL_ASSETS,
    rarity_item_types_discord,
    )


def take(group_godmode):
    @group_godmode.command(
        description='[@Team role] Take an Item from a Singouin',
        default_permission=False,
        name='take',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_singouins_list
        )
    @option(
        "itemuuid",
        description="Item UUID",
        autocomplete=get_singouin_inventory_item_list
        )
    async def take(
        ctx,
        singouinuuid: str,
        itemuuid: str,
    ):
        name    = ctx.author.name
        channel = ctx.channel.name
        # As we need roles, it CANNOT be used in PrivateMessage
        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_godmode} take '
            f'{singouinuuid} {itemuuid}'
            )

        try:
            Creature = RedisCreature(creatureuuid=singouinuuid)
            Item = RedisItem(itemuuid=itemuuid)
            RedisItem(itemuuid=itemuuid).destroy()
        except Exception as e:
            description = f'Godmode-Take Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return
        else:
            embed = discord.Embed(
                title="An item slowly vanishes!",
                colour=discord.Colour.green()
                )

            embed_field_name = (
                f"{rarity_item_types_discord[Item.rarity]} "
                f"{metaNames[Item.metatype][Item.metaid]['name']}"
                )
            embed_field_value  = f"> Bearer : `{Creature.name}`\n"
            embed_field_value += f"> Bearer : `UUID({Item.bearer})`\n"

            embed.add_field(
                name=f'**{embed_field_name}**',
                value=embed_field_value,
                inline=True,
                )

            embed.set_footer(text=f"ItemUUID: {Item.id}")

            URI_PNG = f'sprites/{Item.metatype}s/{Item.metaid}.png'
            logger.debug(f"[embed.thumbnail] {URL_ASSETS}/{URI_PNG}")
            embed.set_thumbnail(url=f"{URL_ASSETS}/{URI_PNG}")

            await ctx.respond(embed=embed)
            logger.info(f'[#{channel}][{name}] └──> Godmode-Take Query OK')
