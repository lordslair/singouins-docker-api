# -*- coding: utf8 -*-

import os

from mongo.models.Meta import MetaArmor, MetaRace, MetaWeapon

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

URL_ASSETS = os.environ.get("URL_ASSETS")

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
