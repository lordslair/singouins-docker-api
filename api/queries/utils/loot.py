# -*- coding: utf8 -*-

from random         import randint,choices

def get_loot_weight(rarity):
    weight = {}
    if   rarity == 'Small':
        weight['b'] = 65
        weight['c'] = 35
        weight['u'] = 0
        weight['r'] = 0
        weight['e'] = 0
        weight['l'] = 0
    elif rarity == 'Medium':
        weight['b'] = 25
        weight['c'] = 65
        weight['u'] = 8
        weight['r'] = 2
        weight['e'] = 0
        weight['l'] = 0
    elif rarity == 'Big':
        weight['b'] = 4
        weight['c'] = 25
        weight['u'] = 65
        weight['r'] = 6
        weight['e'] = 0
        weight['l'] = 0
    elif rarity == 'Unique':
        weight['b'] = 3
        weight['c'] = 4
        weight['u'] = 25
        weight['r'] = 65
        weight['e'] = 3
        weight['l'] = 0
    elif rarity == 'Boss':
        weight['b'] = 2
        weight['c'] = 3
        weight['u'] = 4
        weight['r'] = 25
        weight['e'] = 65
        weight['l'] = 1
    elif rarity == 'God':
        weight['b'] = 1
        weight['c'] = 2
        weight['u'] = 3
        weight['r'] = 4
        weight['e'] = 25
        weight['l'] = 65
    return weight

def get_loot_rarity(rarity):
    weight      = get_loot_weight(rarity)
    loot_rarity = choices(['Broken','Common','Uncommon','Rare','Epic','Legendary'],
                           weights=(weight['b'],
                                    weight['c'],
                                    weight['u'],
                                    weight['r'],
                                    weight['e'],
                                    weight['l']),
                           k=1)
    return loot_rarity

def get_loot_bound_type():
    loot_bound_type = choices(['BoP','BoE'], weights=(95, 5), k=1)
    return loot_bound_type

def get_loot_metatype():
    loot_metatype = choices(['weapon','armor'], weights=(50, 50), k=1)
    return loot_metatype
