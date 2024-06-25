# -*- coding: utf8 -*-

import discord

from loguru import logger

from mongo.models.Creature import CreatureDocument
from mongo.models.User import UserDocument


async def get_mysingouins_list(ctx: discord.AutocompleteContext):
    try:
        User = UserDocument.objects(discord__name=ctx.interaction.user.name).get()
        Creatures = CreatureDocument.objects(account=User.id)
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
        return None
    else:
        db_list = []
        for Creature in Creatures:
            db_list.append(
                discord.OptionChoice(Creature.name, value=str(Creature.id))
                )
        return db_list
