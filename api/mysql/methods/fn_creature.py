# -*- coding: utf8 -*-

from flask                      import jsonify
from loguru                     import logger
from random                     import randint

from mysql.session              import Session
from mysql.models               import (Creature,
                                        CreatureStats)

from nosql.metas                import metaRaces
from nosql.publish              import publish
from nosql.queue                import yqueue_put


def fn_creature_add(name,
                    race,
                    gender,
                    accountid,
                    rarity='Medium',
                    x=randint(2, 4),
                    y=randint(2, 5),
                    instanceid=None):
    session = Session()

    try:
        # We grab the race wanted from metaRaces
        metaRace = dict(list(filter(lambda x: x["id"] == race,
                                    metaRaces))[0])  # Gruikfix
        if metaRace is None:
            logger.error(f'MetaRace not found (race:{race})')
            return None

        if metaRace['id'] > 10:
            # We want to create a NPC
            name = metaRace['name']
    except Exception as e:
        msg = f'PC creation KO (name:{name}) [{e}]'
        logger.error(msg)

    try:
        pc = Creature(name=name,
                      race=metaRace['id'],
                      rarity=rarity,
                      gender=gender,
                      account=accountid,
                      hp=100 + metaRace['min_m'],  # TODO: To remove
                      hp_max=100 + metaRace['min_m'],  # TODO: To remove
                      instance=instanceid,
                      x=x,
                      y=y)

        session.add(pc)
        session.commit()
        session.refresh(pc)
    except Exception as e:
        session.rollback()
        msg = f'PC creation KO (name:{name}) [{e}]'
        logger.error(msg)
    else:
        if pc:
            return pc
        else:
            return None
    finally:
        session.close()


def fn_creature_del(creature_todel):
    session = Session()
    h       = f'[Creature.id:{creature_todel.id}]'  # Header for logging

    try:
        creature = session.query(Creature)\
                          .filter(Creature.id == creature_todel.id)\
                          .one_or_none()

        if creature:
            session.delete(creature)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Creature Query KO [{e}]')
        return None
    else:
        return True
    finally:
        session.close()


def fn_creature_get(pcname, pcid):
    session = Session()

    try:
        if pcid:
            pc = session.query(Creature)\
                        .filter(Creature.id == pcid)\
                        .one_or_none()
        elif pcname:
            pc = session.query(Creature)\
                        .filter(Creature.name == pcname)\
                        .one_or_none()
        else:
            message = f'Wrong pcid/pcname (pcid:{pcid},pcname:{pcname})'
            logger.warning(message)
            return (200, False, message, None)
    except Exception as e:
        message = f'[SQL] PC query failed (pcid:{pcid},pcname:{pcname}) [{e}]'
        logger.error(message)
        return (200, False, message, None)
    else:
        if pc:
            message = f'PC successfully found (pcid:{pcid},pcname:{pcname})'
            logger.trace(message)
            return (200, True, message, pc)
        else:
            message = f'PC does not exist (pcid:{pcid},pcname:{pcname})'
            logger.trace(message)
            return (200, False, message, None)
    finally:
        session.close()


def fn_creature_get_all(userid):
    session = Session()

    try:
        pcs    = session.query(Creature)\
                        .filter(Creature.account == userid)\
                        .all()
    except Exception as e:
        message = f'[SQL] PC query KO (userid:{userid}) [{e}]'
        logger.error(message)
        return None
    else:
        if pcs:
            message = f'[SQL] PC successfully found (userid:{userid})'
            logger.trace(message)
            return pcs
        else:
            return []
    finally:
        session.close()


def fn_creature_tag(pc, tg):
    session = Session()
    h       = f'[Creature.id:{pc.id}]'  # Header for logging

    try:
        tg             = session.query(Creature)\
                                .filter(Creature.id == tg.id)\
                                .one_or_none()
        tg.targeted_by = pc.id
        session.commit()
        session.refresh(tg)
    except Exception as e:
        session.rollback()
        message = f'{h} Targeted_by Query KO (tgid:{tg.id}) [{e}]'
        logger.error(message)
        return None
    else:
        message = f'{h} Targeted_by Query KO (tgid:{tg.id})'
        logger.trace(message)
        return tg
    finally:
        session.close()


