# -*- coding: utf8 -*-

import dataclasses      # Needed for WS JSON broadcast

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get
from .fn_global         import clog

#
# Queries /mypc/{pcid}/inventory/*
#

# API: /mypc/<int:pcid>/inventory/item/<int:itemid>/dismantle
def mypc_inventory_item_dismantle(username,pcid,itemid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()
    bluepa      = get_pa(pcid)[3]['blue']['pa']

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    if bluepa < 1:
        return (200,
                False,
                'Not enough PA (pcid:{},bluepa:{})'.format(pcid,bluepa),
                None)

    item = session.query(Item)\
                  .filter(Item.id == itemid)\
                  .one_or_none()

    if item is None:
        # Item not found
        return (200,
                False,
                'Item not found (pcid:{},itemid:{})'.format(pcid,itemid),
                None)

    if   item.rarity == 'Broken':
        shards = [6,0,0,0,0,0]
        incr_hs(pc,f'action:dismantle:shards:{item.rarity}', shards[0]) # Redis HighScore
    elif item.rarity == 'Common':
        shards = [0,5,0,0,0,0]
        incr_hs(pc,f'action:dismantle:shards:{item.rarity}', shards[1]) # Redis HighScore
    elif item.rarity == 'Uncommon':
        shards = [0,0,4,0,0,0]
        incr_hs(pc,f'action:dismantle:shards:{item.rarity}', shards[2]) # Redis HighScore
    elif item.rarity == 'Rare':
        shards = [0,0,0,3,0,0]
        incr_hs(pc,f'action:dismantle:shards:{item.rarity}', shards[3]) # Redis HighScore
    elif item.rarity == 'Epic':
        shards = [0,0,0,0,2,0]
        incr_hs(pc,f'action:dismantle:shards:{item.rarity}', shards[4]) # Redis HighScore
    elif item.rarity == 'Legendary':
        shards = [0,0,0,0,0,1]
        incr_hs(pc,f'action:dismantle:shards:{item.rarity}', shards[5]) # Redis HighScore

    try:
        wallet = session.query(Wallet).filter(Wallet.id == pc.id).one_or_none()

        wallet.broken    += shards[0]
        wallet.common    += shards[1]
        wallet.uncommon  += shards[2]
        wallet.rare      += shards[3]
        wallet.epic      += shards[4]
        wallet.legendary += shards[5]

        session.delete(item)

        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Wallet update failed (pcid:{})'.format(pc.id),
                None)
    else:
        set_pa(pcid,0,1) # We consume the blue PA (1)
        incr_hs(pc,'action:dismantle:items', 1) # Redis HighScore
        return (200,
                True,
                'Item dismantle successed (pcid:{},itemid:{})'.format(pc.id,item.id),
                {"shards": {
                    "Broken":    shards[0],
                    "Common":    shards[1],
                    "Uncommon":  shards[2],
                    "Rare":      shards[3],
                    "Epic":      shards[4],
                    "Legendary": shards[5]}
                })
    finally:
        session.close()

