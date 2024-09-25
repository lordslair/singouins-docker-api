# -*- coding: utf8 -*-

import os

from distutils.util import strtobool
from loguru import logger

from mongo.models.Meta import MetaArmor, MetaRace, MetaWeapon

# Grab the environment variables
env_vars = {
    "API_ENV": os.environ.get("API_ENV", None),
    "DISCORD_GUILD": os.environ.get("DISCORD_GUILD", None),
    "DISCORD_TOKEN": os.environ.get("DISCORD_TOKEN"),
    "SSL_CHECK": strtobool(os.getenv("SSL_CHECK", "True")),
    "SSL_TARGET_HOST": os.environ.get("SSL_TARGET_HOST"),
    "SSL_TARGET_PORT": os.environ.get("SSL_TARGET_PORT", 443),
    "SSL_CHANNEL": os.environ.get("SSL_CHANNEL"),
    "SSL_IMG_URL": os.environ.get("SSL_IMG_URL"),
    "URL_ASSETS": os.environ.get("URL_ASSETS", 'https://singouins.github.io/assets'),
    "YQ_DISCORD": os.environ.get("YQ_DISCORD", f'{os.environ.get("API_ENV", None)}:yarqueue:discord'), # noqa E501
    "YQ_CHECK": strtobool(os.getenv("YQ_CHECK", "False")),
}
# Print the environment variables for debugging
for var, value in env_vars.items():
    logger.debug(f"{var}: {value}")


"""
DISCLAIMER: This is some fat shit I dumped here

This is a HUGE Dictionary to manipulate pore easiliy all the metas
Without having to query MongoDB all the time internally

Do not modifiy unless you're ready for consequences
"""
metaNames = {
    'armor': [doc.to_mongo().to_dict() for doc in MetaArmor.objects()],
    'weapon': [doc.to_mongo().to_dict() for doc in MetaWeapon.objects()],
    'race': [doc.to_mongo().to_dict() for doc in MetaRace.objects()]
}

item_types_discord = {
    'armor': ':shirt:',
    'weapon': ':dagger:'
    }

rarity_item_types_emoji = {
    'Broken': '🟤 ',
    'Common': '⚪ ',
    'Uncommon': '🟢 ',
    'Rare': '🔵 ',
    'Epic': '🟣 ',
    'Legendary': '🟠 ',
}

rarity_item_types_discord = {
    'Broken': ':brown_square:',
    'Common': ':white_large_square:',
    'Uncommon': ':green_square:',
    'Rare': ':blue_square:',
    'Epic': ':purple_square:',
    'Legendary': ':orange_square:',
}

rarity_item_types_integer = {
    'Broken': 10197915,
    'Common': 16777215,
    'Uncommon': 8311585,
    'Rare': 4886754,
    'Epic': 9442302,
    'Legendary': 16098851,
}

rarity_monster_types_emoji = {
    'Small': '🟤 ',
    'Medium': '⚪ ',
    'Big': '🟢 ',
    'Unique': '🔵 ',
    'Boss': '🟣 ',
    'God': '🟠 ',
}

rarity_monster_types_discord = {
    'Small': ':brown_square:',
    'Medium': ':white_large_square:',
    'Big': ':green_square:',
    'Unique': ':blue_square:',
    'Boss': ':purple_square:',
    'God': ':orange_square:',
}

slots_armor = {
    'head': ':military_helmet:',
    'shoulders': ':mechanical_arm:',
    'torso': ':shirt:',
    'hands': ':hand_splayed:',
    'legs': ':mechanical_leg:',
    'feet': ':athletic_shoe:',
    }
slots_weapon = {
    'holster': ':school_satchel:',
    'lefthand': ':left_fist:',
    'righthand': ':right_fist:',
}
slots_types = slots_armor | slots_weapon
