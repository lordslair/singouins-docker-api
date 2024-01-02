#!/usr/bin/env python3
# -*- coding: utf8 -*-

import asyncio
import discord
import os
import re
import time

from loguru                     import logger

from nosql.metas                import metaNames
from nosql.queue                import yqueue_get

from nosql.models.RedisSearch   import RedisSearch

from variables import (
    rarity_item_types_discord,
    rarity_item_types_integer,
    )

# Log Internal imports
logger.info('Imports OK')

URL_ASSETS    = os.environ.get("SEP_URL_ASSETS")
DISCORD_TOKEN = os.environ.get("SEP_DISCORD_TOKEN")
YQ_DISCORD    = os.environ.get("SEP_YQ_DISCORD", 'yarqueue:discord')

# Log Internal imports
logger.info('Internal ENV vars loading OK')

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

#
# Tasks definition
#


async def yqueue_check(timer):
    while bot.is_ready:
        if bot.user:
            # Opening Queue
            msgs = yqueue_get(YQ_DISCORD)

            if msgs is None:
                # If no msgs are received, GOTO next loop
                logger.debug('Message Queue KO - GOTO next loop')
                continue

            if len(msgs) == 0:
                logger.debug('Message Queue OK - But empty')
            else:
                logger.debug('Message Queue OK')
                msgs.reverse()

            for msg in msgs:
                logger.debug(f'Message type {type(msg)} Received {msg}')
                if msg['payload'] is None:
                    """
                    We are reading a WEIRD message
                    -> We don't do anything
                    """
                    logger.trace(f'Message skipped ({msg}) - No Payload')
                    continue
                else:
                    pass

                if msg['scope'] is None:
                    """
                    We DO NOT HAVE have a Scope
                    -> We don't do anything
                    """
                    logger.trace(f'Message skipped ({msg}) - No Scope')
                    continue
                else:
                    pass

                if msg['embed'] is None:
                    """
                    We are reading a STANDARD message
                    -> We prepare to send
                    """
                    answer = msg['payload']
                    embed  = msg['embed']
                elif msg['payload']['winner'] and msg['payload']['item']:
                    """
                    We are reading a LOOT message
                    -> We prepare to send
                    """

                    item       = msg['payload']['item']

                    winner     = msg['payload']['winner']
                    winnerid   = winner['id']
                    winnername = winner['name']

                    try:
                        id = winner['id'].replace('-', ' ')
                        Users = RedisSearch().user(query=f'@id:{id}')
                    except Exception as e:
                        logger.error(
                            f'User Query KO (winnerid:{winnerid}) [{e}]'
                            )
                        continue
                    else:
                        User = Users.results[0]
                        logger.debug(
                            f'User Query OK (winnerid:{winnerid})'
                            )

                    if User.d_name:
                        # The Singouin who looted is linked on Discord
                        logger.trace(f"Discord Name (d_name:{User.d_name})")
                        (name, discriminator) = User.d_name.split('#')
                        # The loot winner has a registered Discord Acc
                        discorduser = discord.utils.get(
                            bot.get_all_members(),
                            name=name,
                            discriminator=discriminator
                            )
                        # We add that info into the proper var
                        if discorduser:
                            logger.debug(
                                f'Discord User Query OK '
                                f'(discorduser:{discorduser})'
                                )
                            header = (
                                f'{discorduser.mention} (**{winnername}**) '
                                f'looted that !'
                                )
                        else:
                            header = f'Somebody ({winnername}) looted that !'
                            logger.warning('Discord User Query KO - NotFound')
                    else:
                        # The Singouin who looted is NOT linked on Discord
                        header = f'Somebody ({winnername}) looted that !'
                        logger.debug('User Not Linked - Cannot @tag him')

                    answer = None
                    embed  = discord.Embed(
                        color=rarity_item_types_integer[item['rarity']]
                        )

                    embed_field_name = (
                        f"{rarity_item_types_discord[item['rarity']]} "
                        f"{metaNames[item['metatype']][item['metaid']]}"
                        )

                    embed_field_value  = (
                        f"> Bound : `{item['bound']} ({item['bound_type']})`\n"
                        )
                    embed_field_value += f"> State : `{item['state']}`\n"
                    embed_field_value += (
                        f"> Bearer : `UUID({item['bearer']})`\n"
                        )

                    if item['ammo'] is not None:
                        embed_field_value += f"> Ammo : `{item['ammo']}`\n"

                    embed_field_value += header

                    embed.add_field(
                        name=embed_field_name,
                        value=embed_field_value,
                        inline=True,
                        )

                    URI_PNG = (
                        f"sprites/{item['metatype']}s/{item['metaid']}.png"
                        )
                    logger.debug(f"[embed.thumbnail] {URL_ASSETS}/{URI_PNG}")
                    embed.set_thumbnail(url=f"{URL_ASSETS}/{URI_PNG}")

                    embed.set_footer(text=f"ItemUUID: {item['id']}")

                else:
                    """
                    We are reading a UNKNOWN message
                    -> We don't do anything
                    """
                    logger.trace(f'Message skipped ({msg}) - Unknown')
                    continue

                try:
                    # We check if the channel exists
                    channel = discord.utils.get(
                        bot.get_all_channels(),
                        name=msg['scope'].lower()
                        )
                except Exception as e:
                    logger.error(
                        f"Channel Query KO "
                        f"(channel:{msg['scope']}) [{e}]"
                    )
                else:
                    if channel:
                        """
                        Now we have all we need
                        -> We send
                        """
                        try:
                            await channel.send(answer, embed=embed)
                        except Exception as e:
                            logger.error(
                                f'Send message KO '
                                f'(channel:{channel.name}) [{e}]'
                                )
                        else:
                            logger.info(
                                f'Send message OK '
                                f'(channel:{channel.name})'
                                )
                    else:
                        logger.warning(
                            f"Channel Query KO "
                            f"(channel:{msg['scope']}) - NotFound"
                        )

        await asyncio.sleep(timer)


