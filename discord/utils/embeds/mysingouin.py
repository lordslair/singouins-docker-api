# -*- coding: utf8 -*-

import discord
import os

from loguru import logger

from nosql.metas import (
    metaArmors,
    metaWeapons,
    )
from nosql.models.RedisCreature import RedisCreature
from nosql.models.RedisHS       import RedisHS
from nosql.models.RedisItem     import RedisItem
from nosql.models.RedisKorp     import RedisKorp
from nosql.models.RedisPa       import RedisPa
from nosql.models.RedisSquad    import RedisSquad
from nosql.models.RedisSlots    import RedisSlots
from nosql.models.RedisStats    import RedisStats
from nosql.models.RedisUser     import RedisUser
from nosql.models.RedisWallet   import RedisWallet

from utils.variables    import (
    rarity_item_types_discord,
    )

#
# ENV Variables
#

PCS_URL = os.environ.get("SEP_PCS_URL")

#
# Embeds
#


def embed_mysingouin_highscores(bot, singouinuuid):
    Creature = RedisCreature(creatureuuid=singouinuuid)
    HS = RedisHS(Creature)

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

    embed = discord.Embed(
        title=f"{Creature.name} HighScores :trophy:",
        colour=discord.Colour.blue()
    )

    embed_field_value = (
        f"> Deaths : `{HS.global_kills}` {medal['global_kills']}\n"
        )
    embed_field_value += (
        f"> Kills : `{HS.global_deaths}` {medal['global_deaths']}\n"
        )
    embed.add_field(name='**Globals:**', value=embed_field_value, inline=True)

    embed_field_value = (
        f"> Dismantle : `{HS.action_dismantle}` {medal['action_dismantle']}\n"
        )
    embed_field_value += (
        f"> Reload : `{HS.action_reload}` {medal['action_reload']}\n"
        )
    embed_field_value += (
        f"> Unload : `{HS.action_unload}` {medal['action_unload']}\n"
        )
    embed.add_field(name='**Actions:**', value=embed_field_value, inline=True)

    embed_field_value = (
        f"> Potions : `{HS.craft_potion}` {medal['craft_potion']}\n"
        )
    embed.add_field(name='**Crafts:**', value=embed_field_value, inline=True)

    return embed


def embed_mysingouin_korp(bot, singouinuuid):
    Creature = RedisCreature(creatureuuid=singouinuuid)

    if Creature.korp is None:
        embed = discord.Embed(
            description=(
                f"Your Singouin **{Creature.name}** is not in a Korp"
                ),
            colour=discord.Colour.red()
        )
        return embed

    Korp = RedisKorp().get(Creature.korp)
    if Korp is None:
        return None

    emojiRace = [
        discord.utils.get(bot.emojis, name='raceC'),
        discord.utils.get(bot.emojis, name='raceG'),
        discord.utils.get(bot.emojis, name='raceM'),
        discord.utils.get(bot.emojis, name='raceO'),
        ]

    korp = Korp.id.replace('-', ' ')
    KorpMembers = RedisCreature().search(
        f"(@korp:{korp}) & (@squad_rank:-Pending)"
        )
    KorpPending = RedisCreature().search(
        f"(@korp:{korp}) & (@squad_rank:Pending)"
        )

    mydesc = ''
    for member in KorpMembers:
        emojiMyRace = emojiRace[member['race'] - 1]
        if member['id'] == Korp.leader:
            # This SIngouin is the leader
            title = ':first_place: Leader'
        else:
            title = ':second_place: Member'
        level = f"(lvl:{member['level']})"
        mydesc += (
            f"{emojiMyRace} `{member['name']:<14} {level:>8}` | {title}\n"
            )

    for member in KorpPending:
        emojiMyRace = emojiRace[member['race'] - 1]
        title = ':third_place: Pending'
        level = f"(lvl:{member['level']})"
        mydesc += (
            f"{emojiMyRace} `{member['name']:<14} {level:>8}` | {title}\n"
            )

    embed = discord.Embed(
        title=f"Korp <{Korp.name}>",
        description=mydesc,
        colour=discord.Colour.blue()
    )

    return embed


