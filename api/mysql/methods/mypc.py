# -*- coding: utf8 -*-

from random                import randint

from ..session             import Session
from ..models              import (Cosmetic,
                                   Creature,
                                   CreatureSlots,
                                   CreatureStats,
                                   Item,
                                   Wallet)

from .fn_creature          import *
from .fn_user              import fn_user_get

# Loading the Meta for later use
try:
    metaRaces   = metas.get_meta('race')
    metaWeapons = metas.get_meta('weapon')
except Exception as e:
    logger.error(f'Meta fectching: KO [{e}]')
else:
    logger.trace(f'Meta fectching: OK')

#
# Queries /mypc/*
#

# API: POST /mypc
def mypc_create(username,pcname,pcrace,pcclass,pcequipment,pccosmetic,pcgender):
    session = Session()

    mypc_nbr = mypc_get_all(username)[3]
    if mypc_nbr:
        if len(mypc_nbr) >= 3:
            return (200,
                    False,
                    f'PC quota reached (username:{username},pccount:{len(mypc_nbr)})',
                    None)

    if fn_creature_get(pcname,None)[1]:
        return (409,
                False,
                f'PC already exists (username:{username},pcname:{pcname})',
                None)
    else:
        # We grab the race wanted from metaRaces
        metaRace = dict(list(filter(lambda x:x["id"] == pcrace,metaRaces))[0]) # Gruikfix
        if metaRace is None:
            return (200,
                    False,
                    f'MetaRace not found (race:{pcrace})',
                    None)

        pc = Creature(name    = pcname,
                      race    = metaRace['id'],
                      gender  = pcgender,
                      account = fn_user_get(username).id,
                      hp      = 100 + metaRace['min_m'], # TODO: To remove
                      hp_max  = 100 + metaRace['min_m'], # TODO: To remove
                      instance = None,        # Gruikfix for now
                      x       = randint(2,4), # TODO: replace with rand(empty coords)
                      y       = randint(2,5)) # TODO: replace with rand(empty coords)

        session.add(pc)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            session.rollback()
            return (200,
                    False,
                    f'[SQL] PC creation failed (username:{username},pcname:{pcname}) [{e}]',
                    None)
        else:
                cosmetic = Cosmetic(metaid = pccosmetic['metaid'],
                                    bearer = pc.id,
                                    bound = 1,
                                    bound_type = 'BoP',
                                    state = 99,
                                    rarity = 'Epic',
                                    data = str(pccosmetic['data']))

                pc        = fn_creature_get(pcname,None)[3]
                equipment = CreatureSlots(id = pc.id)
                wallet    = Wallet(id = pc.id)

                stats     = CreatureStats(id = pc.id,
                                          m_race = metaRace['min_m'],
                                          r_race = metaRace['min_r'],
                                          g_race = metaRace['min_g'],
                                          v_race = metaRace['min_v'],
                                          p_race = metaRace['min_p'],
                                          b_race = metaRace['min_b'])

                session.add(equipment)
                session.add(wallet)
                session.add(stats)
                session.add(cosmetic)

                if pcclass == '1': stats.m_class = 10
                if pcclass == '2': stats.r_class = 10
                if pcclass == '3': stats.g_class = 10
                if pcclass == '4': stats.v_class = 10
                if pcclass == '5': stats.p_class = 10
                if pcclass == '6': stats.b_class = 10

                try:
                    session.commit()
                except Exception as e:
                    # Something went wrong during commit
                    session.rollback()
                    return (200,
                            False,
                            f'[SQL] PC Cosmetics/Slots/Wallet/Stats creation failed [{e}]',
                            None)
                else:
                    # Money is added
                    wallet.currency = 250

                    if pcequipment:
                        # Items are added
                        if pcequipment['righthand'] is not None:
                            rh   = Item(metatype   = pcequipment['righthand']['metatype'],
                                        metaid     = pcequipment['righthand']['metaid'],
                                        bearer     = pc.id,
                                        bound      = True,
                                        bound_type = 'BoP',
                                        modded     = False,
                                        mods       = None,
                                        state      = 100,
                                        rarity     = 'Common',
                                        offsetx    = 0,
                                        offsety    = 0,
                                        date       = datetime.now())
                            session.add(rh)

                            if rh.metatype == 'weapon':
                                # We grab the weapon wanted from metaWeapons
                                metaWeapon = dict(list(filter(lambda x:x["id"] == rh.metaid,metaWeapons))[0]) # Gruikfix
                                # item.ammo is by default None, we initialize it here
                                if metaWeapon['ranged'] == True:
                                    rh.ammo = metaWeapon['max_ammo']

                        if pcequipment['lefthand'] is not None:
                            lh   = Item(metatype   = pcequipment['lefthand']['metatype'],
                                    metaid     = pcequipment['lefthand']['metaid'],
                                    bearer     = pc.id,
                                    bound      = True,
                                    bound_type = 'BoP',
                                    modded     = False,
                                    mods       = None,
                                    state      = 100,
                                    rarity     = 'Common',
                                    offsetx    = 4,
                                    offsety    = 0,
                                    date       = datetime.now())
                            session.add(lh)

                            if lh.metatype == 'weapon':
                                # We grab the weapon wanted from metaWeapons
                                metaWeapon = dict(list(filter(lambda x:x["id"] == lh.metaid,metaWeapons))[0]) # Gruikfix
                                # item.ammo is by default None, we initialize it here
                                if metaWeapon['ranged'] == True:
                                    lh.ammo = metaWeapon['max_ammo']

                    try:
                        session.commit()
                    except Exception as e:
                        # Something went wrong during commit
                        session.rollback()
                        return (200,
                                False,
                                f'[SQL] PC Wallet/Inventory population failed [{e}]',
                                None)
                    else:
                        return (201,
                                True,
                                f'PC successfully created (pcid:{pc.id})',
                                pc)
        finally:
            session.close()

