# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisKorp import RedisKorp
from nosql.models.RedisSearch import RedisSearch

from subcommands.singouin._autocomplete import get_mysingouins_list
from subcommands.singouin._tools import creature_sprite


def korp(group_singouin, bot):
    @group_singouin.command(
        description='[@Singouins role] Display your Singouin Korp',
        default_permission=False,
        name='korp',
        )
    @commands.has_any_role('Singouins', 'Team')
    @option(
        "singouinuuid",
        description="Singouin ID",
        autocomplete=get_mysingouins_list
        )
    async def korp(
        ctx,
        singouinuuid: str,
    ):
        name = ctx.author.name
        channel = ctx.channel.name
        file = None

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} korp {singouinuuid}'
            )

        try:
            Creature = RedisCreature(creatureuuid=singouinuuid)

            if Creature.korp is None:
                description = (
                    f"Your Singouin **{Creature.name}** is not in a Korp"
                    )
                logger.error(f'[#{channel}][{name}] └──> {description}')
                await ctx.respond(
                    embed=discord.Embed(
                        description=description,
                        colour=discord.Colour.red(),
                        ),
                    ephemeral=True,
                    )
                return

            Korp = RedisKorp(korpuuid=Creature.korp)
            if Korp.id is None:
                description = 'Singouin-Korp Query KO (Korp Not Found)'
                logger.warning(f'[#{channel}][{name}] └──> {description}')
                await ctx.respond(
                    embed=discord.Embed(
                        description=description,
                        colour=discord.Colour.orange(),
                        ),
                    ephemeral=True,
                    )
                return

            emojiRace = [
                discord.utils.get(bot.emojis, name='raceC'),
                discord.utils.get(bot.emojis, name='raceG'),
                discord.utils.get(bot.emojis, name='raceM'),
                discord.utils.get(bot.emojis, name='raceO'),
                ]

            KorpMembers = RedisSearch().creature(
                f"(@korp:{Korp.id.replace('-', ' ')}) & "
                f"(@korp_rank:-Pending)"
                )
            KorpPending = RedisSearch().creature(
                f"(@korp:{Korp.id.replace('-', ' ')}) & "
                f"(@korp_rank:Pending)"
                )

            # Dirty Gruik to find the max(len(Member.name))
            KorpAll = KorpMembers.results + KorpPending.results
            membername_width = max(
                len(Member.name) for Member in KorpAll
                )

            mydesc = ''
            for Member in KorpMembers.results:
                emojiMyRace = emojiRace[Member.race - 1]
                if Member.id == Korp.leader:
                    # This Singouin is the leader
                    title = ':first_place: Leader'
                else:
                    title = ':second_place: Member'
                level = f"(lvl:{Member.level})"
                mydesc += (
                    f"{emojiMyRace} "
                    f"`{Member.name:<{membername_width}} {level:>8}` | "
                    f"{title}\n"
                    )

            for Pending in KorpPending.results:
                emojiMyRace = emojiRace[Pending.race - 1]
                title = ':third_place: Pending'
                level = f"(lvl:{Pending.level})"
                mydesc += (
                    f"{emojiMyRace} "
                    f"`{Pending.name:<{membername_width}} {level:>8}` | "
                    f"{title}\n"
                    )

            embed = discord.Embed(
                title=f"Korp <{Korp.name}>",
                description=mydesc,
                colour=discord.Colour.blue()
                )

            # We check if we have a sprite to add as thumbnail
            if creature_sprite(race=Creature.race, creatureuuid=Creature.id):
                file = discord.File(
                    f'/tmp/{Creature.id}.png',
                    filename=f'{Creature.id}.png'
                    )
            embed.set_thumbnail(url=f'attachment://{Creature.id}.png')
        except Exception as e:
            description = f'Singouin-Korp Query KO [{e}]'
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
            logger.info(f'[#{channel}][{name}] └──> Singouin-Korp Query OK')
            await ctx.respond(embed=embed, ephemeral=True, file=file)
            return
