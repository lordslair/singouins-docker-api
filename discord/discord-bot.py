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

from mysql.methods.fn_creature import fn_creature_get
from mysql.methods.fn_user     import fn_user_get_from_member

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

#
# Commands
#

# !ping
@client.command(name='ping', help='Gives you Discord bot latency')
async def ping(ctx):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print('{} [{}][{}] !ping'.format(mynow(),ctx.message.channel,member))
    await ctx.send(f'Pong! {round (client.latency * 1000)}ms ')

#
# Commands for Registration/Grant
#

# !register {user.mail}
@client.command(pass_context=True,name='register', help='Register a Discord user with a Singouins user')
async def register(ctx, usermail: str):
    member       = ctx.message.author
    discordname  = member.name + '#' + member.discriminator

    print('{} [{}][{}] !register <usermail:{}>'.format(mynow(),ctx.message.channel,member,usermail))

    # Validate user association in DB
    user = query_user_validate(usermail,discordname)
    if user:
        # Send registered DM to user
        answer = msg_register_ok.format(ctx.message.author)
        await ctx.message.author.send(answer)
        print('{} [{}][{}] └> Validation in DB Successful'.format(mynow(),ctx.message.channel,member))
    else:
        # Send failure DM to user
        await ctx.message.author.send(msg_register_ko)
        print('{} [{}][{}] └> Validation in DB Failed'.format(mynow(),ctx.message.channel,member))

# !grant
@client.command(pass_context=True,name='grant', help='Grant a Discord user relative roles')
async def register(ctx):
    member       = ctx.message.author

    print('{} [{}][{}] !grant'.format(mynow(),ctx.message.channel,member))

    # Delete the !grant message sent by the user
    try:
        await ctx.message.delete()
    except:
        pass

    user = fn_user_get_from_member(member)
    if user:
        # Fetch the Discord role
        try:
            role = discord.utils.get(member.guild.roles, name='Singouins')
        except Exception as e:
            # Something went wrong
            print('{} [{}][{}] └> Member get-role Failed'.format(mynow(),ctx.message.channel,member))
        else:
            print('{} [{}][{}] └> Member get-role Successful'.format(mynow(),ctx.message.channel,member))

        # Apply role on user
        try:
            await ctx.message.author.add_roles(role)
        except Exception as e:
            # Something went wrong during commit
            print('{} [{}][{}] └> Member add-role Failed'.format(mynow(),ctx.message.channel,member))
            # Send failure DM to user
            await ctx.message.author.send(msg_grant_ko)
        else:
            # Send success DM to user
            await ctx.message.author.send(msg_grant_ok)
            print('{} [{}][{}] └> Member add-role Successful'.format(mynow(),ctx.message.channel,member))
    else:
        # Send failure DM to user
        await ctx.message.author.send(msg_grant_ko)
        print('{} [{}][{}] └> Query in DB Failed'.format(mynow(),ctx.message.channel,member))

#
# Commands for Admins
#

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
        await ctx.send(f'```{msg_cmd_admin_help}```')
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

#
# Commands for Singouins
#

@client.command(pass_context=True,name='mysingouins', help='Display your Singouins')
async def mysingouins(ctx):
    member       = ctx.message.author

    print('{} [{}][{}] !mysingouins'.format(mynow(),ctx.message.channel,member))

    emojiM = discord.utils.get(client.emojis, name='statM')
    emojiR = discord.utils.get(client.emojis, name='statR')
    emojiV = discord.utils.get(client.emojis, name='statV')
    emojiG = discord.utils.get(client.emojis, name='statG')
    emojiP = discord.utils.get(client.emojis, name='statP')
    emojiB = discord.utils.get(client.emojis, name='statB')

    emojiRaceC = discord.utils.get(client.emojis, name='raceC')
    emojiRaceG = discord.utils.get(client.emojis, name='raceG')
    emojiRaceM = discord.utils.get(client.emojis, name='raceM')
    emojiRaceO = discord.utils.get(client.emojis, name='raceO')
    emojiRace = [emojiRaceC,
                 emojiRaceG,
                 emojiRaceM,
                 emojiRaceO]

    pcs = query_pcs_get(member)[3]
    if pcs is None:
        await ctx.send(f'`No Singouin found in DB`')

    mydesc = ''
    for pc in pcs:
        emojiMyRace = emojiRace[pc.race]
        mydesc += f'{emojiMyRace} [{pc.id}] {pc.name}\n'

    embed = discord.Embed(
        title = 'Mes Singouins:',
        description = mydesc,
        colour = discord.Colour.blue()
    )

    await ctx.send(embed=embed)

@client.command(pass_context=True,name='mysingouin', help='Display a Singouin profile')
async def myperso(ctx, pcid: int):
    member       = ctx.message.author

    print('{} [{}][{}] !mysingouin <{}>'.format(mynow(),ctx.message.channel,member,id))

    pc = query_pc_get(pcid,member)[3]
    if pc is None:
        await ctx.send(f'`Singouin not yours/not found in DB (pcid:{pcid})`')

    embed = discord.Embed(
        title = f'[{pc.id}] {pc.name}\n',
        #description = 'Profil:',
        colour = discord.Colour.blue()
    )

    emojiM = discord.utils.get(client.emojis, name='statM')
    emojiR = discord.utils.get(client.emojis, name='statR')
    emojiV = discord.utils.get(client.emojis, name='statV')
    emojiG = discord.utils.get(client.emojis, name='statG')
    emojiP = discord.utils.get(client.emojis, name='statP')
    emojiB = discord.utils.get(client.emojis, name='statB')

    msg_stats = 'Stats:'
    msg_nbr   = 'Nbr:'
    embed.add_field(name=f'`{msg_stats: >7}`      {emojiM}      {emojiR}      {emojiV}      {emojiG}      {emojiP}      {emojiB}',
                    value=f'`{msg_nbr: >7}` `{pc.m: >4}` `{pc.r: >4}` `{pc.v: >4}` `{pc.g: >4}` `{pc.p: >4}` `{pc.b: >4}`',
                    inline = False)

    msg_shards = 'Shards:'
    msg_nbr    = 'Nbr:'
    embed.add_field(name=f'`{msg_shards: >7}`      🟠      🟣      🔵      🟢      ⚪      🟤',
                    value=f'`{msg_nbr: >7}` `{5: >4}` `{42: >4}` `{31: >4}` `{25: >4}` `{11: >4}` `{123: >4}`',
                    inline = False)

    embed.set_footer(text='🍌: 123456')

    await ctx.send(embed=embed)

@client.event
async def on_member_join(member):
    await member.send(msg_welcome)

client.run(token)
