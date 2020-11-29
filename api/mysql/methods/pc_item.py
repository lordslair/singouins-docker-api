# -*- coding: utf8 -*-

from ..session          import Session
from ..models           import *
from ..utils.redis      import *

from .fn_creature       import fn_creature_get
from .fn_user           import fn_user_get
from .fn_global         import clog

#
# Queries /pc/{pcid}/item/{itemid}/*
#

def pc_items_get(username,pcid):
    (code, success, msg, pc) = fn_creature_get(None,pcid)
    user                     = fn_user_get(username)
    session                  = Session()

    if pc.account is None: return (200, False, 'NPCs do not have items (pcid:{})'.format(pc.id), None)

    try:
        equipment = session.query(CreatureSlots).filter(CreatureSlots.id == pc.id).all()

        feet      = session.query(Item).filter(Item.id == equipment[0].feet).one_or_none()
        hands     = session.query(Item).filter(Item.id == equipment[0].hands).one_or_none()
        head      = session.query(Item).filter(Item.id == equipment[0].head).one_or_none()
        holster   = session.query(Item).filter(Item.id == equipment[0].holster).one_or_none()
        lefthand  = session.query(Item).filter(Item.id == equipment[0].lefthand).one_or_none()
        righthand = session.query(Item).filter(Item.id == equipment[0].righthand).one_or_none()
        shoulders = session.query(Item).filter(Item.id == equipment[0].shoulders).one_or_none()
        torso     = session.query(Item).filter(Item.id == equipment[0].torso).one_or_none()
        legs      = session.query(Item).filter(Item.id == equipment[0].legs).one_or_none()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                '[SQL] Equipment query failed (pcid:{})'.format(pc.id),
                None)
    else:
        feetmetaid      = feet.metaid      if feet      is not None else None
        handsmetaid     = hands.metaid     if hands     is not None else None
        headmetaid      = head.metaid      if head      is not None else None
        holstermetaid   = holster.metaid   if holster   is not None else None
        shouldersmetaid = shoulders.metaid if shoulders is not None else None
        torsometaid     = torso.metaid     if torso     is not None else None
        legsmetaid      = legs.metaid      if legs      is not None else None

        if righthand is not None and lefthand is not None:
            if righthand.id == lefthand.id:
                # PC has ONE two-handed weapon equipped. I send only meta inside RH
                righthandmetaid = righthand.metaid if righthand is not None else None
                lefthandmetaid  = None
        else:
            # PC has TWO two-handed weapon equipped.
            righthandmetaid = righthand.metaid if righthand is not None else None
            lefthandmetaid  = lefthand.metaid  if lefthand  is not None else None

        feetmetatype      = feet.metatype      if feet      is not None else None
        handsmetatype     = hands.metatype     if hands     is not None else None
        headmetatype      = head.metatype      if head      is not None else None
        holstermetatype   = holster.metatype   if holster   is not None else None
        lefthandmetatype  = lefthand.metatype  if lefthand  is not None else None
        righthandmetatype = righthand.metatype if righthand is not None else None
        shouldersmetatype = shoulders.metatype if shoulders is not None else None
        torsometatype     = torso.metatype     if torso     is not None else None
        legsmetatype      = legs.metatype      if legs      is not None else None

        metas = {"feet": {"metaid": feetmetaid,"metatype": feetmetatype},
                "hands": {"metaid": handsmetaid,"metatype": handsmetatype},
                "head": {"metaid": headmetaid,"metatype": headmetatype},
                "holster": {"metaid": holstermetaid,"metatype": holstermetatype},
                "lefthand": {"metaid": lefthandmetaid,"metatype": lefthandmetatype},
                "righthand": {"metaid": righthandmetaid,"metatype": righthandmetatype},
                "shoulders": {"metaid": shouldersmetaid,"metatype": shouldersmetatype},
                "torso": {"metaid": torsometaid,"metatype": torsometatype},
                "legs": {"metaid": legsmetaid,"metatype": legsmetatype}}
        return (200,
                True,
                'Equipment query successed (pcid:{})'.format(pc.id),
                {"equipment": metas})
    finally:
        session.close()
