# -*- coding: utf8 -*-

import prometheus_client as prom
import time

from mod_mysql import *

if __name__ == '__main__':

   sep_count = prom.Gauge('sep_count', 'Actual count of things', ['type'])
   prom.start_http_server(8008)

   while True:
       sep_count.labels('user').set(get_count_table('users'))
       sep_count.labels('pc').set(get_count_table('pjsInfos'))
       sep_count.labels('mp').set(get_count_table('mps'))
       sep_count.labels('squad').set(get_count_table('squads'))
       sep_count.labels('gear').set(get_count_table('gear'))
       sep_count.labels('weapon').set(get_count_table('weapons'))

       time.sleep(30)
