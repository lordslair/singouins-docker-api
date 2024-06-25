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
    metaNames,
    rarity_item_types_discord,
    slots_armor,
    slots_weapon,
    )


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

        Creature = CreatureDocument.objects(_id=singouinuuid).get()

        try:
            embed = discord.Embed(
                title=Creature.name,
                # description='Profil:',
                colour=discord.Colour.blue()
                )

            """
            emojiHE = discord.utils.get(client.emojis, name='itemHead')
            emojiSH = discord.utils.get(client.emojis, name='itemShoulders')
            emojiTO = discord.utils.get(client.emojis, name='itemTorso')
            emojiHA = discord.utils.get(client.emojis, name='itemHands')
            emojiLE = discord.utils.get(client.emojis, name='itemLegs')
            emojiFE = discord.utils.get(client.emojis, name='itemFeet')
            """

            value  = ''
            for piece in slots_armor:
                logger.debug(f'EquippedItem search: {piece}')
                EquippedItem = getattr(Creature.slots, piece)
                if EquippedItem:
                    logger.trace(f'EquippedItem found: {piece}')
                    Item = ItemDocument.objects(_id=EquippedItem._id).get()
                    square = rarity_item_types_discord[Item.rarity]
                    name   = metaNames[Item.metatype][Item.metaid]['name']
                    item   = f'{square} {name}'
                else:
                    item   = ':no_entry_sign:'
                value += f"> {slots_armor[piece]} : {item}\n"

            embed.add_field(
                name='**Equipment**',
                value=value,
                inline=True,
                )

            """
            emojiHO = discord.utils.get(client.emojis, name='itemHolster')
            emojiLH = discord.utils.get(client.emojis, name='itemLHand')
            emojiRH = discord.utils.get(client.emojis, name='itemRHand')
            """

            value   = ''
            for weapon in slots_weapon:
                logger.debug(f'EquippedWeapon search: {weapon}')
                EquippedWeapon = getattr(Creature.slots, weapon)
                if EquippedWeapon:
                    logger.trace(f'EquippedWeapon found: {weapon}')
                    Item = ItemDocument.objects(_id=EquippedWeapon._id).get()
                    square = rarity_item_types_discord[Item.rarity]
                    name   = metaNames[Item.metatype][Item.metaid]['name']
                    item   = f'{square} {name}'
                else:
                    item   = ':no_entry_sign:'
                value += f"> {slots_weapon[weapon]} : {item}\n"

            embed.add_field(
                name='**Weapons**',
                value=value,
                inline=True,
                )

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(race=Creature.race, creatureuuid=Creature.id):
                file = discord.File(
                    f'/tmp/{Creature.id}.png',
                    filename=f'{Creature.id}.png'
                    )
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