# API: /mypc/<int:pcid>/inventory/item/<int:itemid>/equip/<string:type>/<string:slotname>
def mypc_inventory_item_equip(username,pcid,type,slotname,itemid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()
    redpa       = get_pa(pcid)[3]['red']['pa']
    equipment   = session.query(CreatureSlots).filter(CreatureSlots.id == pc.id).one_or_none()

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    if equipment is None:
        return (200,
                False,
                f'Equipment not found (pcid:{pc.id})',
                None)

    stats = get_stats(pc)
    print(stats)
    if stats is None:
        return (200,
                False,
                f'Stats not found (pcid:{pc.id})',
                None)

    if itemid <= 0:
        # Weird weaponid
        return (200,
                False,
                f'Itemid incorrect (pcid:{pc.id},itemid:{itemid})',
                None)

    if   type == 'weapon':
         item     = session.query(Item).filter(Item.id == itemid, Item.bearer == pc.id).one_or_none()
         itemmeta = session.query(MetaWeapon).filter(MetaWeapon.id == item.metaid).one_or_none()
    elif type == 'armor':
         item     = session.query(Item).filter(Item.id == itemid, Item.bearer == pc.id).one_or_none()
         itemmeta = session.query(MetaArmor).filter(MetaArmor.id == item.metaid).one_or_none()

    if item is None:
        return (200,
                False,
                f'Item not found (pcid:{pc.id},itemid:{itemid})',
                None)
    if itemmeta is None:
        return (200,
                False,
                f'ItemMeta not found (pcid:{pc.id},itemid:{itemid})',
                None)

    sizex,sizey = itemmeta.size.split("x")
    costpa      = round(int(sizex) * int(sizey) / 2)
    if redpa < costpa:
        return (200,
                False,
                f'Not enough PA (pcid:{pc.id},redpa:{redpa},cost:{costpa})',
                None)

    # Pre-requisite checks
    if itemmeta.min_m > stats['base']['m']:
        return (200,
                False,
                f"M prequisites failed (m_min:{itemmeta.min_m},m:{stats['base']['m']})",
                None)
    elif itemmeta.min_r > stats['base']['r']:
        return (200,
                False,
                f"R prequisites failed (r_min:{itemmeta.min_r},r:{stats['base']['r']})",
                None)
    elif itemmeta.min_g > stats['base']['g']:
        return (200,
                False,
                f"G prequisites failed (g_min:{itemmeta.min_g},g:{stats['base']['g']})",
                None)
    elif itemmeta.min_v > stats['base']['v']:
        return (200,
                False,
                f"V prequisites failed (v_min:{itemmeta.min_v},v:{stats['base']['v']})",
                None)
    elif itemmeta.min_p > stats['base']['p']:
        return (200,
                False,
                f"P prequisites failed (p_min:{itemmeta.min_p},p:{stats['base']['p']})",
                None)
    elif itemmeta.min_b > stats['base']['b']:
        return (200,
                False,
                f"B prequisites failed (b_min:{itemmeta.min_b},b:{stats['base']['b']})",
                None)

    # The item to equip exists, is owned by the PC, and we retrieved his equipment from DB
    if   slotname == 'head':      equipment.head      = item.id
    elif slotname == 'shoulders': equipment.shoulders = item.id
    elif slotname == 'torso':     equipment.torso     = item.id
    elif slotname == 'hands':     equipment.hands     = item.id
    elif slotname == 'legs':      equipment.legs      = item.id
    elif slotname == 'feet':      equipment.feet      = item.id
    elif slotname == 'holster':
        if int(sizex) * int(sizey) <= 4:
            # It fits inside the holster
            equipment.holster  = item.id
        else:
            return (200,
                    False,
                    f'Item does not fit in holster (itemid:{item.id},size:{itemmeta.size})',
                    None)
    elif slotname == 'righthand':
        equipped     = session.query(Item).filter(Item.id == equipment.righthand, Item.bearer == pc.id).one_or_none()
        if equipped:
            # Something is already in RH
            equippedmeta = session.query(MetaWeapon).filter(MetaWeapon.id == equipped.metaid).one_or_none()
            # We equip a 1H weapon
            if int(sizex) * int(sizey) <= 6:
                if equippedmeta.onehanded is True:
                    # A 1H weapons is in RH : we replace
                    equipment.righthand  = item.id
                if equippedmeta.onehanded is False:
                    # A 2H weapons is in RH & LH : we replace RH and clean LH
                    equipment.righthand  = item.id
                    equipment.lefthand   = None
            # We equip a 2H weapon
            if int(sizex) * int(sizey) > 6:
                # It is a 2H weapon: it fits inside the RH & LH
                equipment.righthand  = item.id
                equipment.lefthand   = item.id
        else:
            # Nothing in RH
            # We equip a 1H weapon
            if int(sizex) * int(sizey) <= 6:
                equipment.righthand  = item.id
            # We equip a 2H weapon
            if int(sizex) * int(sizey) > 6:
                # It is a 2H weapon: it fits inside the RH & LH
                equipment.righthand  = item.id
                equipment.lefthand   = item.id
    elif slotname == 'lefthand':
        if int(sizex) * int(sizey) <= 4:
            # It fits inside the left hand
            equipment.lefthand   = item.id
        else:
            return (200,
                    False,
                    f'Item does not fit in left hand (itemid:{item.id},size:{itemmeta.size})',
                    None)

    equipment.date = datetime.now() # We update the date in DB
    item.bound     = True           # In case the item was not bound to PC. Now it is
    item.offsetx   = None           # Now the item is not in inventory anymore
    item.offsety   = None           # Now the item is not in inventory anymore
    item.date      = datetime.now() # We update the date in DB

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return (200,
                False,
                f'[SQL] Equipment update failed (pcid:{pc.id},itemid:{itemid})',
                None)
    else:
        equipment = session.query(CreatureSlots)\
                           .filter(CreatureSlots.id == pc.id)\
                           .one_or_none()

        # We need to convert datetime to str before dumping it as a dict
        equipment.date = equipment.date.strftime('%Y-%m-%d %H:%M:%S')

        # We put the info in queue for ws
        qciphered = False
        qpayload  = dataclasses.asdict(equipment)
        qscope    = {"id": None, "scope": 'broadcast'}
        qmsg = {"ciphered": qciphered,
                "payload": qpayload,
                "route": "mypc/{id1}/inventory/item/{id2}/equip/{id3}/{id4}",
                "scope": qscope}
        yqueue_put('broadcast', qmsg)

        set_pa(pc.id,costpa,0) # We consume the red PA (costpa) right now

        return (200,
                True,
                f'Equipment successfully updated (pcid:{pc.id},itemid:{itemid})',
                {"red": get_pa(pcid)[3]['red'],
                 "blue": get_pa(pcid)[3]['blue'],
                 "equipment": equipment})
    finally:
        session.close()

# API: /mypc/<int:pcid>/inventory/item/<int:itemid>/unequip/<string:type>/<string:slotname>
def mypc_inventory_item_unequip(username,pcid,type,slotname,itemid):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()
    equipment   = session.query(CreatureSlots).filter(CreatureSlots.id == pc.id).one_or_none()

    if pc and pc.account != user.id:
        return (409, False, 'Token/username mismatch', None)

    if equipment is None:
        return (200,
                False,
                'Equipment not found (pcid:{},itemid:{})'.format(pcid,itemid),
                None)

    if   slotname == 'head':
        if equipment.head == itemid:
            equipment.head = None
    elif slotname == 'shoulders':
        if equipment.shoulders == itemid:
            equipment.shoulders = None
    elif slotname == 'torso':
        if equipment.torso == itemid:
            equipment.torso = None
    elif slotname == 'hands':
        if equipment.hands == itemid:
            equipment.hands = None
    elif slotname == 'legs':
        if equipment.legs == itemid:
            equipment.legs = None
    elif slotname == 'feet':
        if equipment.feet == itemid:
            equipment.feet = None
    elif slotname == 'holster':
        if equipment.holster == itemid:
            equipment.holster = None
    elif slotname == 'righthand':
        if equipment.righthand == itemid:
            if equipment.righthand ==  equipment.lefthand:
                # If the weapon equipped takes both hands
                equipment.righthand = None
                equipment.lefthand  = None
            else:
                equipment.righthand = None
    elif slotname == 'lefthand':
        if equipment.lefthand == itemid:
            if equipment.righthand ==  equipment.lefthand:
                # If the weapon equipped takes both hands
                equipment.righthand = None
                equipment.lefthand  = None
            else:
                equipment.lefthand = None

    equipment.date = datetime.now()

    try:
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Unequip failed (pcid:{},itemid:{})'.format(pcid,itemid),
                None)
    else:
        equipment = session.query(CreatureSlots)\
                           .filter(CreatureSlots.id == pc.id)\
                           .one_or_none()

        # We need to convert datetime to str before dumping it as a dict
        equipment.date = equipment.date.strftime('%Y-%m-%d %H:%M:%S')

        # We put the info in queue for ws
        qciphered = False
        qpayload  = dataclasses.asdict(equipment)
        qscope    = {"id": None, "scope": 'broadcast'}
        qmsg = {"ciphered": qciphered,
                "payload": qpayload,
                "route": "mypc/{id1}/inventory/item/{id2}/unequip/{id3}/{id4}",
                "scope": qscope}
        yqueue_put('broadcast', qmsg)

        return (200,
                True,
                'Unequipped successful (pcid:{},itemid:{})'.format(pcid,itemid),
                {"red": get_pa(pcid)[3]['red'],
                 "blue": get_pa(pcid)[3]['blue'],
                 "equipment": equipment})
    finally:
        session.close()

