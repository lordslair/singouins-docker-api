# -*- coding: utf8 -*-

from sqlalchemy     import create_engine
from sqlalchemy.orm import sessionmaker

from datetime  import datetime

from utils     import tables
from variables import SQL_DSN

import textwrap

engine     = create_engine('mysql+pymysql://' + SQL_DSN, pool_recycle=3600)

#def ratio(points):
#    if   0  <= points <=  60: return points
#    elif 60 <  points <=  75: return 60+(points-60)*0.75
#    elif 90 <  points <= 100: return 80+(points-90)*0.25

def calc(pcid):
    Session = sessionmaker(bind=engine)
    session = Session()

    with engine.connect() as conn:
        try:
            pc    = session.query(tables.PJ).filter(tables.PJ.id == pcid).one_or_none()
            stats = session.query(tables.CreaturesStats).filter(tables.CreaturesStats.id == pcid).one_or_none()
            if pc and stats:
                pc.m = 100 + stats.m_race + round(pc.level * 0.3) + round(stats.m_skill / 2) + min(stats.m_point,80)
                pc.r = 100 + stats.r_race + round(pc.level * 0.3) + round(stats.r_skill / 2) + min(stats.r_point,80)
                pc.g = 100 + stats.g_race + round(pc.level * 0.3) + round(stats.g_skill / 2) + min(stats.g_point,80)
                pc.v = 100 + stats.v_race + round(pc.level * 0.3) + round(stats.v_skill / 2) + min(stats.v_point,80)
                pc.p = 100 + stats.p_race + round(pc.level * 0.3) + round(stats.p_skill / 2) + min(stats.p_point,80)
                pc.b = 100 + stats.b_race + round(pc.level * 0.3) + round(stats.b_skill / 2) + min(stats.b_point,80)

                print(pc)

                session.commit()
        except Exception as e:
            # Something went wrong during commit
            print("Oops")
            return (200, False, 'Stats update failed', None)
        else:
            print(stats.m_race,round(pc.level * 0.3),round(stats.m_skill / 2),min(stats.m_point,80),pc.m)
            print(stats.r_race,round(pc.level * 0.3),round(stats.r_skill / 2),min(stats.r_point,80),pc.r)
            print(stats.g_race,round(pc.level * 0.3),round(stats.g_skill / 2),min(stats.g_point,80),pc.g)
            print(stats.v_race,round(pc.level * 0.3),round(stats.v_skill / 2),min(stats.v_point,80),pc.v)
            print(stats.p_race,round(pc.level * 0.3),round(stats.p_skill / 2),min(stats.p_point,80),pc.p)
            print(stats.b_race,round(pc.level * 0.3),round(stats.b_skill / 2),min(stats.b_point,80),pc.b)
            return (200, True, 'Stats successfully updated', pc)

calc(1)
print("\n")
calc(2)
