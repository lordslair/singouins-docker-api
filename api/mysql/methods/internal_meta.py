# -*- coding: utf8 -*-

from ..utils.redis.metas import get_meta

#
# Queries /internal/meta/*
#

# API: GET /internal/meta/<str:metatype>
def internal_meta_get_one(metatype):
    # Pre-flight checks
    if not isinstance(metatype, str):
        return (200,
                False,
                f'Meta type Malformed (metatype:{metatype})',
                None)

    try:
        meta = get_meta(metatype)
    except Exception as e:
        return (200,
                False,
                f'[get_meta()] Query failed (metatype:{metatype}) [{e}]',
                None)
    else:
        if meta:
            return (200,
                    True,
                    f'Meta found (metatype:{metatype})',
                    meta)
        else:
            return (200,
                    False,
                    f'Meta not found (metatype:{metatype})',
                    None)
