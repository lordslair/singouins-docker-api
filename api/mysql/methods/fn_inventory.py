# -*- coding: utf8 -*-

from loguru                     import logger

from mysql.session              import Session
from mysql.models               import (Cosmetic,
                                        Item)

from nosql.metas                import metaWeapons

#
# Cosmetics
#


def fn_cosmetic_add(creature, pccosmetic):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        cosmetic = Cosmetic(metaid=pccosmetic['metaid'],
                            bearer=creature.id,
                            bound=1,
                            bound_type='BoP',
                            state=99,
                            rarity='Epic',
                            data=str(pccosmetic['data']))

        session.add(cosmetic)
        session.expunge(cosmetic)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Cosmetic Query KO [{e}]')
        return None
    else:
        if cosmetic:
            logger.trace(f'{h} Cosmetic Query OK')
            return cosmetic
        else:
            logger.warning(f'{h} Cosmetic Query KO')
            return None
    finally:
        session.close()


def fn_cosmetic_del(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        cosmetic = session.query(Cosmetic)\
                          .filter(Cosmetic.bearer == creature.id)\
                          .one_or_none()

        if cosmetic:
            session.delete(cosmetic)

        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Cosmetic Query KO [{e}]')
        return None
    else:
        logger.trace(f'{h} Cosmetic Query OK')
        return True
    finally:
        session.close()


def fn_cosmetics_get_all(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        result = session.query(Cosmetic)\
                        .filter(Cosmetic.bearer == creature.id)\
                        .all()
    except Exception as e:
        logger.error(f'{h} Cosmetic Query KO [{e}]')
        return None
    else:
        logger.trace(f'{h} Cosmetic Query OK')
        return result
    finally:
        session.close()


#
# Item
#
def fn_item_ammo_set(itemid, ammo):
    session = Session()

    try:
        item = session.query(Item)\
                      .filter(Item.id == itemid)\
                      .one_or_none()
        item.ammo = ammo
        session.commit()
        session.refresh(item)
    except Exception as e:
        logger.error(f'Item Query KO [{e}]')
        return None
    else:
        if item:
            logger.trace('Item Query OK')
            return item
        else:
            logger.warning('Item Query KO')
            return None
    finally:
        session.close()


def fn_item_owner_set(itemid, ownerid):
    session = Session()

    if itemid is None:
        return None

    try:
        item = session.query(Item)\
                      .filter(Item.id == itemid)\
                      .one_or_none()

        item.bearer = ownerid
        session.commit()
        session.refresh(item)
    except Exception as e:
        session.rollback()
        logger.error(f'Item Query KO [{e}]')
        return None
    else:
        logger.trace('Item Query OK')
        return item
    finally:
        session.close()


def fn_item_get_one(itemid):
    session = Session()

    if itemid is None:
        return None

    try:
        result = session.query(Item)\
                        .filter(Item.id == itemid)\
                        .one_or_none()
    except Exception as e:
        logger.error(f'Item Query KO [{e}]')
        return None
    else:
        logger.trace('Item Query OK')
        return result
    finally:
        session.close()


def fn_item_get_all(creature):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        result = session.query(Item)\
                        .filter(Item.bearer == creature.id)\
                        .all()
    except Exception as e:
        logger.error(f'{h} Item Query KO [{e}]')
        return None
    else:
        logger.trace('Item Query OK')
        return result
    finally:
        session.close()


def fn_item_add(creature, item_caracs):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        item   = Item(metatype=item_caracs['metatype'],
                      metaid=item_caracs['metaid'],
                      bearer=creature.id,
                      bound=item_caracs['bound'],
                      bound_type=item_caracs['bound_type'],
                      modded=item_caracs['modded'],
                      mods=item_caracs['mods'],
                      state=item_caracs['state'],
                      rarity=item_caracs['rarity'],
                      offsetx=None,
                      offsety=None)

        if item.metatype == 'weapon':
            # We grab the weapon wanted from metaWeapons
            metaWeapon = dict(list(filter(lambda x: x["id"] == item.metaid,
                                          metaWeapons))[0])  # Gruikfix
            # item.ammo is by default None, we initialize it here
            if metaWeapon['ranged'] is True:
                item.ammo = metaWeapon['max_ammo']

        session.add(item)
        session.commit()
        session.refresh(item)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Item Query KO [{e}]')
        return None
    else:
        if item:
            logger.trace(f'{h} Item Query OK')
            return item
        else:
            logger.trace(f'{h} Item Query KO - NotFound')
            return None
    finally:
        session.close()


def fn_item_del(creature, itemid):
    session = Session()
    h       = f'[Creature.id:{creature.id}]'  # Header for logging

    try:
        item = session.query(Item)\
                      .filter(Item.id == itemid)\
                      .one_or_none()

        session.delete(item)
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Item Query KO [{e}]')
        return None
    else:
        logger.trace(f'{h} Item Query OK')
        return True
    finally:
        session.close()


def fn_item_offset_set(itemid, offsetx, offsety):
    session = Session()
    h       = '[Creature.id:None]'  # Header for logging

    try:
        item = session.query(Item)\
                      .filter(Item.id == itemid)\
                      .one_or_none()

        item.offsetx = offsetx
        item.offsety = offsety
        session.commit()
        session.refresh(item)
    except Exception as e:
        session.rollback()
        logger.error(f'{h} Item Query KO [{e}]')
        return None
    else:
        if item:
            logger.trace(f'{h} Item Query OK')
            return item
        else:
            logger.warning(f'{h} Item Query KO - NotFound')
            return None
    finally:
        session.close()
