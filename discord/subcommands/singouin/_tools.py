# -*- coding: utf8 -*-

import urllib.request

from itertools import chain
from loguru import logger
from PIL import Image

from mongo.models.Creature import CreatureDocument
from mongo.models.Item import ItemDocument

from variables import env_vars, slots_armor, slots_weapon


def creature_sprite(Creature: CreatureDocument):
    """
    Generate a complete sprite image for a Creature, layering equipped items onto a base sprite.

    Parameters:
        Creature (CreatureDocument): The creature document containing all necessary details.

    Returns:
        bool: True if the sprite generation succeeds, False otherwise.
    """

    # We need to DL the base sprite
    logger.trace(f'Downloading base image for {Creature.id} ({Creature.race})')
    url = f"{env_vars['URL_ASSETS']}/sprites/creatures/{Creature.race}.png"
    logger.trace(f'Downloading {url} > /tmp/{Creature.id}.png')
    urllib.request.urlretrieve(url, f'/tmp/{Creature.id}.png')

    # We keep the sprite_base for later
    sprite_base = Image.open(f'/tmp/{Creature.id}.png').convert("RGBA")

    Creature = CreatureDocument.objects(_id=Creature.id).get()
    try:
        # We compute Armors first to be the lower layer
        for slot in chain(slots_armor.keys(), slots_weapon.keys()):
            Slot = getattr(Creature.slots, slot)
            if Slot is None:
                # Nothing equipped, we go next
                continue

            try:
                Item = ItemDocument.objects(_id=Slot.id).get()
            except ItemDocument.DoesNotExist:
                logger.warning(f'ItemDocument(_id={Slot.id}) Query KO (404)')
                continue
            else:
                logger.trace(f'Equipped: [{Slot.id}] {slot}:{Item.metaid}')

            if slot in slots_weapon:
                # For weapons
                if slot == 'righthand':
                    file = f'{Item.metaid}-0.png'
                elif slot == 'lefthand':
                    file = f'{Item.metaid}-1.png'
                else:
                    file = f'{Item.metaid}.png'
            else:
                # For Armors
                file = f'1/{Item.metaid}.png'

            url = f"{env_vars['URL_ASSETS']}/sprites/{Item.metatype}s/{file}"
            logger.trace(f'Downloading {url} > /tmp/{Creature.id}_{slot}.png')
            urllib.request.urlretrieve(url, f'/tmp/{Creature.id}_{slot}.png')
            sprite_item_raw = Image.open(f'/tmp/{Creature.id}_{slot}.png')
            sprite_item = sprite_item_raw.convert("RGBA")

            # We merge images
            sprite_base.paste(sprite_item, (0, 0), sprite_item)
            logger.trace(f'Merged {slot}')

        sprite_base.save(f'/tmp/{Creature.id}.png', format="PNG")
        logger.trace(f'Saved /tmp/{Creature.id}.png')
    except Exception as e:
        logger.error(e)
        return False
    else:
        return True
