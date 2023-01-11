#!/usr/bin/env python3
# -*- coding: utf8 -*-

import discord
import os
import time

from loguru             import logger
from discord.commands   import option
from discord.ext        import commands
from random             import randint

from utils.embeds.auction import (
    embed_auction_remove,
    embed_auction_search,
    embed_auction_sell,
    )
from utils.embeds.godmode import (
    embed_godmode_kill,
    embed_godmode_give,
    embed_godmode_spawn,
    embed_godmode_take,
    embed_godmode_reset,
    )
from utils.embeds.mysingouin import (
    embed_mysingouin_equipement,
    embed_mysingouin_korp,
    embed_mysingouin_pa,
    embed_mysingouin_list,
    embed_mysingouin_highscores,
    embed_mysingouin_squad,
    embed_mysingouin_stats,
    embed_mysingouin_wallet,
    )
from utils.embeds.user import (
    embed_user_grant,
    embed_user_link,
    )
from utils.functions import (
    get_auctioned_item_list,
    get_monsters_in_instance_list,
    get_instances_list,
    get_metanames_list,
    get_monster_race_list,
    get_rarity_item_list,
    get_rarity_monsters_list,
    get_singouins_list,
    get_singouins_in_instance_list,
    get_singouin_auctionable_item_list,
    get_singouin_auctioned_item_list,
    get_singouin_inventory_item_list,
    )
from utils.k8s import (
    get_k8s_pod_list,
    k8s_backup_logs,
    k8s_deployer,
    k8s_status,
    )
from utils.views        import buyView, killView

# Log Internal imports
logger.info('Imports OK')

# Discord variables
DISCORD_GUILD = os.environ.get("SEP_DISCORD_GUILD", None)
DISCORD_TOKEN = os.environ.get("SEP_DISCORD_TOKEN")

# Log Internal imports
logger.info('Internal ENV vars loading OK')
logger.debug(f'DISCORD_GUILD:{DISCORD_GUILD}')

try:
    if DISCORD_GUILD:
        bot = discord.Bot(debug_guilds=[DISCORD_GUILD])
    else:
        bot = discord.Bot()
except Exception as e:
    logger.error(f'Discord connection KO [{e}]')
else:
    logger.info('Discord connection OK')


@bot.event
async def on_ready():
    try:
        channel = discord.utils.get(bot.get_all_channels(), name='singouins')
    except Exception as e:
        logger.error(f'Discord on_ready KO [{e}]')
    else:
        if channel:
            logger.info(f'Discord on_ready OK ({bot.user})')


# Additionnal error detector to answer properly
@bot.event
async def on_application_command_error(ctx, error):
    """Inform user of errors."""
    if isinstance(error, discord.ext.commands.NoPrivateMessage):
        await ctx.respond(
            "Sorry, this can't be done in DMs.",
            ephemeral=True
            )
    elif isinstance(error, discord.ext.commands.MissingPermissions):
        await ctx.respond(
            "Sorry, you don't have permission to do this.",
            ephemeral=True
            )
    elif isinstance(error, discord.ext.commands.CommandNotFound):
        await ctx.respond(
            "Sorry, unable to find the proper interaction.",
            ephemeral=True
            )
    else:
        raise error


#
# /auction Commands (for @Singouins)
#

try:
    group_name     = 'auction'
    group_auction  = bot.create_group(
        description="Commands related to Auction House usage",
        name=group_name,
        )
except Exception as e:
    logger.error(f'Group KO ({group_name}) [{e}]')
else:
    logger.debug(f'Group OK ({group_name})')


@group_auction.command(
    description='[@Singouins role] Sell an item in the Auction House',
    default_permission=False,
    name='sell',
    )
@option(
    "singouinuuid",
    description="Singouin UUID",
    autocomplete=get_singouins_list
    )
@option(
    "itemuuid",
    description="Item UUID",
    autocomplete=get_singouin_auctionable_item_list
    )
