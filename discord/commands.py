#!/usr/bin/env python3
# -*- coding: utf8 -*-

import discord
import os
import time

from loguru             import logger

from subcommands import (
    auction,
    infra,
    godmode,
    singouin,
    user,
    )

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
    group_auction  = bot.create_group(
        description="Commands related to Auction House usage",
        name='auction',
        )
except Exception as e:
    logger.error(f'[{group_auction}] Command Group KO [{e}]')
else:
    logger.debug(f'[{group_auction}] Command Group OK')
    auction.buy(group_auction)
    auction.remove(group_auction)
    auction.search(group_auction, bot)
    auction.sell(group_auction)
    auction.show(group_auction, bot)
    logger.debug(f'[{group_auction}] Commands OK')
#
# /godmode Commands (for @Admins)
#
try:
    group_name     = 'godmode'
    group_godmode = bot.create_group(
        description="Commands related to being THE almighty",
        name=group_name,
        )
except Exception as e:
    logger.error(f'[{group_name}] Command Group KO [{e}]')
else:
    logger.debug(f'[{group_name}] Command Group OK')
    godmode.depop(group_godmode)
    godmode.give(group_godmode)
    godmode.pop(group_godmode)
    godmode.take(group_godmode)
    godmode.reset(group_godmode)
    logger.debug(f'[{group_name}] Commands OK')
#
# /infra Commands (for @Admins)
#
try:
    group_name     = 'infra'
    group_admin = bot.create_group(
        description="Commands related to Infrastructure management",
        name=group_name,
        )
except Exception as e:
    logger.error(f'[{group_name}] Command Group KO [{e}]')
else:
    logger.debug(f'[{group_name}] Command Group OK')
    infra.backup(group_admin)
    infra.deploy(group_admin)
    infra.kill(group_admin)
    infra.log(group_admin)
    infra.status(group_admin)
    logger.debug(f'[{group_name}] Commands OK')
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
    logger.error(f'[{group_name}] Command Group KO [{e}]')
else:
    logger.debug(f'[{group_name}] Command Group OK')
    singouin.equipment(group_singouin)
    singouin.highscores(group_singouin, bot)
    singouin.inventory(group_singouin)
    singouin.korp(group_singouin, bot)
    singouin.pa(group_singouin)
    singouin.show(group_singouin, bot)
    singouin.squad(group_singouin, bot)
    singouin.stats(group_singouin, bot)
    singouin.wallet(group_singouin, bot)
    logger.debug(f'[{group_name}] Commands OK')
#
# /user Commands (for @everyone)
#
try:
    group_name = 'user'
    group_user = bot.create_group(
        description="Commands related to Users/Players",
        name=group_name,
        )
except Exception as e:
    logger.error(f'[{group_name}] Command Group KO ({group_name}) [{e}]')
else:
    logger.debug(f'[{group_name}] Command Group OK')
    user.grant(group_user, bot)
    user.link(group_user, bot)
    logger.debug(f'[{group_name}] Commands OK')


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
