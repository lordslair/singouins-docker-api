# -*- coding: utf8 -*-

import discord
import uuid

from discord.commands import option
from discord.ext import commands
from loguru import logger
from random import randint

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

from utils.redis import cput
from variables import (
    env_vars,
    metaIndexed,
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
        "race_id",
        description="Monster Race",
        autocomplete=get_monster_race_list
        )
    @option(
        "instance_uuid",
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
        race_id: int,
        instance_uuid: str,
        rarity: str,
        posx: int,
        posy: int,
    ):

        h = f'[#{ctx.channel.name}][{ctx.author.name}]'
        logger.info(f'{h} /{group_godmode} pop {race_id} {instance_uuid} {rarity}')

        try:
            Instance = InstanceDocument.objects(_id=instance_uuid).get()
        except InstanceDocument.DoesNotExist:
            logger.debug(f"{h} ├──> Godmode-Pop InstanceDocument Query KO (404)")
            return None
        except Exception as e:
            logger.error(f'{h} ├──> Godmode-Pop InstanceDocument Query KO [{e}]')
            return None

        # We create the Monster
        try:
            metaRace = metaIndexed['race'][race_id]
            logger.trace(f"{h} ├──> Godmode-Pop {rmtd[rarity]} {metaRace['name']}")

            newCreature = CreatureDocument(
                _id=uuid.uuid3(uuid.NAMESPACE_DNS, metaRace['name']),
                account=None,
                gender=True,
                hp=CreatureHP(
                    base=metaRace['min_m'] + 100,
                    current=metaRace['min_m'] + 100,
                    max=metaRace['min_m'] + 100,
                    ),
                instance=instance_uuid,
                korp=CreatureKorp(),
                name=metaRace['name'],
                race=race_id,
                rarity=rarity,
                squad=CreatureSquad(),
                slots=CreatureSlots(),
                stats=CreatureStats(
                    spec=CreatureStatsType(),
                    race=CreatureStatsType(),
                    total=CreatureStatsType(
                        b=metaRace['min_b'],
                        g=metaRace['min_g'],
                        m=metaRace['min_m'],
                        p=metaRace['min_p'],
                        r=metaRace['min_r'],
                        v=metaRace['min_v'],
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
        cput(f"ai-creature-{env_vars['API_ENV'].lower()}", {
            "action": 'pop',
            "creature": newCreature.to_json(),
            "instance": Instance.to_json(),
            })

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