@option(
    "price",
    description="Price"
    )
async def sell(
    ctx: discord.ApplicationContext,
    singouinuuid: str,
    itemuuid: str,
    price: int,
):

    name = ctx.author.name
    # Pre-flight checks
    if ctx.channel.type is discord.ChannelType.private:
        channel = ctx.channel.type
    else:
        channel = ctx.channel.name

    logger.info(
        f'[#{channel}][{name}] '
        f'/auction sell {singouinuuid} {itemuuid} {price}'
        )

    try:
        embed = embed_auction_sell(singouinuuid, itemuuid, price)
    except Exception as e:
        logger.error(f'[#{channel}][{name}] └──> Auction Query KO [{e}]')
    else:
        if embed:
            logger.info(f'[#{channel}][{name}] └──> Auction Query OK')
        else:
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO')
            embed = discord.Embed(
                description='Command aborted: Auction Query KO',
                colour=discord.Colour.red()
            )
        await ctx.respond(embed=embed)
        return


@group_auction.command(
    description='[@Singouins role] Remove an item from the Auction House',
    default_permission=False,
    name='remove',
    )
@option(
    "singouinuuid",
    description="Singouin ID",
    autocomplete=get_singouins_list
    )
@option(
    "metatype",
    description="Item Type",
    autocomplete=discord.utils.basic_autocomplete(
        [
            discord.OptionChoice("Armor", value='armor'),
            discord.OptionChoice("Weapon", value='weapon'),
            ]
        )
    )
@option(
    "itemuuid",
    description="Item UUID",
    autocomplete=get_singouin_auctioned_item_list
    )
async def remove(
    ctx: discord.ApplicationContext,
    singouinuuid: str,
    metatype: str,
    itemuuid: str,
):

    name = ctx.author.name
    # Pre-flight checks
    if ctx.channel.type is discord.ChannelType.private:
        channel = ctx.channel.type
    else:
        channel = ctx.channel.name

    logger.info(
        f'[#{channel}][{name}] /auction '
        f'remove {singouinuuid} {itemuuid}'
        )

    try:
        embed = embed_auction_remove(singouinuuid, itemuuid)
    except Exception as e:
        logger.error(f'[#{channel}][{name}] └──> Auction Query KO [{e}]')
    else:
        if embed:
            logger.info(f'[#{channel}][{name}] └──> Auction Query OK')
            await ctx.respond(embed=embed)
            return
        else:
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO')
            embed = discord.Embed(
                description='Command aborted: Auction Query KO',
                colour=discord.Colour.red()
            )
            await ctx.respond(embed=embed)
            return


@group_auction.command(
    description='[@Singouins role] Buy an item in the Auction House',
    default_permission=False,
    name='buy',
    )
@option(
    "singouinuuid",
    description="Singouin UUID",
    autocomplete=get_singouins_list
    )
@option(
    "metatype",
    description="Item Type",
    autocomplete=discord.utils.basic_autocomplete(
        [
            discord.OptionChoice("Armor", value='armor'),
            discord.OptionChoice("Weapon", value='weapon'),
            ]
        )
    )
@option(
    "itemuuid",
    description="Item UUID",
    autocomplete=get_auctioned_item_list
    )
