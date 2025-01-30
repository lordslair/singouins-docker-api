# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument

from subcommands.singouin._autocomplete import get_mysingouins_list
from subcommands.singouin._tools import creature_sprite
from variables import item_types_discord as itd, metaIndexed, rarity_item_types_discord as ritd


def inventory(group_singouin):
    @group_singouin.command(
        description=(
            '[@Singouins role] '
            'Display your Singouin Inventory'
            ),
        default_permission=False,
        name='inventory',
        )
    @commands.has_any_role('Singouins')
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_mysingouins_list
        )
    async def inventory(
        ctx,
        singouinuuid: str,
    ):
        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_singouin} inventory {singouinuuid}')

        file = None
        Items = ItemDocument.objects(bearer=singouinuuid, metatype__in=["weapon", "armor"])

        try:
            Creature = CreatureDocument.objects(_id=singouinuuid).get()
        except CreatureDocument.DoesNotExist:
            msg = 'Creature NotFound'
            await ctx.respond(
                embed=discord.Embed(
                    description=msg,
                    colour=discord.Colour.orange()
                    ),
                ephemeral=True,
                )
            logger.info(f'{h} └──> Singouin-Inventory Query KO ({msg})')
            return
        except Exception as e:
            logger.error(f'MongoDB Query KO [{e}]')

        embed = discord.Embed(
            title=Creature.name,
            # description='Profil:',
            colour=discord.Colour.blue()
            )

        try:
            value = ''
            for Item in Items:
                logger.trace(f'{h} ├──> Loop on ItemUUID({Item.id})')
                if Item.offsetx or Item.offsety:
                    logger.trace(f'{h} ├──> Equipped')
                    # Item is equipped, we DO NOT list it
                    continue
                elif hasattr(Item, 'auctioned') and Item.auctioned is True:
                    logger.trace(f'{h} ├──> Auctioned')
                    # Item is auctioned, we DO NOT list it
                    continue
                value += (
                    f"> {itd[Item.metatype]} {ritd[Item.rarity]} "
                    f"[{Item.bound_type}] {metaIndexed[Item.metatype][Item.metaid]['name']} \n"
                    )

            # We looped over all items in Singouin's pockets
            embed.add_field(
                name=':luggage: **Inventory** :',
                value=value,
                inline=True
                )

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(Creature):
                file = discord.File(f'/tmp/{Creature.id}.png', filename=f'{Creature.id}.png')
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')
        except Exception as e:
            description = f'Singouin-Inventory Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    ),
                ephemeral=True,
                )
            return
        else:
            await ctx.respond(embed=embed, ephemeral=True, file=file)
            logger.info(f'{h} └──> Singouin-Inventory Query OK')
