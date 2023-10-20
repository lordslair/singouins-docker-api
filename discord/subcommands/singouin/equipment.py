# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.metas import metaNames
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisItem import RedisItem
from nosql.models.RedisSlots import RedisSlots

from subcommands.singouin._autocomplete import get_singouins_list
from subcommands.singouin._tools import creature_sprite
from variables import rarity_item_types_discord


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
        autocomplete=get_singouins_list
        )
    async def equipment(
        ctx,
        singouinuuid: str,
    ):
        name = ctx.author.name
        channel = ctx.channel.name
        file = None

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} equipment {singouinuuid}'
            )

        Creature = RedisCreature(creatureuuid=singouinuuid)
        Slots = RedisSlots(creatureuuid=singouinuuid)

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
            pieces = {
                'head': ':military_helmet:',
                'shoulders': ':mechanical_arm:',
                'torso': ':shirt:',
                'hands': ':hand_splayed:',
                'legs': ':mechanical_leg:',
                'feet': ':athletic_shoe:',
                }

            for piece in pieces:
                itemuuid = getattr(Slots, piece)
                if itemuuid is not None:
                    Item = RedisItem(itemuuid=itemuuid)
                    square = rarity_item_types_discord[Item.rarity]
                    name   = metaNames[Item.metatype][Item.metaid]['name']
                    item   = f'{square} {name}'
                else:
                    item   = ':no_entry_sign:'
                value += f"> {pieces[piece]} : {item}\n"

            embed.add_field(name='**Equipment**',
                            value=value,
                            inline=True)

            """
            emojiHO = discord.utils.get(client.emojis, name='itemHolster')
            emojiLH = discord.utils.get(client.emojis, name='itemLHand')
            emojiRH = discord.utils.get(client.emojis, name='itemRHand')
            """

            value   = ''
            weapons = {
                'holster': ':school_satchel:',
                'lefthand': ':left_fist:',
                'righthand': ':right_fist:',
                }

            for weapon in weapons:
                itemuuid = getattr(Slots, weapon)
                if itemuuid is not None:
                    Item = RedisItem(itemuuid=itemuuid)
                    square = rarity_item_types_discord[Item.rarity]
                    name   = metaNames[Item.metatype][Item.metaid]['name']
                    item   = f'{square} {name}'
                else:
                    item   = ':no_entry_sign:'
                value += f"> {weapons[weapon]} : {item}\n"

            embed.add_field(name='**Weapons**',
                            value=value,
                            inline=True)

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(race=Creature.race, creatureuuid=Creature.id):
                file = discord.File(
                    f'/tmp/{Creature.id}.png',
                    filename=f'{Creature.id}.png'
                    )
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')

        except Exception as e:
            description = f'Singouin-Equipment Query KO [{e}]'
            logger.error(f'[#{channel}][{name}] └──> {description}')
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
            logger.info(
                f'[#{channel}][{name}] '
                f'└──> Singouin-Equipment Query OK'
                )
