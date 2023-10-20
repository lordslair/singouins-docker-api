# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.metas import metaNames
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSearch import RedisSearch
from nosql.models.RedisSlots import RedisSlots

from subcommands.singouin._autocomplete import get_singouins_list
from subcommands.singouin._tools import creature_sprite
from variables import rarity_item_types_discord, slots_types


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
        autocomplete=get_singouins_list
        )
    async def inventory(
        ctx,
        singouinuuid: str,
    ):
        name = ctx.author.name
        channel = ctx.channel.name
        file = None

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} inventory {singouinuuid}'
            )

        Creature = RedisCreature(creatureuuid=singouinuuid)
        Items = RedisSearch().item(
            query=f"@bearer:{singouinuuid.replace('-', ' ')}"
            )
        logger.debug(f'[#{channel}][{name}] ├──> Redis calls OK')

        embed = discord.Embed(
            title=f"{Creature.name} - Inventory",
            # description='Profil:',
            colour=discord.Colour.blue()
            )

        emojis = {
            'armor': ':shirt:',
            'weapon': ':dagger:'
        }

        try:
            Slots = RedisSlots(creatureuuid=singouinuuid)
            equipped_uuids = []
            for slot in slots_types:
                slot_id = getattr(Slots, slot)
                if slot_id is not None:
                    equipped_uuids.append(slot_id)
                    logger.debug(
                        f'[#{channel}][{name}] ├──> Equipped: '
                        f'[{slot_id}] {slot}'
                        )

            Auctions = RedisSearch().auction(
                query=(f'@sellerid:{singouinuuid.replace("-", " ")}')
                )
            auctionned_uuids = []
            for Auction in Auctions.results:
                auctionned_uuids.append(Auction.id)
                logger.debug(
                    f'[#{channel}][{name}] ├──> Auctionned: '
                    f'[{Auction.id}] {Auction.metaname}'
                    )

            for metatype in ('armor', 'weapon'):
                Items = RedisSearch().item(
                    query=(
                        f"(@bearer:{singouinuuid.replace('-', ' ')}) "
                        f"& (@metatype:{metatype})"
                        )
                )

                value = ''
                logger.debug(f'[#{channel}][{name}] ├──> Loop on {metatype}')
                for Item in Items.results:
                    if Item.id in equipped_uuids:
                        # Item is equipped, we DO NOT list it
                        continue
                    elif Item.id in auctionned_uuids:
                        # Item is auctionned, we DO NOT list it
                        continue
                    value += (
                        f"> {rarity_item_types_discord[Item.rarity]} "
                        f"[{Item.bound_type}] "
                        f"{metaNames[Item.metatype][Item.metaid]['name']} \n"
                        )

                # We looped over all items in Singouin's pockets
                embed.add_field(
                    name=f'**{emojis[metatype]} {metatype.capitalize()}** :',
                    value=value,
                    inline=True
                    )

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(race=Creature.race, creatureuuid=Creature.id):
                file = discord.File(
                    f'/tmp/{Creature.id}.png',
                    filename=f'{Creature.id}.png'
                    )
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')
        except Exception as e:
            description = f'Singouin-Inventory Query KO [{e}]'
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
                f'└──> Singouin-Inventory Query OK'
                )
