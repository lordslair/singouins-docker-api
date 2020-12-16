# -*- coding: utf8 -*-

import os
import re
import sys

from datetime           import datetime,timedelta
from termcolor          import colored

# Shorted definition for actual now() with proper format
def mynow(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Log Discord imports
print('{} [{}] {} [{}]'.format(mynow(),'BOT', 'System   imports finished', colored('✓', 'green')))

import asyncio
import discord
import inspect

from discord.ext        import commands

# Log Discord imports
print('{} [{}] {} [{}]'.format(mynow(),'BOT', 'Discord  imports finished', colored('✓', 'green')))

from mysql.methods      import *
from mysql.utils        import redis
from variables          import token
from utils.messages     import *
from utils.histograms   import draw

# Log Discord imports
print('{} [{}] {} [{}]'.format(mynow(),'BOT', 'Internal imports finished', colored('✓', 'green')))

client = commands.Bot(command_prefix = '!')

# Welcome message in the logs on daemon start
print('{} [{}] {} [{}]'.format(mynow(),'BOT', 'Daemon started', colored('✓', 'green')))
# Pre-flich check for SQL connection
if query_up(): tick = colored('✓', 'green')
else         : tick = colored('✗', 'red')
print('{} [{}] {} [{}]'.format(mynow(),'BOT', 'SQL connection', tick))

@client.event
async def on_ready():
    channel = discord.utils.get(client.get_all_channels(), name='admins')
    if channel:
        tick = colored('✓', 'green')
        #await channel.send(msg_ready)
    else: tick = colored('✗', 'red')
    print('{} [{}] {}  [{}]'.format(mynow(),'BOT', 'Discord ready', tick))

@client.command()
async def ping(ctx):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print('{} [{}][{}] !ping'.format(mynow(),ctx.message.channel,member))
    await ctx.send(f'Pong! {round (client.latency * 1000)}ms ')

@client.command(pass_context=True)
async def register(ctx,arg):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator
    user         = query_get_user(discordname)
    registration = discord.utils.get(client.get_all_channels(), name='registration')

    print('{} [{}][{}] !register <{}> | {}'.format(mynow(),member,ctx.message.channel,arg,user.name))

    if (ctx.message.channel != discord.utils.get(client.get_all_channels(), name='registration')):
        # The command is entered in the wrong channel
        # Delete the !register <monkey> message sent by the user
        await ctx.message.delete()
        # Send help DM to user
        await ctx.message.author.send(msg_registration_help)
    else:
        if user:
            # The discordname is in DB
            if arg == user.d_monkeys:
                # Delete the !register <monkey> message sent by the user
                await ctx.message.delete()
                # Fetch the Discord role
                role = discord.utils.get(member.guild.roles, name='Singouins')
                # Apply role on user
                await ctx.message.author.add_roles(role)
                # Rename user
                await ctx.message.author.edit(nick = user.name)
                # Validate user association in DB
                query_validate_user(discordname)
                # Send registered DM to user
                answer = msg_registered.format(ctx.message.author,user.name)
                await ctx.message.author.send(answer)
                print('{} [{}][{}]   registration done'.format(mynow(),member,ctx.message.channel))
            else:
                # The monkey-code is wrong
               await ctx.message.author.send(msg_wrong_monkeys)
               print('{} [{}][{}]   registration failed (wrong monkeys)'.format(mynow(),member,ctx.message.channel))
        else:
            # The discordname is not in DB
            await ctx.message.author.send(msg_unknown_discordname)
            print('{} [{}][{}]   registration failed (unknown discordname)'.format(mynow(),member,ctx.message.channel))

@client.command(pass_context=True)
async def histo(ctx,arg):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator
    adminrole    = discord.utils.get(member.guild.roles, name='Admins')
    adminchannel = discord.utils.get(client.get_all_channels(), name='admins')

    if adminrole in ctx.author.roles and ctx.message.channel == adminchannel:
        # This command is to be used only by Admin role
        # This command is to be used only in #admins
        print('{} [{}][{}] !histo <{}>'.format(mynow(),member,ctx.message.channel,arg))

        # We'll draw a chart with Creatures Level occurences
        array  = query_histo(arg)
        answer = draw(array)
        if answer:
            await ctx.send(answer)
            print('{} [{}][{}] └> Histogram sent'.format(mynow(),member,ctx.message.channel,arg))
        else:
            print('{} [{}][{}] └> I failed (._.) '.format(mynow(),member,ctx.message.channel,arg))
    else:
        await ctx.send(f'You need to have the role {adminrole.name}')

@client.command(pass_context=True)
async def admin(ctx,*args):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator
    adminrole    = discord.utils.get(member.guild.roles, name='Admins')

    if adminrole not in ctx.author.roles:
        # This command is to be used only by Admin role
        print('{} [{}][{}] !admin <{}> [{}]'.format(mynow(),ctx.message.channel,member,args,'Unauthorized user'))

    # Channel and User are OK
    print('{} [{}][{}] !admin <{}>'.format(mynow(),ctx.message.channel,member,args))

    if args[0] == 'help':
        msg_help  = '!admin help\n'
        msg_help += '!admin redis  {reset|get} {all|blue|red} {pcid}\n'
        msg_help += '!admin wallet {get}       {all}          {pcid}'
        await ctx.send(f'```{msg_help}```')
        return

    if len(args) < 4:
        await ctx.send('`!admin needs more arguments`')
        return

    module = args[0]
    action = args[1]
    select = args[2]
    pcid   = int(args[3])

    pc = fn_creature_get(None,pcid)[3]
    if pc is None:
        await ctx.send(f'`Unknown creature pcid:{pcid}`')
        return

    if module == 'redis':
        if action == 'reset':
            if select == 'all':
                redis.reset_pa(pc,True,True)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
            elif select == 'red':
                redis.reset_pa(pc,False,True)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
            elif select == 'blue':
                redis.reset_pa(pc,True,False)
                await ctx.send(f'`Reset PA {select} done for pcid:{pc.id}`')
        elif action == 'get':
            if select == 'all':
                pa = redis.get_pa(pc)
                await ctx.send(pa)
        elif action == 'help':
            await ctx.send('`!admin redis {reset|get} {all|blue|red} {pcid}`')
    if module == 'wallet':
        if action == 'get':
            if select == 'all':
                wallet = query_wallet_get(pc)
                if wallet:
                    await ctx.send(wallet)
        elif action == 'help':
            await ctx.send('`!admin wallet {get} {all} {pcid}`')

@client.event
async def on_member_join(member):
    answer = msg_welcome.format(member.mention,'username',member.name,member.discriminator)
    await member.send(answer)

client.run(token)