async def squad_channel_cleanup(timer):
    while bot.is_ready:
        for guild in bot.guilds:
            for channel in guild.text_channels:
                m = re.search(r"^squad-(?P<squadid>[\w\-]+)", channel.name)
                if m is None:
                    continue

                # We are here if REGEX matched
                squaduuid = m.group('squadid')
                Squads = RedisSearch().squad(
                    query=f"@id:{squaduuid.replace('-', ' ')}"
                    )
                if len(Squads.results) != 0:
                    # The Squad exists so we keep the channel
                    continue

                # The squad does not exist in DB -> CLEANING
                try:
                    logger.debug(
                        f'Squad channel deletion >> '
                        f'(channel:{channel.name})'
                        )
                    await channel.delete()
                except Exception as e:
                    logger.error(
                        f'Squad channel deletion KO '
                        f'(channel:{channel.name}) [{e}]'
                        )
                else:
                    logger.info(
                        f'Squad channel deletion OK '
                        f'(channel:{channel.name})'
                        )

                # We try to delete the unused role
                try:
                    role = discord.utils.get(
                        guild.roles,
                        name=f'Squad-{squaduuid}'
                        )
                except Exception as e:
                    logger.error(
                        f'Squad role deletion KO '
                        f'(channel:{channel.name}) [{e}]'
                        )
                else:
                    if role:
                        await role.delete()
                        logger.info('Squad role deletion OK')
        await asyncio.sleep(timer)


async def squad_channel_create(timer):
    while bot.is_ready:
        for guild in bot.guilds:
            admin_role = discord.utils.get(guild.roles, name='Team')
            category   = discord.utils.get(guild.categories, name='Squads')

            try:
                Squads = RedisSearch().squad(query='-(@instance:None)')
            except Exception as e:
                logger.error(f'API Query KO [{e}]')
                continue
            else:
                # We skip the loop if no squads are returned
                if Squads is None or Squads == []:
                    logger.info('Squads Query OK - But empty')
                    continue
                else:
                    logger.trace('Squads Query OK')

            for Squad in Squads.results:
                role_name    = f"Squad-{Squad.id}"
                channel_name = role_name.lower()
                channel      = discord.utils.get(
                    bot.get_all_channels(),
                    name=channel_name
                    )
                if channel:
                    # Squad channel already exists
                    logger.debug(
                        f'Squad channel exists (channel:{channel.name})'
                        )
                    pass
                else:
                    # Squad channel do not exists
                    logger.info(
                        f'Squad channel to add (channel:{channel_name})'
                        )

                    # Check role existence
                    if discord.utils.get(guild.roles, name=role_name):
                        # Role already exists, do nothing
                        logger.info(
                            f'Squad role already exists (role:{role_name})'
                            )
                    else:
                        # Role do not exist, create it
                        try:
                            squad_role = await guild.create_role(
                                name=role_name,
                                mentionable=True,
                                permissions=discord.Permissions.none()
                                )
                        except Exception as e:
                            logger.error(
                                f'Squad role creation KO '
                                f'(role:{squad_role}) [{e}]'
                                )
                        else:
                            logger.info(
                                f'Squad role creation OK (role:{squad_role})'
                                )

                    # Create channel
                    try:
                        bot_role   = discord.utils.get(
                            guild.roles,
                            name='BOTS'
                            )
                        squad_role = discord.utils.get(
                            guild.roles,
                            name=role_name
                            )
                        overwrites = {
                            guild.default_role:
                                discord.PermissionOverwrite(
                                    read_messages=False,
                                    ),
                            guild.me:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                            admin_role:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                            squad_role:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                            bot_role:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                        }
                        mysquadchannel = await guild.create_text_channel(
                            channel_name,
                            category=category,
                            topic=None,
                            overwrites=overwrites
                            )
                    except Exception as e:
                        logger.error(
                            f'Squad channel creation KO '
                            f'(channel:{channel_name}) [{e}]'
                            )
                    else:
                        logger.info(
                            f'Squad channel creation OK '
                            f'(channel:{mysquadchannel.name})'
                            )
        await asyncio.sleep(timer)


