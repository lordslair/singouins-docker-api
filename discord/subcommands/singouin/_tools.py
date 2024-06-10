# -*- coding: utf8 -*-

import urllib.request

from loguru import logger
from PIL import Image

from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument

from variables import URL_ASSETS, slots_armor, slots_weapon


def creature_sprite(creatureuuid, race):
    # We need to DL the base sprite
    logger.debug(f'Downloading base image for {creatureuuid} ({race})')
    url = f'{URL_ASSETS}/sprites/creatures/{race}.png'
    logger.trace(f'Downloading {url} > /tmp/{creatureuuid}.png')
    urllib.request.urlretrieve(url, f'/tmp/{creatureuuid}.png')

    # We keep the sprite_base for later
    sprite_base = Image.open(f'/tmp/{creatureuuid}.png').convert("RGBA")

    Creature = CreatureDocument.objects(_id=creatureuuid).get()
    try:
        # We compute Armors first to be the lower layer
        for slot in slots_armor:
            slot_id = getattr(Creature.slots, slot)
            if slot_id is None:
                # Nothing equipped, we go next
                continue

            Item = ItemDocument.objects(_id=slot_id).get()
            logger.debug(f'Equipped: [{slot_id}] {slot}:{Item.metaid}')

            file = f'/1/{Item.metaid}.png'
            url = f'{URL_ASSETS}/sprites/{Item.metatype}s/{file}'
            logger.trace(f'Downloading {url} > /tmp/{creatureuuid}_{slot}.png')
            urllib.request.urlretrieve(url, f'/tmp/{creatureuuid}_{slot}.png')
            sprite_item_raw = Image.open(f'/tmp/{creatureuuid}_{slot}.png')
            sprite_item = sprite_item_raw.convert("RGBA")

            # We merge images
            sprite_base.paste(sprite_item, (0, 0), sprite_item)
            logger.trace(f'Merged {slot}')

        for slot in slots_weapon:
            slot_id = getattr(Creature.slots, slot)
            if slot_id is None:
                # Nothing equipped, we go next
                continue

            Item = ItemDocument.objects(_id=slot_id).get()
            logger.debug(f'Equipped: [{slot_id}] {slot}:{Item.metaid}')

            # Specifics for weapons
            if slot == 'righthand':
                file = f'{Item.metaid}-0.png'
            elif slot == 'lefthand':
                file = f'{Item.metaid}-1.png'
            else:
                file = f'{Item.metaid}.png'
            url = f'{URL_ASSETS}/sprites/{Item.metatype}s/{file}'
            logger.trace(f'Downloading {url} > /tmp/{creatureuuid}_{slot}.png')
            urllib.request.urlretrieve(url, f'/tmp/{creatureuuid}_{slot}.png')
            sprite_item_raw = Image.open(f'/tmp/{creatureuuid}_{slot}.png')
            sprite_item = sprite_item_raw.convert("RGBA")

            # We merge images
            sprite_base.paste(sprite_item, (0, 0), sprite_item)
            logger.trace(f'Merged {slot}')

        sprite_base.save(f'/tmp/{creatureuuid}.png', format="PNG")
        logger.trace(f'Saved /tmp/{creatureuuid}.png')
    except Exception as e:
        logger.error(e)
        return False
    else:
        return True