def embed_mysingouin_pa(bot, singouinuuid):
    Creature = RedisCreature(creatureuuid=singouinuuid)
    Pa = RedisPa(Creature)

    try:
        embed = discord.Embed(
            title=Creature.name,
            colour=discord.Colour.blue()
        )

        redpa     = Pa.redpa
        bluepa    = Pa.bluepa

        redbar    = redpa * ':red_square:'
        redbar   += (16 - redpa) * ':white_large_square:'
        bluebar   = bluepa * ':blue_square:'
        bluebar  += (8 - bluepa) * ':white_large_square:'

        embed.add_field(
            name='PA Count:',
            value=(
                f"> {redbar} ({redpa}/16)\n> :clock1: : {Pa.redttnpa}s \n"
                f"▬▬\n"
                f"> {bluebar} ({bluepa}/8)\n> :clock1: : {Pa.bluettnpa}s"
                ),
            inline=False,
            )
    except Exception as e:
        logger.error(f'Discord Embed creation KO [{e}]')
    else:
        logger.trace('Discord Embed creation OK')
        return embed


def embed_mysingouin_stats(bot, singouinuuid):
    Creature = RedisCreature(creatureuuid=singouinuuid)
    Stats = RedisStats(Creature)

    try:
        embed = discord.Embed(
            title=Creature.name,
            description=(
                f":heart_decoration: : "
                f"`{Stats.hp}/{Stats.hpmax} HP`\n"
                ),
            colour=discord.Colour.blue()
        )

        emojiStats = {
            'b': discord.utils.get(bot.emojis, name='statB'),
            'g': discord.utils.get(bot.emojis, name='statG'),
            'm': discord.utils.get(bot.emojis, name='statM'),
            'p': discord.utils.get(bot.emojis, name='statP'),
            'r': discord.utils.get(bot.emojis, name='statR'),
            'v': discord.utils.get(bot.emojis, name='statV'),
            }

        # We generate base Stats field
        value = ''
        for stat in emojiStats:
            value += f"> {emojiStats[stat]} : `{getattr(Stats, stat)}`\n"
        embed.add_field(name='**Base Stats**', value=value, inline=True)

        # We generate DEF Stats field
        value  = f"> :dash: : `{Stats.dodge}`\n"
        value += f"> :shield: : `{Stats.parry}`\n"
        value += "▬\n"
        value += f"> :shield: : `{Stats.arm_b}` (B/:gun:)\n"
        value += f"> :shield: : `{Stats.arm_p}` (P/:axe:)\n"
        embed.add_field(name='**DEF Stats**', value=value, inline=True)

        # We generate OFF Stats field
        value  = f"> :axe: : `{Stats.capcom}`\n"
        value += f"> :gun: : `{Stats.capsho}`\n"
        embed.add_field(name='**OFF Stats**', value=value, inline=True)

    except Exception as e:
        logger.error(f'Discord Embed creation KO [{e}]')
    else:
        logger.trace('Discord Embed creation OK')
        return embed


def embed_mysingouin_wallet(bot, singouinuuid):
    Creature = RedisCreature(creatureuuid=singouinuuid)
    Wallet = RedisWallet(Creature.id)

    try:
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
    except Exception as e:
        logger.error(f'Discord Embed creation KO [{e}]')
    else:
        logger.trace('Discord Embed creation OK')
        return embed


def embed_mysingouin_equipement(bot, singouinuuid):
    Creature = RedisCreature(creatureuuid=singouinuuid)
    Slots = RedisSlots(Creature)

    try:
        equipment = {}
        for slot in [
            'feet', 'hands', 'head',
            'holster', 'lefthand', 'righthand',
            'shoulders', 'torso', 'legs'
        ]:
            itemuuid = getattr(Slots, slot)
            if itemuuid is None:
                # If the Slot is empty, let's put None directly
                equipment[slot] = None
            else:
                # An item is equipped in this slot, lets gather info
                item = RedisItem(Creature).get(itemuuid)
                if item:
                    equipment[slot] = item._asdict()
                else:
                    equipment[slot] = None
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')

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
            if equipment[piece] is not None:
                metaid = equipment[piece]['metaid']
                square = rarity_item_types_discord[equipment[piece]['rarity']]
                meta   = dict(list(filter(
                    lambda x: x["id"] == metaid,
                    metaArmors))[0]
                    )  # GruikFix
                name   = meta['name']
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
            if equipment[weapon] is not None:
                metaid = equipment[weapon]['metaid']
                square = rarity_item_types_discord[equipment[weapon]['rarity']]
                meta   = dict(list(filter(
                    lambda x: x["id"] == metaid,
                    metaWeapons))[0]
                    )  # GruikFix
                name   = meta['name']
                item   = f'{square} {name}'
            else:
                item   = ':no_entry_sign:'
            value += f"> {weapons[weapon]} : {item}\n"

        embed.add_field(name='**Weapons**',
                        value=value,
                        inline=True)
    except Exception as e:
        logger.error(f'Discord Embed creation KO [{e}]')
    else:
        logger.trace('Discord Embed creation OK')
        return embed


