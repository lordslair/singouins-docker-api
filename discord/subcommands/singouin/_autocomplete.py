# -*- coding: utf8 -*-

import discord

from loguru import logger

from mongo.models.Creature import CreatureDocument
from mongo.models.User import UserDocument


async def get_mysingouins_list(ctx: discord.AutocompleteContext):
    db_list = []
    try:
        User = UserDocument.objects(discord__name=ctx.interaction.user.name).get()
        Creatures = CreatureDocument.objects(account=User.id)
    except CreatureDocument.DoesNotExist:
        logger.warning("CreatureDocument Query KO (404)")
    except UserDocument.DoesNotExist:
        logger.warning("UserDocument Query KO (404)")
    except Exception as e:
        logger.error(f'MongoDB Query KO [{e}]')
    else:
        for Creature in Creatures:
            db_list.append(
                discord.OptionChoice(Creature.name, value=str(Creature.id))
                )
    finally:
        return db_list