async def korp_channel_cleanup(timer):
    while bot.is_ready:
        for guild in bot.guilds:
            for channel in guild.text_channels:
                m = re.search(r"^korp-(?P<korpid>[\w\-]+)", channel.name)
                if m is None:
                    continue

                # We are here if REGEX matched
                korpuuid = m.group('korpid')
                Korps = RedisSearch().korp(
                    query=f"@id:{korpuuid.replace('-', ' ')}"
                    )
                if len(Korps.results) != 0:
                    # The Korp exists so we keep the channel
                    continue

                # The Korp does not exist in DB -> CLEANING
                try:
                    logger.debug(
                        f'Korp channel deletion >> '
                        f'(channel:{channel.name})'
                        )
                    await channel.delete()
                except Exception as e:
                    logger.error(
                        f'Korp channel deletion KO '
                        f'(channel:{channel.name}) [{e}]'
                        )
                else:
                    logger.info(
                        f'Korp channel deletion OK '
                        f'(channel:{channel.name})'
                        )

                # We try to delete the unused role
                try:
                    role = discord.utils.get(
                        guild.roles,
                        name=f'Korp-{korpuuid}'
                        )
                except Exception as e:
                    logger.error(
                        f'Korp role deletion KO '
                        f'(channel:{channel.name}) [{e}]'
                        )
                else:
                    if role:
                        await role.delete()
                        logger.info('Korp role deletion OK')
        await asyncio.sleep(timer)


async def korp_channel_create(timer):
    while bot.is_ready:
        for guild in bot.guilds:
            admin_role = discord.utils.get(guild.roles, name='Team')
            category   = discord.utils.get(guild.categories, name='Korps')

            try:
                Korps = RedisSearch().korp(query='-(@instance:None)')
            except Exception as e:
                logger.error(f'API Query KO [{e}]')
                continue
            else:
                # We skip the loop if no korps are returned
                if Korps.results == []:
                    logger.debug('Korps Query OK - But empty')
                    continue
                else:
                    logger.trace('Korps Query OK')

            for Korp in Korps.results:
                role_name    = f"Korp-{Korp.id}"
                channel_name = role_name.lower()
                channel      = discord.utils.get(
                    bot.get_all_channels(),
                    name=channel_name,
                    )
                if channel:
                    # Korp channel already exists
                    logger.debug(
                        f'Korp channel exists (channel:{channel.name})'
                        )
                    pass
                else:
                    # Korp channel do not exists
                    logger.info(
                        f'Korp channel to add (channel:{channel_name})'
                        )

                    # Check role existence
                    if discord.utils.get(guild.roles, name=role_name):
                        # Role already exists, do nothing
                        logger.info(
                            f'Korp role already exists (role:{role_name})'
                            )
                    else:
                        # Role do not exist, create it
                        try:
                            korp_role = await guild.create_role(
                                name=role_name,
                                mentionable=True,
                                permissions=discord.Permissions.none()
                            )
                        except Exception as e:
                            logger.error(
                                f'Korp role creation KO '
                                f'(role:{korp_role}) [{e}]'
                                )
                        else:
                            logger.info(
                                f'Korp role creation OK (role:{korp_role})'
                                )

                    # Create channel
                    try:
                        bot_role   = discord.utils.get(
                            guild.roles,
                            name='BOTS'
                            )
                        korp_role = discord.utils.get(
                            guild.roles,
                            name=role_name
                            )
                        overwrites = {
                            guild.default_role:
                                discord.PermissionOverwrite(
                                    read_messages=False,
                                    ),
                            guild.me:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                            admin_role:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                            korp_role:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                            bot_role:
                                discord.PermissionOverwrite(
                                    read_messages=True,
                                    ),
                        }
                        mykorpchannel = await guild.create_text_channel(
                            channel_name,
                            category=category,
                            topic=f"<**{Korp.name}**>",
                            overwrites=overwrites,
                        )
                    except Exception as e:
                        logger.error(
                            f'Korp channel creation KO '
                            f'(channel:{channel_name}) [{e}]'
                            )
                    else:
                        logger.info(
                            f'Korp channel creation OK '
                            f'(channel:{mykorpchannel.name})'
                            )
        await asyncio.sleep(timer)


