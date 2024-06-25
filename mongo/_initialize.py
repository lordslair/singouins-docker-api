# -*- coding: utf8 -*-

import json
import os

from loguru import logger

from mongo.models.Meta import MetaArmor, MetaRace, MetaWeapon

# Metafiles location for Redis init
META_FILES = {
    'armor': 'mongo/data/metas/armors.json',
    'consumable': 'mongo/data/metas/consumables.json',
    'race': 'mongo/data/metas/races.json',
    'recipe': 'mongo/data/metas/recipes.json',
    'weapon': 'mongo/data/metas/weapons.json',
}


# Load JSON meta files into DB if not exists
def initialize_mongodb_meta():
    # Loop over meta files
    for metatype, filename in META_FILES.items():
        if metatype == 'weapon':
            if MetaWeapon.objects().count() > 0:
                continue
        elif metatype == 'armor':
            if MetaArmor.objects().count() > 0:
                continue
        elif metatype == 'race':
            if MetaRace.objects().count() > 0:
                continue
        try:
            logger.debug(f'MongoDB init: >> singouins/meta/{metatype}')
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    metas = json.load(file)
                    for meta in metas:
                        # Needed to force ID creation in mongo
                        meta['_id'] = meta['id']
                        del meta['id']
                        # Create an instance of the Meta document
                        if metatype == 'weapon':
                            meta_doc = MetaWeapon(**meta)
                            meta_doc.save()
                        elif metatype == 'armor':
                            meta_doc = MetaArmor(**meta)
                            meta_doc.save()
                        elif metatype == 'race':
                            meta_doc = MetaRace(**meta)
                            meta_doc.save()
                        else:
                            logger.warning(f'MongoDB init: KO {metatype} not listed')

                        logger.trace(f"MongoDB init: >> singouins/meta_{metatype}/{meta['_id']}")
        except Exception as e:
            logger.error(f'MongoDB init: KO [{e}]')
        else:
            logger.debug(f'MongoDB init: OK singouins/meta_{metatype}')

    logger.info('MongoDB init: OK singouins/meta*')
