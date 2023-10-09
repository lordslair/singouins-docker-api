# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisSquad import RedisSquad
from nosql.models.RedisSearch import RedisSearch

from subcommands.singouin._autocomplete import get_singouins_list


def squad(group_singouin, bot):
    @group_singouin.command(
        description='[@Singouins role] Display your Singouin Squad',
        default_permission=False,
        name='squad',
        )
    @commands.has_any_role('Singouins', 'Team')
    @option(
        "singouinuuid",
        description="Singouin ID",
        autocomplete=get_singouins_list
        )
    async def squad(
        ctx,
        singouinuuid: str,
    ):
        name         = ctx.author.name
        channel      = ctx.channel.name

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} equipment {singouinuuid}'
            )

        Creature = RedisCreature(creatureuuid=singouinuuid)
        if Creature.squad is None:
            description = (
                f"Your Singouin **{Creature.name}** is not in a Squad"
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

        Squad = RedisSquad(squaduuid=Creature.squad)
        if Squad.id is None:
            description = 'Singouin-Squad Query KO (Squad Not Found)'
            logger.error(f'[#{channel}][{name}] └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
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

        SquadMembers = RedisSearch().creature(
            f"(@squad:{Squad.id.replace('-', ' ')}) & "
            f"(@squad_rank:-Pending)"
            )
        SquadPending = RedisSearch().creature(
            f"(@squad:{Squad.id.replace('-', ' ')}) & "
            f"(@squad_rank:Pending)"
            )

        # Dirty Gruik to find the max(len(Member.name))
        SquadAll = SquadMembers.results + SquadPending.results
        membername_width = max(
            len(Member.name) for Member in SquadAll
            )

        mydesc = ''
        for Member in SquadMembers.results:
            emojiMyRace = emojiRace[Member.race - 1]
            if Member.id == Squad.leader:
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

        for Pending in SquadPending.results:
            emojiMyRace = emojiRace[Pending.race - 1]
            title = ':third_place: Pending'
            level = f"(lvl:{Pending.level})"
            mydesc += (
                f"{emojiMyRace} "
                f"`{Pending.name:<{membername_width}} {level:>8}` | "
                f"{title}\n"
                )

        await ctx.respond(
            embed=discord.Embed(
                title="Squad",
                description=mydesc,
                colour=discord.Colour.blue()
                ),
            ephemeral=True,
            )
        logger.info(f'[#{channel}][{name}] └──> Singouin-Squad Query OK')