def fn_creature_kill(pc, tg, action):
    session = Session()

    # As tg object will be destroyed, we store the info for later
    tgid    = tg.id
    tgname  = tg.name

    try:
        tg      = session.query(Creature)\
                         .filter(Creature.id == tg.id)\
                         .one_or_none()
        session.delete(tg)
        session.commit()
    except Exception as e:
        msg = f'Creature DB delete KO ([{tgid}] {tgname}) [{e}]'
        logger.error(msg)
        return False
    else:
        # Creature has been deleted from DB
        msg = f'Creature DB delete OK ([{tgid}] {tgname})'
        logger.trace(msg)
        # Now we send the WS messages
        # Broadcast Queue
        queue = 'broadcast'
        qmsg = {
            "ciphered": False,
            "payload": {
                "id": pc.id,
                "target": {
                    "id": tg.id,
                    "name": tg.name
                },
                "action": None
            },
            "route": "mypc/{id1}/action/resolver/skill/{id2}",
            "scope": {
                "id": None,
                "scope": 'broadcast'
            }
        }
        try:
            yqueue_put(queue, qmsg)
        except Exception as e:
            msg = f'Queue PUT KO (queue:{queue}) [{e}]'
            logger.error(msg)
        else:
            msg = f'Queue PUT OK (queue:{queue})'
            logger.trace(msg)

        # Discord Queue
        queue = 'yarqueue:discord'
        if pc.squad is not None:
            scope = f'Squad-{pc.squad}'
        else:
            scope = None
        qmsg = {
            "ciphered": False,
            "payload":
                (f':pirate_flag: **[{pc.id}] '
                 f'{pc.name}** killed **[{tgid}] {tgname}**'),
            "embed": None,
            "scope": scope,
        }
        try:
            yqueue_put(queue, qmsg)
        except Exception as e:
            msg = f'Queue PUT KO (queue:{queue}) [{e}]'
            logger.error(msg)
        else:
            msg = f'Queue PUT OK (queue:{queue})'
            logger.trace(msg)

        # We put the info in pubsub channel for IA to regulate the instance
        try:
            pmsg     = {"action": 'kill',
                        "instance": None,
                        "creature": tg}
            pchannel = 'ai-creature'
            publish(pchannel, jsonify(pmsg).get_data())
        except Exception as e:
            msg = f'Publish({pchannel}) KO [{e}]'
            logger.error(msg)
        else:
            logger.trace(f'Publish({pchannel}) OK')

        msg = f'Creature Kill OK ([{tgid}] {tgname})'
        logger.trace(msg)
        return True
    finally:
        session.close()


def fn_creature_xp_add(pc, xp):
    session = Session()
    h       = f'[Creature.id:{pc.id}]'  # Header for logging

    try:
        pc = session.query(Creature)\
                    .filter(Creature.id == pc.id)\
                    .one_or_none()
        pc.xp  += xp
        session.commit()
    except Exception as e:
        session.rollback()
        msg = f'{h} XP update KO (xp:{xp}) [{e}]'
        logger.error(msg)
        return None
    else:
        msg = f'{h} XP update OK (xp:{xp})'
        logger.trace(msg)
        return True
    finally:
        session.close()


def fn_creature_stats_add(creature, metaRace, pcclass):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        stats = CreatureStats(id=creature.id,
                              m_race=metaRace['min_m'],
                              r_race=metaRace['min_r'],
                              g_race=metaRace['min_g'],
                              v_race=metaRace['min_v'],
                              p_race=metaRace['min_p'],
                              b_race=metaRace['min_b'])

        if pcclass == '1':
            stats.m_class = 10
        if pcclass == '2':
            stats.r_class = 10
        if pcclass == '3':
            stats.g_class = 10
        if pcclass == '4':
            stats.v_class = 10
        if pcclass == '5':
            stats.p_class = 10
        if pcclass == '6':
            stats.b_class = 10

        session.add(stats)
        session.commit()
        session.refresh(stats)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Stats Query KO [{e}]')
        return None
    else:
        if stats:
            logger.trace(f'{h} Stats Query OK')
            return stats
        else:
            return None
    finally:
        session.close()


def fn_creature_stats_del(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        stats = session.query(CreatureStats)\
                       .filter(CreatureStats.id == creature.id)\
                       .one_or_none()

        if stats:
            session.delete(stats)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Stats Query KO [{e}]')
        return None
    else:
        logger.trace(f'{h} Stats Query OK')
        return True
    finally:
        session.close()


def fn_creature_stats_get(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        stats = session.query(CreatureStats)\
                       .filter(CreatureStats.id == creature.id)\
                       .one_or_none()
    except Exception as e:
        logger.error(f'{h} Stats Query KO [{e}]')
        return None
    else:
        logger.trace(f'{h} Stats Query OK')
        return stats
    finally:
        session.close()


def fn_creature_position_set(creatureid, x, y):
    session = Session()

    try:
        creature = session.query(Creature)\
                          .filter(Creature.id == creatureid)\
                          .one_or_none()

        if creature:
            h = f'[Creature.id:{creature.id}]'  # Header for logging
            creature.x = x
            creature.y = y
        else:
            h = '[Creature.id:None'  # Header for logging
            logger.warning(f'{h} Creature Query KO - NotFound')

        session.commit()
        session.refresh(creature)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Creature Query KO [{e}]')
        return None
    else:
        if creature:
            logger.trace(f'{h} Creature Query OK')
            return creature
        else:
            logger.warning(f'{h} Creature Query KO - NotFound')
            return None
    finally:
        session.close()
