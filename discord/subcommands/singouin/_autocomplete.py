# -*- coding: utf8 -*-

import discord

from loguru import logger

from nosql.models.RedisSearch import RedisSearch


async def get_mysingouins_list(ctx: discord.AutocompleteContext):
    try:
        DiscordUser = ctx.interaction.user
        discordname = f'{DiscordUser.name}#{DiscordUser.discriminator}'
        Users = RedisSearch().user(query=f'@d_name:{discordname}')

        if len(Users.results) == 0:
            return []
        else:
            User = Users.results[0]
            account = User.id.replace('-', ' ')
            Creatures = RedisSearch().creature(query=f'@account:{account}')
    except Exception as e:
        logger.error(f'Redis Query KO [{e}]')
        return None
    else:
        db_list = []
        for Creature in Creatures.results:
            db_list.append(
                discord.OptionChoice(Creature.name, value=Creature.id)
                )
        return db_list
