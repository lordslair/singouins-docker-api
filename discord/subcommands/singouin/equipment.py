# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument

from subcommands.singouin._autocomplete import get_mysingouins_list
from subcommands.singouin._tools import creature_sprite
from variables import (
    metaIndexed,
    rarity_item_types_discord as ritd,
    slots_armor,
    slots_weapon,
    )


def slottype_generator(Creature: CreatureDocument, slots: dict):
    """
    Generates a formatted string representing the equipped items
    for the specified creature and their corresponding slots.

    Parameters:
    - Creature (CreatureDocument): The creature object containing equipped items.
    - slots (dict): A dictionary mapping slot names to their descriptions.

    Returns:
    - str: A formatted string listing each slot with its corresponding item or a no-entry sign.
    """
    value   = ''
    for slot_name in slots:
        logger.debug(f'EquippedItem search: {slot_name}')
        EquippedItem = getattr(Creature.slots, slot_name)
        if EquippedItem:
            Item = ItemDocument.objects(_id=EquippedItem.id).get()
            logger.trace(f'EquippedItem found: {Item.id}')
            item   = f"{ritd[Item.rarity]} {metaIndexed[Item.metatype][Item.metaid]['name']}"
        else:
            item   = ':no_entry_sign:'
        value += f"> {slots[slot_name]} : {item}\n"

    return value


def equipment(group_singouin):
    @group_singouin.command(
        description=(
            '[@Singouins role] '
            'Display your Singouin Equipped items'
            ),
        default_permission=False,
        name='equipment',
        )
    @commands.has_any_role('Singouins')
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_mysingouins_list
        )
    async def equipment(
        ctx,
        singouinuuid: str,
    ):
        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_singouin} equipment {singouinuuid}')

        file = None

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
            logger.info(f'{h} └──> Singouin-Equipment Query KO ({msg})')
            return
        except Exception as e:
            logger.error(f'MongoDB Query KO [{e}]')

        try:
            embed = discord.Embed(
                title=Creature.name,
                colour=discord.Colour.blue()
                )

            armors_data = slottype_generator(Creature, slots=slots_armor)
            embed.add_field(name='**Equipment**', value=armors_data, inline=True)

            weapons_data = slottype_generator(Creature, slots=slots_weapon)
            embed.add_field(name='**Weapons**', value=weapons_data, inline=True)

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(Creature):
                file = discord.File(f'/tmp/{Creature.id}.png', filename=f'{Creature.id}.png')
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')

        except Exception as e:
            description = f'Singouin-Equipment Query KO [{e}]'
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
            logger.info(f'{h} └──> Singouin-Equipment Query OK')
