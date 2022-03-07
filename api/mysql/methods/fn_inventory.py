# -*- coding: utf8 -*-

from ..session          import Session
from ..models.items     import Cosmetic,Item
from ..models.creatures import CreatureSlots,Wallet

from nosql              import * # Custom internal module for Redis queries

# Loading the Meta for later use
try:
    metaWeapons = metas.get_meta('weapon')
except Exception as e:
    logger.error(f'Meta fectching: KO [{e}]')
else:
    logger.trace(f'Meta fectching: OK')

#
# Cosmetics
#

def fn_cosmetic_add(pc,pccosmetic):
    session = Session()

    try:
        cosmetic = Cosmetic(metaid     = pccosmetic['metaid'],
                            bearer     = pc.id,
                            bound      = 1,
                            bound_type = 'BoP',
                            state      = 99,
                            rarity     = 'Epic',
                            data       = str(pccosmetic['data']))

        session.add(cosmetic)
        session.expunge(cosmetic)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'Cosmetic Query KO [{e}]')
        return None
    else:
        if cosmetic:
            return cosmetic
        else:
            return None
    finally:
        session.close()

def fn_cosmetic_del(pc):
    session = Session()

    try:
        cosmetic = session.query(Cosmetic)\
                          .filter(Cosmetic.bearer == pc.id)\
                          .one_or_none()

        if cosmetic: session.delete(cosmetic)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'Cosmetic Query KO [{e}]')
        return None
    else:
        return True
    finally:
        session.close()

def fn_cosmetics_get_all(creature):
    session = Session()

    try:
        result = session.query(Cosmetic)\
                        .filter(Cosmetic.bearer == creature.id)\
                        .all()
    except Exception as e:
        logger.error(f'Cosmetic Query KO [{e}]')
        return None
    else:
        return result
    finally:
        session.close()

#
# Item
#

def fn_item_get_one(itemid):
    session = Session()

    if itemid is None: return None

    try:
       result = session.query(Item)\
                       .filter(Item.id == itemid)\
                       .one_or_none()
    except Exception as e:
        logger.error(f'Item Query KO [{e}]')
        return None
    else:
        return result
    finally:
        session.close()

def fn_item_get_all(creature):
    session = Session()

    try:
       result = session.query(Item)\
                       .filter(Item.bearer == creature.id)\
                       .all()
    except Exception as e:
        logger.error(f'Item Query KO [{e}]')
        return None
    else:
        return result
    finally:
        session.close()

def fn_item_add(pc,item_caracs):
    session = Session()

    try:
        item   = Item(metatype   = item_caracs['metatype'],
                      metaid     = item_caracs['metaid'],
                      bearer     = pc.id,
                      bound      = item_caracs['bound'],
                      bound_type = item_caracs['bound_type'],
                      modded     = item_caracs['modded'],
                      mods       = item_caracs['mods'],
                      state      = item_caracs['state'],
                      rarity     = item_caracs['rarity'],
                      offsetx    = None,
                      offsety    = None)

        if item.metatype == 'weapon':
            # We grab the weapon wanted from metaWeapons
            metaWeapon = dict(list(filter(lambda x:x["id"] == item.metaid,metaWeapons))[0]) # Gruikfix
            # item.ammo is by default None, we initialize it here
            if metaWeapon['ranged'] == True:
                item.ammo = metaWeapon['max_ammo']

        session.add(item)
        session.commit()
        session.refresh(item)
    except Exception as e:
        session.rollback()
        logger.error(f'Item Query KO [{e}]')
        return None
    else:
        if item:
            return item
        else:
            return None
    finally:
        session.close()

#
# Slots
#

def fn_slots_add(creature):
    session = Session()

    try:
        slots = CreatureSlots(id = creature.id)

        session.add(slots)
        session.commit()
        session.refresh(slots)
    except Exception as e:
        session.rollback()
        logger.error(f'Slots Query KO [{e}]')
        return None
    else:
        if slots:
            return slots
        else:
            return None
    finally:
        session.close()

def fn_slots_get_all(creature):
    session = Session()

    try:
        result = session.query(CreatureSlots)\
                        .filter(CreatureSlots.id == creature.id)\
                        .all()
    except Exception as e:
        logger.error(f'Slots Query KO [{e}]')
        return None
    else:
        return result
    finally:
        session.close()

def fn_slots_del(creature):
    session = Session()

    try:
        slots = session.query(CreatureSlots)\
                       .filter(CreatureSlots.id == creature.id)\
                       .one_or_none()

        if slots: session.delete(slots)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'Slots Query KO [{e}]')
        return None
    else:
        return True
    finally:
        session.close()

#
# Wallet
#

def fn_wallet_add(creature):
    session = Session()

    try:
        wallet = Wallet(id = creature.id)

        # Money is added
        wallet.currency = 250

        session.add(wallet)
        session.commit()
        session.refresh(wallet)
    except Exception as e:
        session.rollback()
        logger.error(f'Wallet Query KO [{e}]')
        return None
    else:
        if wallet:
            return wallet
        else:
            return None
    finally:
        session.close()

def fn_wallet_del(creature):
    session = Session()

    try:
        wallet = session.query(Wallet)\
                        .filter(Wallet.id == creature.id)\
                        .one_or_none()

        if wallet: session.delete(wallet)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'Wallet Query KO [{e}]')
        return None
    else:
        return True
    finally:
        session.close()

def fn_wallet_get(creature):
    session = Session()

    try:
        wallet = session.query(Wallet)\
                        .filter(Wallet.id == creature.id)\
                        .one_or_none()
    except Exception as e:
        session.rollback()
        logger.error(f'Wallet Query KO [{e}]')
        return None
    else:
        if wallet:
            return wallet
        else:
            return None
    finally:
        session.close()
