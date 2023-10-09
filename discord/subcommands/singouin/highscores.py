# -*- coding: utf8 -*-

import discord

from discord.commands import option
from discord.ext import commands
from loguru import logger

from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisHS import RedisHS

from subcommands.singouin._autocomplete import get_singouins_list


def highscores(group_singouin, bot):
    @group_singouin.command(
        description='[@Singouins role] Display your Singouin(s) HighScores',
        default_permission=False,
        name='highscores',
        )
    @commands.has_any_role('Singouins', 'Team')
    @option(
        "singouinuuid",
        description="Singouin UUID",
        autocomplete=get_singouins_list
        )
    async def highscores(
        ctx,
        singouinuuid: str,
    ):
        name = ctx.author.name
        channel = ctx.channel.name

        logger.info(
            f'[#{channel}][{name}] '
            f'/{group_singouin} highscores {singouinuuid}'
            )

        Creature = RedisCreature(creatureuuid=singouinuuid)
        HS = RedisHS(creatureuuid=singouinuuid)

        """
        # We try to fetch the TOP1 HighScores
        try:
            maxhs_score = {}
            HighScores = RedisHS().search(query='*')
            if HighScores and len(HighScores) > 0:
                for HighScore in HighScores:
                    for key, val in HighScore.items():
                        if key == 'payload':
                            pass
                        elif key == 'id':
                            creatureuuid = val
                        else:
                            if key not in maxhs_score:
                                maxhs_score[key] = {
                                    "value": 0,
                                    "creature": None,
                                    }

                            if val and val >= maxhs_score[key]['value']:
                                maxhs_score[key]['value'] = val
                                maxhs_score[key]['creature'] = creatureuuid

        except Exception as e:
            msg = f'Max HighScores Query KO [{e}]'
            logger.error(msg)

        logger.success(maxhs_score)

        # We check if the Creature is the TOP1 or not
        medal = {}
        for hs in maxhs_score.keys():
            if maxhs_score[hs]['creature'] == Creature.id:
                medal[hs] = ':first_place: '
            else:
                medal[hs] = ''
        """

        embed = discord.Embed(
            title=f"{Creature.name} HighScores :trophy:",
            colour=discord.Colour.blue()
        )

        tree = {}
        for key, val in HS.as_dict().items():
            t = tree
            prev = None
            for part in key.split('_'):
                if prev is not None:
                    t = t.setdefault(prev, {})
                prev = part
            else:
                t.setdefault(prev, val)

        for section in tree:
            embed_field_value  = ''
            if not isinstance(tree[section], dict):
                continue
            for subsection in tree[section]:
                embed_field_value += (
                    f"> {subsection.capitalize()} : "
                    f"`{tree[section][subsection]}`\n"
                    )
            embed.add_field(
                name=f'**{section.capitalize()}:**',
                value=embed_field_value,
                inline=True,
                )

        await ctx.respond(embed=embed, ephemeral=True)
        logger.info(f'[#{channel}][{name}] └──> Singouin-HighScore Query OK')
