# -*- coding: utf8 -*-

import re
import time

from .connector import r

redpaduration  = 3600
bluepaduration = 3600

#
# Queries: cds:*
#

def set_cd(pc,skillid,pa):
    ttl       = pa * redpaduration
    mypattern = f'cds:{pc.instance}:{pc.id}:*'
    value     = ''

    try:
        r.set(f'{mypattern}:{skillid}:bearer',pc.id,ttl)
        r.set(f'{mypattern}:{skillid}:duration_base',ttl,ttl)
        r.set(f'{mypattern}:{skillid}:type','cd',ttl)
    except Exception as e:
        print(f'set_cd failed:{e}')
        return False
    else:
        return True

def get_cds(pc):
    mypattern = f'cds:{pc.instance}:{pc.id}'
    cds       = []

    try:
        keys = r.scan_iter(mypattern + ':*:bearer')
    except Exception as e:
        print(f'scan_iter({mypattern}) failed:{e}')

    try:
        for key in keys:
            m = re.match(f"{mypattern}:(\d+)", key.decode("utf-8"))
            if m:
                ts      = int(m.group(1))
                fullkey = mypattern + ':' + f'{ts}'
                ttl     = int(r.ttl(fullkey))
                cd      = {"bearer":          int(r.get(fullkey + ':bearer').decode("utf-8")),
                          "duration_base":   int(r.get(fullkey + ':duration_base').decode("utf-8")),
                          "duration_left":   ttl,
                          "timestamp_start": ts,
                          "timestamp_end":   ts - ttl,
                          "type":            r.get(fullkey + ':type').decode("utf-8")}
            cds.append(cd)
    except Exception as e:
        print(f'CDs fetching failed:{e}')
        return cds
    else:
        return cds
