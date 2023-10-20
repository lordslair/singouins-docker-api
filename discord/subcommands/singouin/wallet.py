# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisWallet import RedisWallet

from subcommands.singouin._autocomplete import get_mysingouins_list
from subcommands.singouin._tools import creature_sprite


def wallet(group_singouin, bot):
    @group_singouin.command(
        description=(
            '[@Singouins role] '
            'Display your Singouin Wallet'
            ),
        default_permission=False,
        name='wallet',
        )
    @commands.has_any_role('Singouins')
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_mysingouins_list
        )
    async def wallet(
        ctx,
        singouinuuid: str,
    ):
        name = ctx.author.name
        channel = ctx.channel.name
        file = None

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} wallet {singouinuuid}'
            )

        try:
            Creature = RedisCreature(creatureuuid=singouinuuid)
            Wallet = RedisWallet(creatureuuid=singouinuuid)

            embed = discord.Embed(
                title=Creature.name,
                # description='Profil:',
                colour=discord.Colour.blue()
            )

            emojiScraps = {
                'broken': discord.utils.get(bot.emojis, name='shardB'),
                'common': discord.utils.get(bot.emojis, name='shardC'),
                'uncommon': discord.utils.get(bot.emojis, name='shardU'),
                'rare': discord.utils.get(bot.emojis, name='shardR'),
                'epic': discord.utils.get(bot.emojis, name='shardE'),
                'legendary': discord.utils.get(bot.emojis, name='shardL'),
                }

            # We generate Scraps field
            value = ''
            for rarity in emojiScraps:
                value += (
                    f"> {emojiScraps[rarity]} : "
                    f"`{getattr(Wallet, rarity): >4}`\n"
                    )
            embed.add_field(name='**Scraps**', value=value, inline=True)

            # We generate Ammo field
            emojiAmmos = {
                'cal22': discord.utils.get(bot.emojis, name='ammo22'),
                'cal223': discord.utils.get(bot.emojis, name='ammo223'),
                'cal311': discord.utils.get(bot.emojis, name='ammo311'),
                'cal50': discord.utils.get(bot.emojis, name='ammo50'),
                'cal55': discord.utils.get(bot.emojis, name='ammo55'),
                'shell': discord.utils.get(bot.emojis, name='ammoShell'),
                }

            value = ''
            for caliber in emojiAmmos:
                value += (
                    f"> {emojiAmmos[caliber]} : "
                    f"`{getattr(Wallet, caliber): >4}`\n"
                    )
            embed.add_field(name='**Ammo**', value=value, inline=True)

            # We generate Specials field
            emojiSpecials = {
                'cal22': discord.utils.get(bot.emojis, name='ammoArrow'),
                'cal223': discord.utils.get(bot.emojis, name='ammoBolt'),
                'cal311': discord.utils.get(bot.emojis, name='ammoFuel'),
                'cal50': discord.utils.get(bot.emojis, name='ammoGrenade'),
                'cal55': discord.utils.get(bot.emojis, name='ammoRocket'),
                'shell': discord.utils.get(bot.emojis, name='ammoShell'),
                }

            value = ''
            for caliber in emojiSpecials:
                value += (
                    f"> {emojiSpecials[caliber]} : "
                    f"`{getattr(Wallet, caliber): >4}`\n"
                    )
            embed.add_field(name='**Specials**', value=value, inline=True)

            # We generate Currency field
            if Creature.race in [1, 2, 3, 4]:
                # Creature is a Singouin, we use bananas
                value = (
                    f"> {discord.utils.get(bot.emojis, name='moneyB')} : "
                    f"`{Wallet.bananas: >4}`"
                    )
            elif Creature.race in [5, 6, 7, 8]:
                # Creature is a Pourchon, we use sausages
                value = (
                    f"> {discord.utils.get(bot.emojis, name='moneyB')} : "
                    f"`{Wallet.sausages: >4}`"
                    )
            else:
                # We fucked up
                value = ""

            embed.add_field(name='**Currency**', value=value, inline=True)

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(race=Creature.race, creatureuuid=Creature.id):
                file = discord.File(
                    f'/tmp/{Creature.id}.png',
                    filename=f'{Creature.id}.png'
                    )
                embed.set_thumbnail(url=f'attachment://{Creature.id}.png')
        except Exception as e:
            description = f'Singouin-Wallet Query KO [{e}]'
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
            logger.info(f'[#{channel}][{name}] └──> Singouin-Squad Query OK')
            await ctx.respond(embed=embed, ephemeral=True, file=file)
            return
