# -*- coding: utf8 -*-

import asyncio
import discord
import os

from datetime import datetime
from loguru import logger
from urllib.request import ssl, socket

SSL_TARGET_HOST = os.environ.get("SSL_TARGET_HOST")
SSL_TARGET_PORT = os.environ.get("SSL_TARGET_PORT", 443)
SSL_CHANNEL     = os.environ.get("SSL_CHANNEL")
SSL_IMG_URL     = os.environ.get("SSL_IMG_URL")


async def validator(bot: discord.Client, timer: int):
    while bot.is_ready:
        if bot.user:
            try:
                context = ssl.create_default_context()

                with socket.create_connection(
                    (SSL_TARGET_HOST, SSL_TARGET_PORT)
                ) as sock:
                    with context.wrap_socket(
                        sock,
                        server_hostname=SSL_TARGET_HOST,
                    ) as ssock:
                        certificate = ssock.getpeercert()
            except Exception as e:
                logger.error(f'SSL Cert Query KO ({SSL_TARGET_HOST}:{SSL_TARGET_PORT}) [{e}]')
                continue
            else:
                logger.trace(f'SSL Cert Query OK ({SSL_TARGET_HOST}:{SSL_TARGET_PORT})')

            try:
                channel = discord.utils.get(bot.get_all_channels(), name=SSL_CHANNEL)
            except Exception as e:
                logger.error(f'Discord Channel Query KO (channel:#{SSL_CHANNEL}) [{e}]')
                continue

            try:
                cert_expires = datetime.strptime(certificate['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_left = (cert_expires - datetime.now()).days
                common_name = certificate['subject'][0][0][1]
                description = f'The SSL cert. for {common_name} expires in **{days_left}** days'

                if days_left > 15:
                    # Everything is fine
                    logger.debug(description)
                    embed = None
                elif 7 < days_left < 15:
                    # We need to do something
                    logger.warning(description)
                    embed = discord.Embed(
                        title='SSL Certificate Validator',
                        description=description,
                        colour=discord.Colour.orange()
                    )
                    embed.set_thumbnail(url=SSL_IMG_URL)
                elif days_left <= 7:
                    # We need to do something FAST
                    logger.error(description)
                    embed = discord.Embed(
                        title='SSL Certificate Validator',
                        description=description,
                        colour=discord.Colour.red()
                    )
                    embed.set_thumbnail(url=SSL_IMG_URL)
            except Exception as e:
                logger.error(f'Discord Embed KO [{e}]')
                continue
            else:
                if embed:
                    await channel.send(embed=embed)
                    logger.trace('Discord Embed OK')

        await asyncio.sleep(timer)