# API: GET /mypc
def mypc_get_all(username):
    session = Session()

    try:
        userid = fn_user_get(username).id
        pcs    = session.query(Creature).filter(Creature.account == userid).all()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[SQL] PCs query failed (username:{username}) [{e}]',
                None)
    else:
        if pcs:
            return (200,
                    True,
                    f'PCs successfully found (username:{username})',
                    pcs)
        else:
            return (200,
                    False,
                    f'No PC found for this user (username:{username})',
                    None)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>
def mypc_get_one(username,pcid):
    session = Session()

    try:
        userid = fn_user_get(username).id
        pcs    = session.query(Creature)\
                        .filter(Creature.account == userid, Creature.id == pcid)\
                        .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[SQL] PC query failed (username:{username},pcid:{pcid}) [{e}]',
                None)
    else:
        if pcs:
            return (200,
                    True,
                    f'PCs successfully found (username:{username},pcid:{pcid})',
                    pcs)
        else:
            return (200,
                    False,
                    f'No PC found for this user (username:{username},pcid:{pcid})',
                    None)
    finally:
        session.close()


# API: DELETE /mypc/<int:pcid>
def mypc_del(username,pcid):
    session = Session()

    if not fn_creature_get(None,pcid)[3]:
        return (200,
                False,
                f'PC does not exist (pcid:{pcid})',
                None)

    try:
        userid    = fn_user_get(username).id

        pc        = session.query(Creature).filter(Creature.account == userid, Creature.id == pcid).one_or_none()
        equipment = session.query(CreatureSlots).filter(CreatureSlots.id == pc.id).one_or_none()
        wallet    = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()
        stats     = session.query(CreatureStats).filter(CreatureStats.id == pc.id).one_or_none()
        cosmetics = session.query(Cosmetic).filter(Cosmetic.bearer == pc.id).one_or_none()

        if pc: session.delete(pc)
        if equipment: session.delete(equipment)
        if wallet: session.delete(wallet)
        if stats: session.delete(stats)
        if cosmetics: session.delete(cosmetics)

        items = session.query(Item).filter(Item.bearer == pc.id).all()
        if items:
            for item in items:
                # To archive the item without deleting it
                item.bearer  = None
                item.offsetx = None
                item.offsety = None

        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                f'[SQL] PC deletion failed (username:{username},pcid:{pcid}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'PC successfully deleted (username:{username},pcid:{pcid})',
                None)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>/stats
def mypc_get_stats(pc):

    # We check if we have the data in redis
    creature_stats = stats.get_stats(pc)
    if creature_stats:
        # Data was in Redis, so we return it
        return (200,
                True,
                f'Stats Redis query successed (pcid:{pc.id})',
                creature_stats)

    # Data was not in Redis, so we compute it
    creature_stats = fn_creature_stats(pc)
    if creature_stats:
        # Data was computed, so we return it
        return (200,
                True,
                f'Stats computation successed (pcid:{pc.id})',
                creature_stats)
    else:
        # Data computation failed
        return (200,
                False,
                f'Stats computation failed (pcid:{pc.id})',
                None)

# API: GET /mypc/<int:pcid>/cds
def mypc_get_cds(username,pcid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    try:
        creature_cds = cds.get_cds(pc)
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                f'[Redis] CDs query failed (pcid:{pc.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'CDs found (pcid:{pc.id})',
                creature_cds)
    finally:
        session.close()

# API: GET /mypc/<int:pcid>/effects
def mypc_get_effects(username,pcid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)

    # Pre-flight checks
    if pc is None:
        return (200,
                False,
                f'PC not found (pcid:{pcid})',
                None)
    if pc.account != user.id:
        return (409,
                False,
                f'Token/username mismatch (pcid:{pcid},username:{username})',
                None)

    try:
        creature_effects = effects.get_effects(pc)
    except Exception as e:
        return (200,
                False,
                f'[Redis] Effects query failed (pcid:{pc.id}) [{e}]',
                None)
    else:
        return (200,
                True,
                f'Effects found (pcid:{pc.id})',
                creature_effects)
