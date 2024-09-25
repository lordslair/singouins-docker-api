# -*- coding: utf8 -*-

import discord
import uuid

from discord.commands import option
from discord.ext import commands
from loguru import logger
from random import randint

from nosql.connector import r

from mongo.models.Creature import (
    CreatureDocument,
    CreatureHP,
    CreatureStats,
    CreatureStatsType,
    CreatureSquad,
    CreatureSlots,
    CreatureKorp
    )
from mongo.models.Instance import InstanceDocument

from subcommands.godmode._autocomplete import (
    get_instances_list,
    get_monster_race_list,
    get_rarity_monsters_list
    )

from variables import (
    env_vars,
    metaNames,
    rarity_monster_types_discord as rmtd,
    )


def pop(group_godmode):
    @group_godmode.command(
        description='[@Team role] Spawn a Monster',
        default_permission=False,
        name='pop',
        )
    @commands.guild_only()  # Hides the command from the menu in DMs
    @commands.has_any_role('Team')
    @option(
        "monster",
        description="Monster Race",
        autocomplete=get_monster_race_list
        )
    @option(
        "instanceuuid",
        description="Instance UUID",
        autocomplete=get_instances_list
        )
    @option(
        "rarity",
        description="Monster Rarity",
        autocomplete=get_rarity_monsters_list,
        )
    @option(
        "posx",
        description="Position X",
        default=randint(2, 4),
        )
    @option(
        "posy",
        description="Position Y",
        default=randint(2, 5),
        )
    async def pop(
        ctx,
        monster: int,
        instanceuuid: str,
        rarity: str,
        posx: int,
        posy: int,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_godmode} pop {monster} {instanceuuid} {rarity}')

        try:
            Instance = InstanceDocument.objects(_id=instanceuuid).get()
        except InstanceDocument.DoesNotExist:
            logger.debug(f"{h} ├──> Godmode-Pop InstanceDocument Query KO (404)")
            return None
        except Exception as e:
            logger.error(f'{h} ├──> Godmode-Pop InstanceDocument Query KO [{e}]')
            return None

        # We create the Monster
        try:
            metaMonster = metaNames['race'][monster - 1]
            logger.trace(f"{h} ├──> Godmode-Pop {rmtd[rarity]} {metaMonster['name']}")

            newCreature = CreatureDocument(
                _id=uuid.uuid3(uuid.NAMESPACE_DNS, metaMonster['name']),
                account=None,
                gender=True,
                hp=CreatureHP(
                    base=metaMonster['min_m'] + 100,
                    current=metaMonster['min_m'] + 100,
                    max=metaMonster['min_m'] + 100,
                    ),
                instance=instanceuuid,
                korp=CreatureKorp(),
                name=metaMonster['name'],
                race=monster,
                rarity=rarity,
                squad=CreatureSquad(),
                slots=CreatureSlots(),
                stats=CreatureStats(
                    spec=CreatureStatsType(),
                    race=CreatureStatsType(),
                    total=CreatureStatsType(
                        b=metaMonster['min_b'],
                        g=metaMonster['min_g'],
                        m=metaMonster['min_m'],
                        p=metaMonster['min_p'],
                        r=metaMonster['min_r'],
                        v=metaMonster['min_v'],
                    ),
                ),
                x=posx,
                y=posy,
            )
            newCreature.save()
        except Exception as e:
            description = f'Godmode-Pop Query KO [{e}]'
            logger.error(f'{h} └──> {description}')
            await ctx.respond(
                embed=discord.Embed(
                    description=description,
                    colour=discord.Colour.red(),
                    )
                )
            return

        # We put the info in pubsub channel for IA to populate the instance
        try:
            pmsg = {
                "action": 'pop',
                "creature": newCreature.to_json(),
                "instance": Instance.to_json(),
                }
            r.publish('ai-creature', pmsg)
        except Exception as e:
            msg = f'Publish(ai-creature) KO [{e}]'
            logger.error(msg)

        # MongoDB CreatureDocument should be created
        # Pub/Sub message should be sent

        embed = discord.Embed(
            title="A new creature appears!",
            colour=discord.Colour.green()
            )

        embed_field_value  = f"> Instance : `{newCreature.instance}`\n"
        embed_field_value += f"> Level : `{newCreature.level}`\n"
        embed_field_value += f"> Position : `({newCreature.x},{newCreature.y})`\n"

        embed.add_field(
            name=f'{rmtd[newCreature.rarity]} **{newCreature.name}**',
            value=embed_field_value,
            inline=True,
            )

        embed.set_footer(text=f"CreatureUUID: {newCreature.id}")

        URI_PNG = f'sprites/creatures/{newCreature.race}.png'
        logger.debug(f"[embed.thumbnail] {env_vars['URL_ASSETS']}/{URI_PNG}")
        embed.set_thumbnail(url=f"{env_vars['URL_ASSETS']}/{URI_PNG}")

        await ctx.respond(embed=embed)
        logger.info(f'{h} └──> Godmode-Pop Query OK')
