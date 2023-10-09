# -*- coding: utf8 -*-

import os

URL_ASSETS = os.environ.get("SEP_URL_ASSETS")

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
