#!/usr/bin/env python3
# -*- coding: utf8 -*-

import discord

from loguru import logger

from subtasks import channels, ssl_cert, yqueue
from variables import env_vars

try:
    bot = discord.Bot(intents=discord.Intents.all())
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

# 86400s Tasks (@Daily)
if env_vars['SSL_CHECK']:
    bot.loop.create_task(ssl_cert.validator(bot, 86400))
# 3600s Tasks (@Hourly)
bot.loop.create_task(channels.create(bot, 'Squad', 300))
bot.loop.create_task(channels.cleanup(bot, 'Korp', 300))
# 300s Tasks (@5Minutes)
bot.loop.create_task(channels.create(bot, 'Korp', 300))
bot.loop.create_task(channels.create(bot, 'Squad', 300))
# 60s Tasks (@1Minute)
if env_vars['YQ_CHECK']:
    bot.loop.create_task(yqueue.check(bot, 60))

# Run Discord bot
try:
    logger.debug('Discord bot.run >>')
    bot.run(env_vars['DISCORD_TOKEN'])
except Exception as e:
    logger.error(f'Discord bot.run KO [{e}]')
