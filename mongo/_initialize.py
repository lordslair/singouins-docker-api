# -*- coding: utf8 -*-

import json
import os

from loguru import logger

from mongo.models.Meta import (
    MetaArmor,
    MetaConsumable,
    MetaMap,
    MetaRace,
    MetaRecipe,
    MetaWeapon,
    )

# Metafiles location for Mongo init
META_FILES = {
    'armor': 'mongo/data/metas/armors.json',
    'consumable': 'mongo/data/metas/consumables.json',
    'race': 'mongo/data/metas/races.json',
    'recipe': 'mongo/data/metas/recipes.json',
    'weapon': 'mongo/data/metas/weapons.json',
}
# Mapfiles location for Redis init
MAP_FILES = {
    1: 'mongo/data/maps/1.json',
    2: 'mongo/data/maps/2.json'
}


# Load JSON meta files into DB if not exists
def initialize_mongodb_meta():
    # Loop over meta files
    for metatype, filename in META_FILES.items():
        if metatype == 'armor':
            if MetaArmor.objects().count() > 0:
                continue
        elif metatype == 'consumable':
            if MetaConsumable.objects().count() > 0:
                continue
        elif metatype == 'race':
            if MetaRace.objects().count() > 0:
                continue
        elif metatype == 'recipe':
            if MetaRecipe.objects().count() > 0:
                continue
        elif metatype == 'weapon':
            if MetaWeapon.objects().count() > 0:
                continue

        try:
            logger.trace(f'MongoDB init: >> singouins/_meta{metatype}')
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    metas = json.load(file)
                    for meta in metas:
                        # Needed to force ID creation in mongo
                        meta['_id'] = meta['id']
                        del meta['id']
                        # Create an instance of the Meta document
                        if metatype == 'armor':
                            meta_doc = MetaArmor(**meta)
                        elif metatype == 'consumable':
                            meta_doc = MetaConsumable(**meta)
                        elif metatype == 'race':
                            meta_doc = MetaRace(**meta)
                        elif metatype == 'recipe':
                            meta_doc = MetaRecipe(**meta)
                        elif metatype == 'weapon':
                            meta_doc = MetaWeapon(**meta)
                        else:
                            logger.warning(f'MongoDB init: KO {metatype} not listed')
                            continue

                        meta_doc.save()
                        logger.trace(f"MongoDB init: >> singouins/_meta{metatype}/{meta['_id']}")
        except Exception as e:
            logger.error(f'MongoDB init: KO [{e}]')
        else:
            logger.debug(f'MongoDB init: OK singouins/_meta{metatype}')

    logger.info('MongoDB init: OK singouins/_meta*')


# Load JSON meta files into DB if not exists
def initialize_mongodb_map():
    logger.trace('MongoDB init: >> singouins/_maps/*')
    for map_id, filename in MAP_FILES.items():
        if MetaMap.objects(_id=map_id):
            continue

        if os.path.exists(filename):
            pass
        else:
            logger.warning("MongoDB init: KO filename 404")
            continue

        try:
            logger.trace(f"MongoDB init: >> singouins/_maps/{map_id}")
            with open(filename, 'r') as file:
                map_data = json.load(file)
                # Create an instance of the Map document
                map_doc = MetaMap(
                    _id=map_id,
                    size=f"{map_data['height']}x{map_data['width']}",
                    data=map_data,
                    )
                map_doc.save()
        except Exception as e:
            logger.error(f'MongoDB init: KO [{e}]')
        else:
            logger.trace(f"MongoDB init: OK singouins/_maps/{map_id}")

    logger.info('MongoDB init: OK singouins/_maps/*')
