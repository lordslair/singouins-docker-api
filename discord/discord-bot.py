# -*- coding: utf8 -*-

import asyncio
import discord
import inspect
import os
import re
import sys

from datetime  import datetime,timedelta
from variables import token

client = discord.Client()

@client.event
async def on_ready():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    channel = discord.utils.get(client.get_all_channels(), name='admins')

    if channel:
        answer = ':partying_face: Salutations, votre serviteur est là !'
        await channel.send(answer)

client.run(token)
