# -*- coding: utf8 -*-

from loguru import logger
from redis import ResponseError
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition

from nosql.connector import r


def initialize_redis_config():
    try:
        config = r.config_get(pattern='notify-keyspace-events')
        if 'notify-keyspace-events' not in config or config['notify-keyspace-events'] == '':
            r.config_set(name='notify-keyspace-events', value='$sxE')
            logger.debug('Redis init: notify-keyspace-events OK')
    except Exception as e:
        logger.error(f'Redis init: notify-keyspace-events KO [{e}]')


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
