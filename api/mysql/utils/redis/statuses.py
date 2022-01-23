# -*- coding: utf8 -*-

import re
import time

from .connector import r

redpaduration  = 3600
bluepaduration = 3600

#
# Queries: statuses:*
#

def get_statuses(pc):
    mypattern = f'statuses:{pc.instance}:{pc.id}'
    statuses  = []

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
                status = {"bearer":          int(r.get(fullkey + ':bearer').decode("utf-8")),
                          "duration_base":   int(r.get(fullkey + ':duration_base').decode("utf-8")),
                          "duration_left":   ttl,
                          "timestamp_start": ts,
                          "timestamp_end":   ts - ttl,
                          "type":            r.get(fullkey + ':type').decode("utf-8")}
            statuses.append(status)
    except Exception as e:
        print(f'Statuses fetching failed:{e}')
        return statuses
    else:
        return statuses