async def buy(
    ctx: discord.ApplicationContext,
    singouinuuid: str,
    metatype: str,
    itemuuid: str,
):

    name = ctx.author.name
    # Pre-flight checks
    if ctx.channel.type is discord.ChannelType.private:
        channel = ctx.channel.type
    else:
        channel = ctx.channel.name

    logger.info(
        f'[#{channel}][{name}] '
        f'/auction buy {singouinuuid} {itemuuid}'
        )

    try:
        view = buyView(ctx, singouinuuid, itemuuid)
        embed = discord.Embed(
            title='Aknowledgement required',
            description=(
                'Are you sure you really want to buy this item ?\n'
                '-> Currency will be removed from your Wallet\n'
                '-> Item will be added to your Inventory'
                ),
            colour=discord.Colour.blue()
        )
        await ctx.respond(embed=embed,
                          view=view)
    except Exception as e:
        logger.error(f'[#{channel}][{name}] └──> Auction View KO [{e}]')
        embed = discord.Embed(
            description='Command aborted: Auction Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return
    else:
        logger.info(f'[#{channel}][{name}] └──> Auction View OK')
        return


@group_auction.command(
    description='[@Singouins role] Search an item in the Auction House',
    default_permission=False,
    name='search',
    )
@option(
    "metatype",
    description="Item Type",
    autocomplete=discord.utils.basic_autocomplete(
        [
            discord.OptionChoice("Armor", value='armor'),
            discord.OptionChoice("Weapon", value='weapon'),
            ]
        )
    )
@option(
    "metaname",
    description="Item Name",
    autocomplete=discord.utils.basic_autocomplete(get_metanames_list),
    required=False,
    )
async def search(
    ctx: discord.ApplicationContext,
    metatype: str,
    metaname: str,
):

    name = ctx.author.name
    # Pre-flight checks
    if ctx.channel.type is discord.ChannelType.private:
        channel = ctx.channel.type
    else:
        channel = ctx.channel.name

    logger.info(
        f'[#{channel}][{name}] '
        f'/auction search {metatype} {metaname}'
        )

    try:
        embed = embed_auction_search(metatype, metaname)
    except Exception as e:
        logger.error(f'[#{channel}][{name}] ├──> Auction Query KO [{e}]')
    else:
        if embed:
            logger.info(f'[#{channel}][{name}] ├──> Auction Query OK')
            await ctx.respond(embed=embed)
            return
        else:
            logger.info(f'[#{channel}][{name}] └──> Auction Query KO')
            embed = discord.Embed(
                description='Command aborted: Auction Query KO',
                colour=discord.Colour.red()
            )
            await ctx.respond(embed=embed)
            return


#
# /godmode Commands (for @Admins)
#
try:
    group_name     = 'godmode'
    group_singouin = bot.create_group(
        description="Commands related to being THE almighty",
        name=group_name,
        )
except Exception as e:
    logger.error(f'Group KO ({group_name}) [{e}]')
else:
    logger.debug(f'Group OK ({group_name})')


@group_singouin.command(
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
    name    = ctx.author.name
    channel = ctx.channel.name
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{channel}][{name}] '
        f'/{group_name} spawn {monster} {instanceuuid}'
        )

    embed = embed_godmode_spawn(
        bot,
        ctx,
        monster,
        instanceuuid,
        posx,
        posy,
        rarity,
        )
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Monster spawn query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Monster spawn sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Monster spawn query KO')
        embed = discord.Embed(
            description='Spawn Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Team role] Kill a Monster',
    default_permission=False,
    name='depop',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "instanceuuid",
    description="Instance UUID",
    autocomplete=get_instances_list
    )
@option(
    "creatureuuid",
    description="Creature UUID",
    autocomplete=get_monsters_in_instance_list
    )
