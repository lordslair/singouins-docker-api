# -*- coding: utf8 -*-

import json
import os.path

from loguru                      import logger
from redis                       import ResponseError
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.indexDefinition import IndexDefinition

from nosql.connector             import r

from .variables                  import MAP_FILES, META_FILES


def initialize_redis_meta():
    try:
        for meta, file in META_FILES.items():
            if os.path.exists(file):
                with open(file) as f:
                    content = f.read()
                    logger.debug(f'Redis init: creating system:meta:{meta}')
                    r.set(f'system:meta:{meta}', content)
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK system:meta:*')

    try:
        for metatype, file in META_FILES.items():
            metas = json.loads(r.get(f'system:meta:{metatype}'))
            logger.debug(f'Redis init: creating metas:{metatype}:*')
            for meta in metas:
                for k, v in meta.items():
                    if v is None:
                        meta[k] = 'None'
                    elif v is False:
                        meta[k] = 'False'
                    elif v is True:
                        meta[k] = 'True'
                    elif isinstance(v, dict):
                        meta[k] = str(v)
                r.hset(f"metas:{metatype}:{meta['id']}", mapping=meta)
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK metas:*')

    try:
        for map, file in MAP_FILES.items():
            if os.path.exists(file):
                with open(file) as f:
                    content = f.read()
                    data = json.loads(content)
                    logger.debug(f'Redis init: creating system:map:{map}')
                    r.set(f'system:map:{map}:data', content)
                    r.set(f'system:map:{map}:type', 'Instance')
                    r.set(f'system:map:{map}:mode', 'Normal')
                    r.set(
                        f'system:map:{map}:size',
                        f"{data['height']}x{data['width']}"
                        )
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK system:map:*')


