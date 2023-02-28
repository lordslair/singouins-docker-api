# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.metas import metaNames
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem import RedisItem

from subcommands.godmode._autocomplete import (
    get_instances_list,
    get_singouins_in_instance_list,
    get_singouin_inventory_item_list,
    )

from variables import (
    PCS_URL,
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
        "instanceuuid",
        description="Instance UUID",
        autocomplete=get_instances_list
        )
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_singouins_in_instance_list
        )
    @option(
        "itemuuid",
        description="Item UUID",
        autocomplete=get_singouin_inventory_item_list
        )
    async def take(
        ctx,
        instanceuuid: str,
        singouinuuid: str,
        itemuuid: str,
    ):
        name    = ctx.author.name
        channel = ctx.channel.name
        # As we need roles, it CANNOT be used in PrivateMessage
        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_godmode} take '
            f'{instanceuuid} {singouinuuid} {itemuuid}'
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

            embed.set_thumbnail(
                url=(
                    f"{PCS_URL}/resources/sprites"
                    f"/{Item.metatype}s/{Item.metaid}.png"
                    )
                )

            await ctx.respond(embed=embed)
            logger.info(f'[#{channel}][{name}] └──> Godmode-Take Query OK')
