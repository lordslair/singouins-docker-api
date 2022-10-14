# -*- coding: utf8 -*-

import json

from datetime                   import datetime
from loguru                     import logger

from nosql.connector            import r

from .variables                 import MAP_FILES, META_FILES


def initialize_redis():
    try:
        logger.info('Redis init: start')
        r.set('system:startup', datetime.now().isoformat())
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK system:startup')

    try:
        for meta, file in META_FILES.items():
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
            metas = json.loads(content)
            for meta in metas:
                for k, v in meta.items():
                    if v is None:
                        meta[k] = 'None'
                    elif v is False:
                        meta[k] = 'False'
                    elif v is True:
                        meta[k] = 'True'
                r.hset(f"metas:{metatype}:{meta['id']}", mapping=meta)
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK metas:*')

    try:
        for map, file in MAP_FILES.items():
            with open(file) as f:
                content = f.read()
                data = json.loads(content)
                logger.debug(f'Redis init: creating system:map:{map}')
                r.set(f'system:map:{map}:data', content)
                r.set(f'system:map:{map}:type', 'Instance')
                r.set(f'system:map:{map}:mode', 'Normal')
                r.set(f'system:map:{map}:size',
                      f"{data['height']}x{data['width']}")
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK system:map:*')

    try:
        if r.exists('system:instance_max_id'):
            pass
        else:
            r.set('system:instance_max_id', 0)
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK system:instance_max_id')
    finally:
        logger.info('Redis init: end')
