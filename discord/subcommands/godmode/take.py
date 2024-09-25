# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument

from subcommands.godmode._autocomplete import (
    get_singouins_list,
    get_singouin_inventory_item_list,
    )

from variables import (
    env_vars,
    metaNames,
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

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_godmode} take {singouinuuid} {itemuuid}')

        try:
            Creature = CreatureDocument.objects(_id=singouinuuid).get()
            Item = ItemDocument.objects(_id=itemuuid).get()
        except CreatureDocument.DoesNotExist:
            msg = 'Auction NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Auction-Remove Query KO ({msg})')
            return
        except ItemDocument.DoesNotExist:
            msg = 'Item NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Auction-Remove Query KO ({msg})')
            return
        except Exception as e:
            description = f'Godmode-Take Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return

        try:
            Item.delete()
        except Exception as e:
            description = f'Godmode-Take Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
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
            logger.debug(f"[embed.thumbnail] {env_vars['URL_ASSETS']}/{URI_PNG}")
            embed.set_thumbnail(url=f"{env_vars['URL_ASSETS']}/{URI_PNG}")

            await ctx.respond(embed=embed)
            logger.info(f'{h} └──> Godmode-Take Query OK')