def embed_mysingouin_list(bot, ctx):
    # Pre-flight checks : Roles
    # Fetch the Discord role
    try:
        singouinrole = discord.utils.get(
            ctx.author.guild.roles,
            name='Singouins'
            )
    except Exception as e:
        embed = discord.Embed(
            description=f'User Singouins get-role:Singouins KO [{e}]',
            colour=discord.Colour.red()
        )
        return embed
    else:
        if singouinrole not in ctx.author.roles:
            embed = discord.Embed(
                description=(
                    'Unauthorized user: '
                    'Use `/user command: grant` before'
                    ),
                colour=discord.Colour.orange()
            )
            return embed

    emojiRace = [
        discord.utils.get(bot.emojis, name='raceC'),
        discord.utils.get(bot.emojis, name='raceG'),
        discord.utils.get(bot.emojis, name='raceM'),
        discord.utils.get(bot.emojis, name='raceO'),
        ]

    discordname = f'{ctx.author.name}#{ctx.author.discriminator}'
    Users = RedisUser().search(field='d_name', query=discordname)

    if len(Users) == 0:
        msg = f'No User linked with `{discordname}`'
        embed = discord.Embed(
            description=msg,
            colour=discord.Colour.orange()
        )
        return embed
    else:
        User = Users[0]
        account = User['id'].replace('-', ' ')
        Creatures = RedisCreature().search(query=f'@account:{account}')

    try:
        mydesc = ''
        for Creature in Creatures:
            emojiMyRace = emojiRace[Creature['race'] - 1]
            mydesc += (
                f"{emojiMyRace} {Creature['name']} "
                f"| Level:{Creature['level']}\n"
                )

        embed = discord.Embed(
            title='Your Singouins:',
            description=mydesc,
            colour=discord.Colour.blue()
        )
    except Exception as e:
        logger.error(f'Discord Embed creation KO [{e}]')
    else:
        logger.trace('Discord Embed creation OK')
        return embed


def embed_mysingouin_squad(bot, singouinuuid):
    Creature = RedisCreature(creatureuuid=singouinuuid)

    if Creature.squad is None:
        embed = discord.Embed(
            description=(
                f"Your Singouin **{Creature.name}** is not in a Squad"
                ),
            colour=discord.Colour.red()
        )
        return embed

    Squad = RedisSquad().get(Creature.squad)
    if Squad is None:
        return None

    emojiRace = [
        discord.utils.get(bot.emojis, name='raceC'),
        discord.utils.get(bot.emojis, name='raceG'),
        discord.utils.get(bot.emojis, name='raceM'),
        discord.utils.get(bot.emojis, name='raceO'),
        ]

    squad = Squad.id.replace('-', ' ')
    SquadMembers = RedisCreature().search(
        f"(@squad:{squad}) & (@squad_rank:-Pending)"
        )
    SquadPending = RedisCreature().search(
        f"(@squad:{squad}) & (@squad_rank:Pending)"
        )

    mydesc = ''
    for member in SquadMembers:
        emojiMyRace = emojiRace[member['race'] - 1]
        if member['id'] == Squad.leader:
            # This SIngouin is the leader
            title = ':first_place: Leader'
        else:
            title = ':second_place: Member'
        level = f"(lvl:{member['level']})"
        mydesc += (
            f"{emojiMyRace} `{member['name']:<14} {level:>8}` | {title}\n"
            )

    for member in SquadPending:
        emojiMyRace = emojiRace[member['race'] - 1]
        title = ':third_place: Pending'
        level = f"(lvl:{member['level']})"
        mydesc += (
            f"{emojiMyRace} `{member['name']:<14} {level:>8}` | {title}\n"
            )

    embed = discord.Embed(
        title="Squad",
        description=mydesc,
        colour=discord.Colour.blue()
    )

    return embed
