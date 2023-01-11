# -*- coding: utf8 -*-

from nosql.metas import (
    metaArmors,
    metaRaces,
    metaWeapons,
    )

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

# We build a simple dict to have the matching name for a metaid
# Gruik
# But working flawlessly
metaNames = {
    'armor': {},
    'race': {},
    'weapon': {},
}
for meta in metaWeapons:
    metaNames['weapon'][meta['id']] = meta['name']
for meta in metaArmors:
    metaNames['armor'][meta['id']] = meta['name']
for meta in metaRaces:
    metaNames['race'][meta['id']] = meta['name']
