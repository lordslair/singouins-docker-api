# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.metas import metaNames, metaWeapons
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem import RedisItem

from subcommands.godmode._autocomplete import (
    get_instances_list,
    get_metanames_list,
    get_rarity_item_list,
    get_singouins_in_instance_list,
    )

from variables import (
    PCS_URL,
    rarity_item_types_discord,
    )


def give(group_godmode):
    @group_godmode.command(
        description='[@Team role] Loot an Item to a Singouin',
        default_permission=False,
        name='give',
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
        "rarity",
        description="Item Rarity",
        autocomplete=get_rarity_item_list
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
        )
    async def give(
        ctx,
        instanceuuid: str,
        singouinuuid: str,
        rarity: str,
        metatype: str,
        metaid: int,
    ):
        name    = ctx.author.name
        channel = ctx.channel.name
        # As we need roles, it CANNOT be used in PrivateMessage
        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_godmode} give '
            f'{instanceuuid} {singouinuuid} {rarity} {metatype} {metaid}'
            )

        Creature = RedisCreature(creatureuuid=singouinuuid)

        try:
            Item = RedisItem().new(
                creatureuuid=singouinuuid,
                item_caracs={
                    "metatype": metatype,
                    "metaid": metaid,
                    "bound": True,
                    "bound_type": 'BoP',
                    "modded": False,
                    "mods": None,
                    "state": 100,
                    "rarity": rarity,
                },
            )
        except Exception as e:
            description = f'Godmode-Give Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return
        else:
            if Item.metatype == 'armor':
                max_ammo = None
            elif Item.metatype == 'weapon':
                meta = dict(
                    list(
                        filter(lambda x: x["id"] == Item.metaid, metaWeapons)
                        )[0]
                    )  # Gruikfix
                max_ammo = meta['max_ammo']
            else:
                pass

            embed = discord.Embed(
                title="A new item appears!",
                colour=discord.Colour.green()
                )

            embed_field_name = (
                f"{rarity_item_types_discord[Item.rarity]} "
                f"{metaNames[Item.metatype][Item.metaid]['name']}"
                )
            embed_field_value  = f"> Bearer : `{Creature.name}`\n"
            embed_field_value += f"> Bearer : `UUID({Item.bearer})`\n"
            embed_field_value += (
                f"> Bound : `{Item.bound} ({Item.bound_type})`\n"
                )

            if max_ammo is not None:
                embed_field_value += f"> Ammo : `{Item.ammo}/{max_ammo}`\n"

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
            logger.info(f'[#{channel}][{name}] └──> Godmode-Give Query OK')