# API: /mypc/<int:pcid>/inventory/item/<int:itemid>/offset/<int:offsetx>/<int:offsety>
def mypc_inventory_item_offset(username,pcid,itemid,offsetx,offsety):
    pc          = fn_creature_get(None,pcid)[3]
    user        = fn_user_get(username)
    session     = Session()

    if pc and pc.account == user.id:
        item  = session.query(Item).filter(Item.id == itemid, Item.bearer == pc.id).one_or_none()
        if item is None:
            return (200,
                    False,
                    'Item not found (pcid:{},itemid:{})'.format(pc.id,itemid),
                    None)

        item.offsetx = offsetx
        item.offsety = offsety
        item.date    = datetime.now() # We update the date in DB

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Item update failed (pcid:{},itemid:{})'.format(pc.id,item.id),
                    None)
        else:
            weapon   = session.query(Item).\
                               filter(Item.bearer == pc.id).filter(Item.metatype == 'weapon').all()
            armor    = session.query(Item).\
                               filter(Item.bearer == pc.id).filter(Item.metatype == 'armor').all()
            equipment = session.query(CreatureSlots).filter(CreatureSlots.id == pc.id).all()
            return (200,
                    True,
                    'Item update successed (itemid:{})'.format(item.id),
                    {"weapon": weapon, "armor": armor, "equipment": equipment})
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)