async def depop(
    ctx,
    instanceuuid: str,
    creatureuuid: str,
):
    name    = ctx.author.name
    channel = ctx.channel.name
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{channel}][{name}] '
        f'/{group_name} spawn {instanceuuid} {creatureuuid}'
        )

    embed = embed_godmode_kill(bot, ctx, creatureuuid, instanceuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Monster kill query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Monster kill sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Monster kill query KO')
        embed = discord.Embed(
            description='Kill Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Team role] Loot an Item to a Singouin',
    default_permission=False,
    name='give',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "instanceuuid",
    description="Instance UUID",
    autocomplete=get_instances_list
    )
@option(
    "singouinuuid",
    description="Singouin UUID",
    autocomplete=get_singouins_in_instance_list
    )
@option(
    "rarity",
    description="Item Rarity",
    autocomplete=get_rarity_item_list
    )
@option(
    "metatype",
    description="Item Type",
    autocomplete=discord.utils.basic_autocomplete(
        [
            discord.OptionChoice("Armor", value='armor'),
            discord.OptionChoice("Weapon", value='weapon'),
            ]
        )
    )
@option(
    "metaid",
    description="Item Name",
    autocomplete=get_metanames_list,
    )
async def give(
    ctx,
    instanceuuid: str,
    singouinuuid: str,
    rarity: str,
    metatype: str,
    metaid: int,
):
    name    = ctx.author.name
    channel = ctx.channel.name
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{channel}][{name}] '
        f'/{group_name} give '
        f'{instanceuuid} {singouinuuid} {rarity} {metatype} {metaid}'
        )

    embed = embed_godmode_give(
        bot,
        ctx,
        singouinuuid,
        metatype,
        metaid,
        rarity,
        )
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin give query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin give sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin give query KO')
        embed = discord.Embed(
            description='Loot Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Team role] Take an Item from a Singouin',
    default_permission=False,
    name='take',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "instanceuuid",
    description="Instance UUID",
    autocomplete=get_instances_list
    )
@option(
    "singouinuuid",
    description="Singouin UUID",
    autocomplete=get_singouins_in_instance_list
    )
@option(
    "itemuuid",
    description="Item UUID",
    autocomplete=get_singouin_inventory_item_list
    )
