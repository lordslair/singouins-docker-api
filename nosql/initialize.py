# -*- coding: utf8 -*-

import json
import os.path

from loguru                      import logger
from redis                       import ResponseError
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition

from nosql.connector             import r

from .variables                  import MAP_FILES, META_FILES


def initialize_redis_config():
    try:
        config = r.config_get(pattern='notify-keyspace-events')
        if config is None or config != '':
            r.config_set(name='notify-keyspace-events', value='$sxE')
    except Exception as e:
        logger.error(f'Redis init: notify-keyspace-events KO [{e}]')
    else:
        logger.debug('Redis init: notify-keyspace-events OK')


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
                TextField("instance"),
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
                TextField("instance"),
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

    # RedisStatus
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
                TextField("instance"),
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