def initialize_redis_indexes():
    #
    # RedisSearch INDEX init
    #

    # RedisAuction
    try:
        r.ft("auction_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_auction = IndexDefinition(
                prefix=["auctions:"],
                score=0.5,
                score_field="auction_score"
                )

            # Schema definition
            schema = (
                NumericField("duration_base"),
                TextField("id"),
                NumericField("metaid"),
                TextField("metaname"),
                TextField("metatype"),
                NumericField("price"),
                TextField("rarity"),
                TextField("sellerid"),
                TextField("sellername"),
            )

            # Create an index and pass in the schema
            r.ft("auction_idx").create_index(
                schema,
                definition=index_auction
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK auction_idx')
    else:
        logger.trace('Redis init: OK auction_idx (already created)')

    # RedisCD
    try:
        r.ft("cd_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_cd = IndexDefinition(
                prefix=["cds:"],
                score=0.5,
                score_field="cd_score"
                )

            # Schema definition
            schema = (
                TextField("bearer"),
                NumericField("duration_base"),
                TextField("extra"),
                TextField("id"),
                TextField("name"),
                TextField("source"),
                TextField("type"),
            )

            # Create an index and pass in the schema
            r.ft("cd_idx").create_index(
                schema,
                definition=index_cd
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK cd_idx')
    else:
        logger.trace('Redis init: OK cd_idx (already created)')

    # RedisCosmetic
    try:
        r.ft("cosmetic_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_cosmetic = IndexDefinition(
                prefix=["cosmetics:"],
                score=0.5,
                score_field="cosmetic_score"
                )

            # Schema definition
            schema = (
                TextField("bearer"),
                TextField("bound"),
                TextField("bound_type"),
                TextField("id"),
                NumericField("metaid"),
                TextField("rarity"),
                NumericField("state"),
            )

            # Create an index and pass in the schema
            r.ft("cosmetic_idx").create_index(
                schema,
                definition=index_cosmetic
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK cosmetic_idx')
    else:
        logger.trace('Redis init: OK cosmetic_idx (already created)')

    # RedisCreature
    try:
        r.ft("creature_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_creature = IndexDefinition(
                prefix=["creatures:"],
                score=0.5,
                score_field="creature_score"
                )

            # Schema definition
            schema = (
                TextField("account"),
                TextField("id"),
                TextField("instance"),
                TextField("korp"),
                TextField("korp_rank"),
                TextField("name"),
                NumericField("race"),
                TextField("squad"),
                TextField("squad_rank"),
                NumericField("x"),
                NumericField("y"),
            )

            # Create an index and pass in the schema
            r.ft("creature_idx").create_index(
                schema,
                definition=index_creature
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK creature_idx')
    else:
        logger.trace('Redis init: OK creature_idx (already created)')

    # RedisEffect
    try:
        r.ft("effect_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_effect = IndexDefinition(
                prefix=["effects:"],
                score=0.5,
                score_field="effect_score"
                )

            # Schema definition
            schema = (
                TextField("bearer"),
                NumericField("duration_base"),
                TextField("extra"),
                TextField("id"),
                TextField("name"),
                TextField("source"),
                TextField("type"),
            )

            # Create an index and pass in the schema
            r.ft("effect_idx").create_index(
                schema,
                definition=index_effect
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK effect_idx')
    else:
        logger.trace('Redis init: OK effect_idx (already created)')

    # RedisEvent
    try:
        r.ft("event_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_event = IndexDefinition(
                prefix=["events:"],
                score=0.5,
                score_field="event_score"
                )

            # Schema definition
            schema = (
                TextField("dst"),
                TextField("action"),
                TextField("type"),
                TextField("src"),
                TextField("date"),
                TextField("id"),
                NumericField("timestamp"),
            )

            # Create an index and pass in the schema
            r.ft("event_idx").create_index(
                schema,
                definition=index_event
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK event_idx')
    else:
        logger.trace('Redis init: OK event_idx (already created)')

    # RedisInstance
    try:
        r.ft("instance_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_instance = IndexDefinition(
                prefix=["instances:"],
                score=0.5,
                score_field="instance_score"
                )

            # Schema definition
            schema = (
                TextField("creator"),
                TextField("fast"),
                TextField("hardcore"),
                TextField("id"),
                NumericField("map"),
                TextField("public"),
                NumericField("tick"),
            )

            # Create an index and pass in the schema
            r.ft("instance_idx").create_index(
                schema,
                definition=index_instance
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK instance_idx')
    else:
        logger.trace('Redis init: OK instance_idx (already created)')

    # RedisItem
    try:
        r.ft("item_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_item = IndexDefinition(
                prefix=["items:"],
                score=0.5,
                score_field="item_score"
                )

            # Schema definition
            schema = (
                TextField("bearer"),
                TextField("bound"),
                TextField("bound_type"),
                TagField("id"),
                TextField("metatype"),
                NumericField("metaid"),
                TextField("modded"),
                TextField("mods"),
                NumericField("NUMERIC"),
                TextField("TEXT"),
            )

            # Create an index and pass in the schema
            r.ft("item_idx").create_index(
                schema,
                definition=index_item
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK item_idx')
    else:
        logger.trace('Redis init: OK item_idx (already created)')

    # RedisKorp
    try:
        r.ft("korp_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_korp = IndexDefinition(
                prefix=["korps:"],
                score=0.5,
                score_field="korp_score"
                )

            # Schema definition
            schema = (
                TextField("id"),
                TextField("leader"),
                TextField("name"),
            )

            # Create an index and pass in the schema
            r.ft("korp_idx").create_index(
                schema,
                definition=index_korp
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK korp_idx')
    else:
        logger.trace('Redis init: OK korp_idx (already created)')

    # RedisSquad
    try:
        r.ft("squad_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_squad = IndexDefinition(
                prefix=["squads:"],
                score=0.5,
                score_field="squad_score"
                )

            # Schema definition
            schema = (
                TextField("id"),
                TextField("leader"),
                TextField("name"),
            )

            # Create an index and pass in the schema
            r.ft("squad_idx").create_index(
                schema,
                definition=index_squad
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK squad_idx')
    else:
        logger.trace('Redis init: OK squad_idx (already created)')

    # RedisCD
    try:
        r.ft("status_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_status = IndexDefinition(
                prefix=["statuses:"],
                score=0.5,
                score_field="status_score"
                )

            # Schema definition
            schema = (
                TextField("bearer"),
                NumericField("duration_base"),
                TextField("extra"),
                TextField("id"),
                TextField("name"),
                TextField("source"),
                TextField("type"),
            )

            # Create an index and pass in the schema
            r.ft("status_idx").create_index(
                schema,
                definition=index_status
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK status_idx')
    else:
        logger.trace('Redis init: OK status_idx (already created)')

    # RedisUser
    try:
        r.ft("user_idx").info()
    except ResponseError:
        # We need to create the index
        try:
            # Options for index creation
            index_user = IndexDefinition(
                prefix=["users:"],
                score=0.5,
                score_field="user_score"
                )

            # Schema definition
            schema = (
                TextField("active"),
                TextField("d_ack"),
                TextField("d_name"),
                TextField("id"),
                TextField("name"),
            )

            # Create an index and pass in the schema
            r.ft("user_idx").create_index(
                schema,
                definition=index_user
                )
        except Exception as e:
            logger.error(f'Redis init: KO [{e}]')
        else:
            logger.info('Redis init: OK user_idx')
    else:
        logger.trace('Redis init: OK user_idx (already created)')