async def take(
    ctx,
    instanceuuid: str,
    singouinuuid: str,
    itemuuid: str,
):
    name    = ctx.author.name
    channel = ctx.channel.name
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{channel}][{name}] '
        f'/{group_name} take '
        f'{instanceuuid} {singouinuuid} {itemuuid}'
        )

    embed = embed_godmode_take(bot, ctx, singouinuuid, itemuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin give query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin give sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin give query KO')
        embed = discord.Embed(
            description='Loot Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Team role] Reset Action Points for a Singouin',
    default_permission=False,
    name='reset',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "instanceuuid",
    description="Instance UUID",
    autocomplete=get_instances_list
    )
@option(
    "singouinuuid",
    description="Singouin UUID",
    autocomplete=get_singouins_in_instance_list
    )
async def reset(
    ctx,
    instanceuuid: str,
    singouinuuid: str,
):
    name    = ctx.author.name
    channel = ctx.channel.name
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{channel}][{name}] '
        f'/{group_name} reset '
        f'{instanceuuid} {singouinuuid}'
        )

    embed = embed_godmode_reset(bot, ctx, singouinuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin give query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin give sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin give query KO')
        embed = discord.Embed(
            description='Loot Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


#
# /infra Commands (for @Admins)
#
try:
    group_name     = 'infra'
    group_singouin = bot.create_group(
        description="Commands related to Infrastructure management",
        name=group_name,
        )
except Exception as e:
    logger.error(f'Group KO ({group_name}) [{e}]')
else:
    logger.debug(f'Group OK ({group_name})')


@group_singouin.command(
    description='[@Team role] Display backup information',
    default_permission=False,
    name='backup',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "env",
    description="Target environment",
    choices=['dev', 'prod'],
    )
@option(
    "action",
    description="Action to execute",
    choices=['status'],
    )
async def backup(
    ctx,
    env: str,
    action: str,
):
    # As the API takes is so dams slow, we need more time to answer
    await ctx.defer()
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{ctx.channel.name}][{ctx.channel.name}] '
        f'/{group_name} backup {env}'
        )

    try:
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> K8s Query Starting'
            )
        if action == 'status':
            exec_stdout = k8s_backup_logs(env)
        logger.debug(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> K8s Query Ended'
            )
    except Exception as e:
        logger.error(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'└──> K8s Query KO [{e}]'
            )
        embed = discord.Embed(
            description='Command aborted: K8s Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return
    else:
        # We got the logs, we can start working
        embed = discord.Embed(
            title=f'K8s backup status [{env}]',
            description=f'```{exec_stdout}```',
            colour=discord.Colour.green()
        )
        await ctx.interaction.edit_original_response(embed=embed)

    logger.info(
        f'[#{ctx.channel.name}][{ctx.author.name}] '
        f'└──> K8s Query OK'
        )
    return


@group_singouin.command(
    description='[@Team role] Deploy latest Front build',
    default_permission=False,
    name='deploy',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "env",
    description="Target environment",
    choices=['dev', 'prod'],
    )
async def deploy(
    ctx,
    env: str,
):
    # As the API takes is so dams slow, we need more time to answer
    await ctx.defer()
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{ctx.channel.name}][{ctx.channel.name}] '
        f'/{group_name} deploy {env}'
        )

    try:
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> K8s Query Starting'
            )
        exec_stdout = k8s_deployer(env)
        logger.debug(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> K8s Query Ended'
            )
    except Exception as e:
        logger.error(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'└──> K8s Query KO [{e}]'
            )
        embed = discord.Embed(
            description='Command aborted: K8s Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return
    else:
        # We got the logs, we can start working
        embed = discord.Embed(
            title=f'K8s deploy status [{env}]',
            description=f'```{exec_stdout}```',
            colour=discord.Colour.green()
        )
        await ctx.interaction.edit_original_response(embed=embed)

    logger.info(
        f'[#{ctx.channel.name}][{ctx.author.name}] '
        f'└──> K8s Query OK'
        )
    return


@group_singouin.command(
    description='[@Team role] Display Infra status',
    default_permission=False,
    name='status',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "env",
    description="Target environment",
    choices=['dev', 'prod'],
    )
@option(
    "verbose",
    description="--verbose",
    choices=['True', 'False'],
    required=False,
    default='False',
    )
async def status(
    ctx,
    env: str,
    verbose: str,
):
    # As the API takes is so dams slow, we need more time to answer
    await ctx.defer()
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{ctx.channel.name}][{ctx.channel.name}] '
        f'/{group_name} status {env} --verbose={verbose}'
        )

    try:
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> K8s Query Starting'
            )
        pods = k8s_status(env, verbose)
        logger.debug(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> K8s Query Ended'
            )
    except Exception as e:
        logger.error(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'└──> K8sKill View KO [{e}]'
            )
        embed = discord.Embed(
            description='Command aborted: K8s Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return

    # We got the pod object, we can start working
    description = ''
    embed = discord.Embed(
        title=f'K8s status [{env}]',
        description=description,
        colour=discord.Colour.green()
    )
    # We Start to update the Embed
    await ctx.interaction.edit_original_response(embed=embed)
    # We loop over pods to have detailed infos
    for pod in pods.items:
        # We skip CronJob generated pods
        if 'job-name' in pod.metadata.labels:
            continue
        # We fetch the POD name and format it
        app_name = pod.metadata.labels['name'].title()
        if verbose == 'True':
            app_status = ''
        else:
            if pod.status.phase == 'Running':
                app_status = '🟢'
            else:
                app_status = '🔴'
        description += f"{app_status} {app_name}\n"
        logger.trace(f"{app_status} {app_name}")

        # We fetch the container(s) name and format it
        if verbose == 'True':
            for container in pod.status.container_statuses:
                container_name = container.name
                container_name.removeprefix('sep-backend-')
                if container.ready:
                    container_status = '🟢'
                else:
                    container_status = '🔴'
                logger.trace(f"> {container_status} {container_name} "
                             f"({container.restart_count})")
                description += (
                    f"> {container_status} {container_name} "
                    f"({container.restart_count})\n"
                    )

        # We update the Embed with the pod result
        embed = discord.Embed(
            title=f'K8s status [{env}]',
            description=description,
            colour=discord.Colour.green()
            )
        await ctx.interaction.edit_original_response(embed=embed)

    logger.info(
        f'[#{ctx.channel.name}][{ctx.author.name}] '
        f'└──> K8s Query OK'
        )
    return


@group_singouin.command(
    description='[@Team role] Kill an Infra POD',
    default_permission=False,
    name='kill',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
@commands.has_any_role('Team')
@option(
    "env",
    description="Target environment",
    choices=['dev', 'prod'],
    )
@option(
    "pod",
    description="Pod",
    autocomplete=get_k8s_pod_list
    )
async def kill(
    ctx,
    env: str,
    pod: str,
):
    # As we need roles, it CANNOT be used in PrivateMessage
    logger.info(
        f'[#{ctx.channel.name}][{ctx.channel.name}] '
        f'/{group_name} kill {env} {pod}'
        )

    try:
        view = killView(ctx, env, pod)

        embed = discord.Embed(
            title='Aknowledgement required',
            description=f'Do you want to kill `{pod}`',
            colour=discord.Colour.blue()
        )
        await ctx.respond(embed=embed,
                          view=view)
    except Exception as e:
        logger.error(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'└──> K8sKill View KO [{e}]'
            )
        embed = discord.Embed(
            description='Command aborted: K8s Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return
    else:
        logger.info(
            f'[#{ctx.channel.name}][{ctx.channel.name}] '
            f'└──> K8sKill View OK'
            )
        return


#
# /mysingouin Commands (for @Singouins)
#
try:
    group_name     = 'mysingouin'
    group_singouin = bot.create_group(
        description="Commands related to Singouins",
        name=group_name,
        )
except Exception as e:
    logger.error(f'Group KO ({group_name}) [{e}]')
else:
    logger.debug(f'Group OK ({group_name})')


@group_singouin.command(
    description='[@Singouins role] Display your Singouin Equipped items',
    default_permission=False,
    name='equipment',
    )
@commands.has_any_role('Singouins', 'Team')
@option(
    "singouinuuid",
    description="Singouin ID",
    autocomplete=get_singouins_list
    )
async def equipment(
    ctx,
    singouinuuid: str,
):
    name         = ctx.author.name
    channel      = ctx.channel.name
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(
            f'[#{channel}][{name}] /mysingouin equipment '
            f'<{singouinuuid}> [Admin user]'
            )
    else:
        logger.info(
            f'[#{channel}][{name}] /mysingouin equipment '
            f'<{singouinuuid}> [Singouin user]'
            )

    embed = embed_mysingouin_equipement(bot, singouinuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin Equipment query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin Equipment sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin Equipment query KO')
        embed = discord.Embed(
            description='Equipment get KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


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
    name         = ctx.author.name
    channel      = ctx.channel.name
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(
            f'[#{channel}][{name}] /singouins hs '
            f'<{singouinuuid}> [Admin user]'
            )
    else:
        logger.info(
            f'[#{channel}][{name}] /singouins hs '
            f'<{singouinuuid}> [Singouin user]'
            )

    embed = embed_mysingouin_highscores(bot, singouinuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin hs query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin hs sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin hs query KO')
        embed = discord.Embed(
            description='HighScores Query KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Singouins role] Display your Singouin Korp',
    default_permission=False,
    name='korp',
    )
@commands.has_any_role('Singouins', 'Team')
@option(
    "singouinuuid",
    description="Singouin ID",
    autocomplete=get_singouins_list
    )
async def korp(
    ctx,
    singouinuuid: str,
):
    name         = ctx.author.name
    channel      = ctx.channel.name
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(
            f'[#{channel}][{name}] /singouins korp '
            f'<{singouinuuid}> [Admin user]'
            )
    else:
        logger.info(
            f'[#{channel}][{name}] /singouins korp '
            f'<{singouinuuid}> [Singouin user]'
            )

    embed = embed_mysingouin_korp(bot, singouinuuid)

    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin Korp query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin Korp sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin Korp query KO')
        embed = discord.Embed(
            description='Korp get KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Singouins role] Display your Singouin(s) informations',
    default_permission=False,
    name='list',
    )
@commands.has_any_role('Singouins', 'Team')
async def list(
    ctx,
):
    name         = ctx.author.name
    channel      = ctx.channel.name
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(f'[#{channel}][{name}] /mysingouin list [Admin user]')
    else:
        logger.info(f'[#{channel}][{name}] /mysingouin list [Singouin user]')

    embed = embed_mysingouin_list(bot, ctx)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin list query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin list sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin list query KO')
        embed = discord.Embed(
            description='Korp get KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Singouins role] Display your Singouin Action Points (PA)',
    default_permission=False,
    name='pa',
    )
@commands.has_any_role('Singouins', 'Team')
@option(
    "singouinuuid",
    description="Singouin ID",
    autocomplete=get_singouins_list
    )
async def pa(
    ctx,
    singouinuuid: str,
):
    name         = ctx.author.name
    channel      = ctx.channel.name
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(
            f'[#{channel}][{name}] /mysingouin pa '
            f'<{singouinuuid}> [Admin user]'
            )
    else:
        logger.info(
            f'[#{channel}][{name}] /mysingouin pa '
            f'<{singouinuuid}> [Singouin user]'
            )

    embed = embed_mysingouin_pa(bot, singouinuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin PA query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin PA sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin PA query KO')
        embed = discord.Embed(
            description='PA get KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


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
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(
            f'[#{channel}][{name}] /singouins squad '
            f'<{singouinuuid}> [Admin user]'
            )
    else:
        logger.info(
            f'[#{channel}][{name}] /singouins squad '
            f'<{singouinuuid}> [Singouin user]'
            )

    embed = embed_mysingouin_squad(bot, singouinuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin Squad query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin Squad sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin Squad query KO')
        embed = discord.Embed(
            description='Squad get KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Singouins role] Display your Singouin Stats',
    default_permission=False,
    name='stats',
    )
@commands.has_any_role('Singouins', 'Team')
@option(
    "singouinuuid",
    description="Singouin ID",
    autocomplete=get_singouins_list
    )
async def stats(
    ctx,
    singouinuuid: str,
):
    name         = ctx.author.name
    channel      = ctx.channel.name
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(
            f'[#{channel}][{name}] /mysingouin stats '
            f'<{singouinuuid}> [Admin user]'
            )
    else:
        logger.info(
            f'[#{channel}][{name}] /mysingouin stats '
            f'<{singouinuuid}> [Singouin user]'
            )

    embed = embed_mysingouin_stats(bot, singouinuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin Stats query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin Stats sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin Stats query KO')
        embed = discord.Embed(
            description='Stats get KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@Singouins role] Display your Singouin Wallet',
    default_permission=False,
    name='wallet',
    )
@commands.has_any_role('Singouins', 'Team')
@option(
    "singouinuuid",
    description="Singouin ID",
    autocomplete=get_singouins_list
    )
async def wallet(
    ctx,
    singouinuuid: str,
):
    name         = ctx.author.name
    channel      = ctx.channel.name
    adminrole    = discord.utils.get(ctx.author.guild.roles, name='Team')

    # Pre-flight checks : Roles
    if adminrole in ctx.author.roles:
        # As admin, we don't check if we own the Creature or not
        logger.info(
            f'[#{channel}][{name}] /mysingouin wallet '
            f'<{singouinuuid}> [Admin user]'
            )
    else:
        logger.info(
            f'[#{channel}][{name}] /mysingouin wallet '
            f'<{singouinuuid}> [Singouin user]'
            )

    embed = embed_mysingouin_wallet(bot, singouinuuid)
    if embed:
        logger.info(f'[#{channel}][{name}] ├──> Singouin Wallet query OK')
        await ctx.respond(embed=embed)
        logger.info(f'[#{channel}][{name}] └──> Singouin Wallet sent')
    else:
        logger.info(f'[#{channel}][{name}] └──> Singouin Wallet query KO')
        embed = discord.Embed(
            description='Wallet get KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


#
# /uer Commands (for @everyone)
#
try:
    group_name     = 'user'
    group_singouin = bot.create_group(
        description="Commands related to Users/Players",
        name=group_name,
        )
except Exception as e:
    logger.error(f'Group KO ({group_name}) [{e}]')
else:
    logger.debug(f'Group OK ({group_name})')


@group_singouin.command(
    description='[@everyone] Update your Discord roles (Squad/Korp)',
    default_permission=False,
    name='grant',
    )
@commands.guild_only()  # Hides the command from the menu in DMs
async def grant(
    ctx,
):
    logger.info(
        f'[#{ctx.channel.name}][{ctx.author.name}] '
        f'/{group_name} grant'
        )

    embed = await embed_user_grant(bot, ctx)
    if embed:
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'├──> Query OK'
            )
        await ctx.respond(embed=embed)
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'└──> Answer sent'
            )
    else:
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'└──> Query KO'
            )
        embed = discord.Embed(
            description='User Singouins grant KO',
            colour=discord.Colour.red()
        )
        await ctx.respond(embed=embed)
        return


@group_singouin.command(
    description='[@everyone] Link your Singouin with Discord',
    name='link',
    )
@option(
    "mail",
    description="User mail adress (The one used in the game)",
    )
async def link(
    ctx,
    mail: str,
):
    # Pre-flight checks
    if ctx.channel.type is discord.ChannelType.private:
        logger.info(
            f'[#{ctx.channel.type}][{ctx.author.name}] '
            f'/{group_name} link <{mail}>'
            )
        # We are in a private DMChannel
        try:
            embed = embed_user_link(bot, ctx, mail)
        except Exception as e:
            logger.error(
                f'[#{ctx.channel.type}][{ctx.author.name}] '
                f'└──> Embed KO [{e}]'
                )
        else:
            if embed:
                logger.info(
                    f'[#{ctx.channel.type}][{ctx.author.name}] '
                    f'├──> Query OK'
                    )
                await ctx.respond(embed=embed)
                logger.info(
                    f'[#{ctx.channel.type}][{ctx.author.name}] '
                    f'└──> Answer sent'
                    )
            else:
                logger.info(
                    f'[#{ctx.channel.type}][{ctx.author.name}] '
                    f'└──> Query KO'
                    )
                embed = discord.Embed(
                    description='User Singouins register KO',
                    colour=discord.Colour.red()
                )
                await ctx.respond(embed=embed)
                return
    else:
        logger.info(
            f'[#{ctx.channel.name}][{ctx.author.name}] '
            f'/{group_name} link <{mail}>'
            )
        try:
            embed = discord.Embed(
                description=(
                    f':information_source: You tried to register '
                    f'your account here on the channel `#{ctx.channel.name}`\n'
                    f'---\n'
                    f'Go to {bot.user.mention} Private Messages to avoid '
                    f'showing publicly your email & retry the command there\n'
                    f'The bot should have sent you a PM right now\n'
                    f'---\n'
                    f'This message will be discarded automatically\n'
                ),
                colour=discord.Colour.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            embed = discord.Embed(
                description=(
                    f':information_source: You tried to register '
                    f'your account on the channel `#{ctx.channel.name}`\n'
                    f'---\n'
                    f'But it will be better to do that here :smiley: \n'
                    f'---\n'
                    f'You can safely use the command `/user link` here\n'
                ),
                colour=discord.Colour.green()
            )
            await ctx.author.send(embed=embed)
        except Exception as e:
            await ctx.respond(f'[{e}]')
        else:
            return

# Run Discord bot
iter = 0
while iter < 5:
    try:
        bot.run(DISCORD_TOKEN)
        break
    except Exception as e:
        logger.error(f'Discord bot.run KO (Attempt: {iter+1}/5) [{e}]')
        iter += 1
        time.sleep(5)
        continue
