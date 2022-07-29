# -*- coding: utf8 -*-

from datetime             import datetime

from .connector            import *
from .variables            import MAP_FILES,META_FILES

def initialize_redis():
    try:
        logger.info(f'Redis init: start')
        r.set('system:startup',datetime.now().isoformat())
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info('Redis init: OK system:startup')

    try:
        for meta,file in META_FILES.items():
            with open(file) as f:
                content = f.read()
                logger.debug(f'Redis init: creating system:meta:{meta}')
                r.set(f'system:meta:{meta}', content)
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info(f'Redis init: OK system:meta:*')

    try:
        for map,file in MAP_FILES.items():
            with open(file) as f:
                content = f.read()
                data = json.loads(content)
                logger.debug(f'Redis init: creating system:map:{map}')
                r.set(f'system:map:{map}:data', content)
                r.set(f'system:map:{map}:type', 'Instance')
                r.set(f'system:map:{map}:mode', 'Normal')
                r.set(f'system:map:{map}:size', f"{data['height']}x{data['width']}")
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info(f'Redis init: OK system:map:*')

    try:
        if r.exists(f'system:instance_max_id'):
            pass
        else:
            r.set(f'system:instance_max_id', 0)
    except Exception as e:
        logger.error(f'Redis init: KO [{e}]')
    else:
        logger.info(f'Redis init: OK system:instance_max_id')
    finally:
        logger.info('Redis init: end')