async def ssl_cert_validator(timer):
    import datetime

    from urllib.request import ssl, socket

    SSL_TARGET_HOST = os.environ.get("SEP_SSL_TARGET_HOST")
    SSL_TARGET_PORT = os.environ.get("SEP_SSL_TARGET_PORT", 443)
    SSL_CHANNEL     = os.environ.get("SEP_SSL_CHANNEL")
    SSL_IMG_URL     = os.environ.get("SEP_SSL_IMG_URL")

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
                logger.error(
                    f'SSL Cert Query KO '
                    f'({SSL_TARGET_HOST}:{SSL_TARGET_PORT}) [{e}]'
                    )
                continue
            else:
                logger.trace(
                    f'SSL Cert Query OK '
                    f'({SSL_TARGET_HOST}:{SSL_TARGET_PORT})'
                    )

            try:
                channel = discord.utils.get(
                    bot.get_all_channels(),
                    name=SSL_CHANNEL,
                    )
            except Exception as e:
                logger.error(
                    f'Discord Channel Query KO (channel:#{SSL_CHANNEL}) [{e}]'
                    )
                continue
            else:
                if channel:
                    logger.trace(
                        f'Discord Channel Query OK (channel:#{SSL_CHANNEL})'
                        )
                else:
                    logger.warning(
                        f'Discord Channel Query KO (channel:#{SSL_CHANNEL})'
                        )
                    continue

            try:
                certExpires = datetime.datetime.strptime(
                    certificate['notAfter'],
                    '%b %d %H:%M:%S %Y %Z'
                    )
                daysToExpiration = (certExpires - datetime.datetime.now()).days
                commonName = certificate['subject'][0][0][1]
                description = (
                    f'The SSL certificate for {commonName} '
                    f'will expire in **{daysToExpiration}** days'
                    )

                if daysToExpiration > 15:
                    # Everything is fine
                    logger.debug(description)
                    embed = None
                    pass
                elif 7 < daysToExpiration < 15:
                    # We need to do something
                    logger.warning(description)
                    embed = discord.Embed(
                        title='SSL Certificate Validator',
                        description=description,
                        colour=discord.Colour.orange()
                    )
                    embed.set_thumbnail(url=SSL_IMG_URL)
                elif daysToExpiration <= 7:
                    # We need to do something FAST
                    logger.error(description)
                    embed = discord.Embed(
                        title='SSL Certificate Validator',
                        description=description,
                        colour=discord.Colour.red()
                    )
                    embed.set_thumbnail(url=SSL_IMG_URL)

                if embed:
                    await channel.send(embed=embed)
            except Exception as e:
                logger.error(f'Discord Embed KO [{e}]')
                continue
            else:
                logger.trace('Discord Embed OK')

        await asyncio.sleep(timer)

# 86400s Tasks (@Daily)
bot.loop.create_task(ssl_cert_validator(86400))
# 3600s Tasks (@Hourly)
bot.loop.create_task(squad_channel_cleanup(3600))
bot.loop.create_task(korp_channel_cleanup(3600))
# 300s Tasks (@5Minutes)
bot.loop.create_task(squad_channel_create(300))
bot.loop.create_task(korp_channel_create(300))
# 60s Tasks (@1Minute)
bot.loop.create_task(yqueue_check(60))
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
