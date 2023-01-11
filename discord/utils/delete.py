#!/usr/bin/env python3
# -*- coding: utf8 -*-
import discord
import json
import os

# Discord variables
DISCORD_TOKEN = os.environ.get("SEP_DISCORD_TOKEN")

bot = discord.Bot()


async def on_connect():
    print(f'Connected with token as: {bot.user}')
    global_commands = await bot.http.get_global_commands(bot.application_id)
    print(f'{len(global_commands)} global_commands')
    for command in global_commands:
        print(f'global_command: {json.dumps(command)}')
        # Uncomment the next line (safeguard)
        """
        await bot.http.delete_global_command(bot.application_id, command['id'])
        """

    async for guild in bot.fetch_guilds():
        guild_commands = await bot.http.get_guild_commands(bot.application_id,
                                                           guild.id)
        print(f'{len(guild_commands)} guild_commands')
        for command in guild_commands:
            print(f'guild_command: {json.dumps(command)}')
            # Uncomment the next line (safeguard)
            """
            await bot.http.delete_guild_command(bot.application_id,
                                                guild.id,
                                                command['id'])
            """

bot.on_connect = on_connect

bot.run(DISCORD_TOKEN)
