# -*- coding: utf8 -*-

from datetime       import datetime
from random         import randint

import textwrap

from ..session          import Session
from ..models           import *
from ..utils.loot       import *
from ..utils.redis      import *

from .fn_creature       import *
from .fn_globals        import clog

#
# Queries: /auth
#

def get_username_exists(username):
    session = Session()

    try:
        result = session.query(User)\
                        .filter(User.name == username)\
                        .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return True
    finally:
        session.close()

def get_usermail_exists(usermail):
    session = Session()

    try:
       result = session.query(User)\
                       .filter(User.mail == usermail)\
                       .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return True
    finally:
        session.close()

def get_user(username):
    session = Session()

    try:
       result = session.query(User)\
                       .filter(User.name == username)\
                       .one_or_none()
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return result
    finally:
        session.close()

def add_user(username,password,usermail):
    session = Session()

    if get_username_exists(username) or get_usermail_exists(usermail):
        return (409)
    else:
        from flask_bcrypt import generate_password_hash

        user = User(name      = username,
                    mail      = usermail,
                    hash      = generate_password_hash(password, rounds = 10),
                    d_name    = '',
                    d_monkeys = '', # Todo later
                    d_ack     = False,
                    created   = datetime.now(),
                    active    = True)

        session.add(user)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (422)
        else:
            return (201)
        finally:
            session.close()

def set_user_confirmed(usermail):
    session = Session()

    try:
        user = session.query(User)\
                      .filter(User.mail == usermail)\
                      .one_or_none()
        user.active = True
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (422)
    else:
        return (201)
    finally:
        session.close()

def del_user(username):
    session = Session()

    if not get_username_exists(username):
        return (404)
    else:
        try:
            user = session.query(User)\
                          .filter(User.name == username)\
                          .one_or_none()
            session.delete(user)
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (422)
        else:
            return (200)
        finally:
            session.close()

#
# Queries: /pc
#
from variables      import PCS_URL

def get_pc_exists(pcname,pcid):
    session = Session()

    try:
        if not pcname and not pcid:
            return False
        elif pcname and pcid:
            result = session.query(PJ).filter(PJ.name == pcname, PJ.id == pcid).one_or_none()
        elif pcname and not pcid:
            result = session.query(PJ).filter(PJ.name == pcname).one_or_none()
        elif not pcname and pcid:
            result = session.query(PJ).filter(PJ.id == pcid).one_or_none()
        else:
            return False
    except Exception as e:
        # Something went wrong during query
        return False
    else:
        if result: return True
    finally:
        session.close()

def add_pc(username,pcname,pcrace):
    session = Session()

    if get_pc_exists(pcname,None):
        return (409,
                False,
                'PC already exists (username:{},pcname:{})'.format(username,pcname),
                None)
    else:
        pc = PJ(name    = pcname,
                race    = pcrace,
                account = get_user(username).id,
                rarity  = 'Normal',
                level   = 1,
                x       = 0,
                y       = 0,
                xp      = 0,
                hp      = 80,
                hp_max  = 80,
                arm_p   = 50,
                arm_b   = 25,
                m       = 100,
                r       = 100,
                g       = 100,
                v       = 100,
                p       = 100,
                b       = 100,
                sprite  = PCS_URL + '/resources/sprites/creatures/' + pcrace + '.png')

        session.add(pc)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC creation failed (username:{},pcname:{})'.format(username,pcname),
                    None)
        else:
                (code, success, msg, pc) = get_pc(pcname,None)
                equipment = CreaturesSlots(id     = pc.id)
                session.add(equipment)

                try:
                    session.commit()
                except Exception as e:
                    # Something went wrong during commit
                    return (200, False, '[SQL] PC Slots creation failed', None)
                else:
                    return (201, True, 'PC successfully created', pc)
        finally:
            session.close()

def get_pc(pcname,pcid):
    session = Session()

    try:
        if pcid:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
        elif pcname:
            pc = session.query(PJ).filter(PJ.name == pcname).one_or_none()
        else:
            return (200,
                    False,
                    'Wrong pcid/pcname (pcid:{},pcname:{})'.format(pcid,pcname),
                    None)
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                '[SQL] PC query failed (pcid:{},pcname:{})'.format(pcid,pcname),
                None)
    else:
        if pc:
            return (200,
                    True,
                    'PC successfully found (pcid:{},pcname:{})'.format(pcid,pcname),
                    pc)
        else:
            return (200,
                    False,
                    'PC does not exist (pcid:{},pcname:{})'.format(pcid,pcname),
                    None)
    finally:
        session.close()

def get_pcs(username):
    session = Session()

    try:
        userid = get_user(username).id
        pcs    = session.query(PJ).filter(PJ.account == userid).all()
    except Exception as e:
        # Something went wrong during query
        return (200,
                False,
                '[SQL] PCs query failed (username:{})'.format(username),
                None)
    else:
        if pcs:
            return (200,
                    True,
                    'PCs successfully found (username:{})'.format(username),
                    pcs)
        else:
            return (200,
                    False,
                    'No PC found for this user (username:{})'.format(username),
                    None)
    finally:
        session.close()

def del_pc(username,pcid):
    session = Session()

    if not get_pc_exists(None,pcid):
        return (200, False, 'PC does not exist (pcid:{})'.format(pcid), None)

    try:
        userid  = get_user(username).id
        pc = session.query(PJ).filter(PJ.account == userid, PJ.id == pcid).one_or_none()
        session.delete(pc)
        equipment = session.query(CreaturesSlots).filter(CreaturesSlots.id == pc.id).one_or_none()
        session.delete(equipment)
        session.commit()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] PC deletion failed (username:{},pcid:{})'.format(username,pcid),
                None)
    else:
        return (200,
                True,
                'PC successfully deleted (username:{},pcid:{})'.format(username,pcid),
                None)
    finally:
        session.close()

#
# Queries: /mp
#

def add_mp(username,src,dsts,subject,body):
    (code, success, msg, pcsrc) = get_pc(None,src)
    user                        = get_user(username)
    session                     = Session()

    if pcsrc:
        for dst in dsts:
            (code, success, msg, pcdst) = get_pc(None,dst)
            if pcdst:
                mp = MP(src_id  = pcsrc.id,
                        src     = pcsrc.name,
                        dst_id  = pcdst.id,
                        dst     = pcdst.name,
                        subject = subject,
                        body    = body)
                session.add(mp)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            session.rollback()
            return (200,
                    False,
                    '[SQL] MP creation failed (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                    None)
        else:
            return (201,
                    True,
                    'MP successfully created (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                    None)
        finally:
            session.close()

    elif user.id != pcsrc.account:
        return (409, False, 'Token/username mismatch', None)
    else:
        return (200,
                False,
                'PC does not exist (srcid:{},dstid:{})'.format(pcsrc.id,pcdst.id),
                None)

def get_mp(username,pcid,mpid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
        except Exception as e:
            # Something went wrong during query
            return (200,
                    False,
                    '[SQL] MP query failed (pcid:{},mpid:{})'.format(pc.id,mpid),
                    None)
        else:
            if mp:
                return (200,
                        True,
                        'MP successfully found (pcid:{},mpid:{})'.format(pc.id,mpid),
                        mp)
            else:
                return (200, True, 'MP not found (pcid:{},mpid:{})'.format(pc.id,mpid), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def del_mp(username,pcid,mpid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mp = session.query(MP).filter(MP.dst_id == pc.id, MP.id == mpid).one_or_none()
            if not mp: return (200, True, 'No MP found for this PC', None)
            session.delete(mp)
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] MP deletion failed', None)
        else:
            return (200, True, 'MP successfully deleted', None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def get_mps(username,pcid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            mps = session.query(MP).filter(MP.dst_id == pc.id).all()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] MPs query failed (pcid:{})'.format(pc.id), None)
        else:
            if mps:
                for mp in mps: mp.body = textwrap.shorten(mp.body, width=50, placeholder="...")
                return (200, True, 'MPs successfully found (pcid:{})'.format(pc.id), mps)
            else:
                return (200, True, 'No MP found (pcid:{})'.format(pc.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def get_mp_addressbook(username,pcid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            addressbook = session.query(PJ).with_entities(PJ.id,PJ.name).all()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Addressbook query failed (pcid:{})'.format(pc.id), None)
        else:
            if addressbook:
                return (200, True, 'Addressbook successfully found (pcid:{})'.format(pc.id), addressbook)
            else:
                return (200, True, 'No Addressbook found (pcid:{})'.format(pc.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /item
#

def get_items(username,pcid,public):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc.account is None: return (200, False, 'NPCs do not have items (pcid:{})'.format(pc.id), None)

    if public is True:
        # Here it's for a public /pc call
        try:
            equipment = session.query(CreaturesSlots).filter(CreaturesSlots.id == pc.id).all()

            feet      = session.query(Items).filter(Items.id == equipment[0].feet).one_or_none()
            hands     = session.query(Items).filter(Items.id == equipment[0].hands).one_or_none()
            head      = session.query(Items).filter(Items.id == equipment[0].head).one_or_none()
            holster   = session.query(Items).filter(Items.id == equipment[0].holster).one_or_none()
            lefthand  = session.query(Items).filter(Items.id == equipment[0].lefthand).one_or_none()
            righthand = session.query(Items).filter(Items.id == equipment[0].righthand).one_or_none()
            shoulders = session.query(Items).filter(Items.id == equipment[0].shoulders).one_or_none()
            torso     = session.query(Items).filter(Items.id == equipment[0].torso).one_or_none()
            legs      = session.query(Items).filter(Items.id == equipment[0].legs).one_or_none()
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
    else:
        # Here it's for a private /mypc call
        if pc and pc.account == user.id:
            try:
                weapon    = session.query(Items)\
                                   .filter(Items.bearer == pc.id)\
                                   .filter(Items.metatype == 'weapon')\
                                   .all()
                armor     = session.query(Items)\
                                   .filter(Items.bearer == pc.id)\
                                   .filter(Items.metatype == 'armor')\
                                   .all()
                equipment = session.query(CreaturesSlots)\
                                   .filter(CreaturesSlots.id == pc.id)\
                                   .all()
                cosmetic  = session.query(Cosmetics)\
                                   .filter(Cosmetics.bearer == pc.id)\
                                   .all()
            except Exception as e:
                # Something went wrong during query
                return (200,
                        False,
                        '[SQL] Equipment query failed (pcid:{})'.format(pc.id),
                        None)
            else:
                return (200,
                        True,
                        'Equipment query successed (pcid:{})'.format(pc.id),
                        {"weapon": weapon,
                         "armor": armor,
                         "equipment": equipment,
                         "cosmetic": cosmetic})
            finally:
                session.close()
        else: return (409, False, 'Token/username mismatch', None)

def set_item_offset(username,pcid,itemid,offsetx,offsety):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        item  = session.query(Items).filter(Items.id == itemid, Items.bearer == pc.id).one_or_none()
        if item is None:
            return (200,
                    False,
                    'Item not found (pcid:{},itemid:{})'.format(pc.id,itemid),
                    None)

        item.offsetx = offsetx
        item.offsety = offsety

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Item update failed (pcid:{},itemid:{})'.format(pc.id,item.id),
                    None)
        else:
            weapon   = session.query(Items).\
                               filter(Items.bearer == pc.id).filter(Items.metatype == 'weapon').all()
            armor    = session.query(Items).\
                               filter(Items.bearer == pc.id).filter(Items.metatype == 'armor').all()
            equipment = session.query(CreaturesSlots).filter(CreaturesSlots.id == pc.id).all()
            return (200,
                    True,
                    'Item update successed (itemid:{})'.format(item.id),
                    {"weapon": weapon, "armor": armor, "equipment": equipment})
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /meta
#

def get_meta_item(metatype):
    session = Session()

    try:
        if    metatype == 'weapon': meta = session.query(MetaWeapons).all()
        elif  metatype == 'armor':  meta = session.query(MetaArmors).all()
        else:  meta = None
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Meta query failed (metatype:{})'.format(metatype),
                None)
    else:
        if meta:
            return (200, True, 'OK', meta)
        else:
            return (200, False, 'Meta does not exist (metatype:{})'.format(metatype), None)
    finally:
        session.close()

#
# Queries /squad
#

def get_squad(username,pcid,squadid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        try:
            squad = session.query(Squad).\
                            filter(Squad.id == pc.squad).\
                            filter(PJ.id == pc.id)

            pc_is_member  = squad.filter(PJ.squad_rank != 'Pending').one_or_none()
            pc_is_pending = squad.filter(PJ.squad_rank == 'Pending').one_or_none()

            if pc_is_member:
                squad   = squad.session.query(Squad).filter(Squad.id == pc.squad).one_or_none()
                members = session.query(PJ).filter(PJ.squad == squad.id).filter(PJ.squad_rank != 'Pending').all()
                pending = session.query(PJ).filter(PJ.squad == squad.id).filter(PJ.squad_rank == 'Pending').all()
            elif pc_is_pending:
                squad   = squad.session.query(Squad).filter(Squad.id == pc.squad).one_or_none()

        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Squad query failed (pcid:{},squadid:{})'.format(pcid,squadid),
                    None)
        else:
            if pc_is_member:
                if squad:
                    if isinstance(members, list):
                        if isinstance(pending, list):
                            return (200,
                                    True,
                                    'Squad query successed (pcid:{},squadid:{})'.format(pcid,squadid),
                                    {"squad": squad, "members": members, "pending": pending})
            elif pc_is_pending:
                return (200,
                        True,
                        'PC is pending in a squad (pcid:{},squadid:{})'.format(pcid,squadid),
                        {"squad": squad})
            else: return (200,
                          False,
                          'PC is not in a squad (pcid:{},squadid:{})'.format(pcid,squadid),
                          None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def add_squad(username,pcid,squadname):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        if session.query(Squad).filter(Squad.name == squadname).one_or_none():
            return (409, False, 'Squad already exists', None)
        if pc.squad is not None:
            return (200,
                    False,
                    'Squad leader already in a squad (pcid:{},squadid:{})'.format(pc.id,squad.id),
                    None)

        squad = Squad(name    = squadname,
                      leader  = pc.id,
                      created = datetime.now())
        session.add(squad)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Squad creation failed (pcid:{})'.format(pcid), None)

        # Squad created, let's assign the team creator in the squad
        pc            = session.query(PJ).filter(PJ.id == pcid).one_or_none()
        squad         = session.query(Squad).filter(Squad.leader == pc.id).one_or_none()
        pc.squad      = squad.id
        pc.squad_rank = 'Leader'

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Squad leader assignation failed (pcid:{},squadid:{})'.format(pc.id,squad.id),
                    None)
        else:
            return (201,
                    True,
                    'Squad successfully created (pcid:{},squadid:{})'.format(pc.id,squad.id),
                    squad)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def del_squad(username,leaderid,squadid):
    (code, success, msg, leader) = get_pc(None,leaderid)
    user                         = get_user(username)
    session                      = Session()

    if leader:
        if leader.squad != squadid:
            return (200, False, 'Squad request outside of your scope ({} =/= {})'.format(leader.squad,squadid), None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(leaderid), None)

    if leader and leader.account == user.id:
        try:
            squad = session.query(Squad).filter(Squad.leader == leader.id).one_or_none()
            if not squad: return (200, True, 'No Squad found for this PC (pcid:{})'.format(leader.id), None)

            count = session.query(PJ).filter(PJ.squad == squad.id).count()
            if count > 1: return (200, False, 'Squad not empty (squadid:{})'.format(squad.id), None)

            session.delete(squad)
            pc = session.query(PJ).filter(PJ.id == leader.id).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Squad deletion failed (squadid:{})'.format(squad.id), None)
        else:
            return (200, True, 'Squad successfully deleted (squadid:{})'.format(squad.id), None)
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def invite_squad_member(username,leaderid,squadid,targetid):
    (code, success, msg, target) = get_pc(None,targetid)
    (code, success, msg, leader) = get_pc(None,leaderid)
    user                         = get_user(username)
    session                      = Session()

    if leader:
        if leader.squad is None:
            return (200, False, 'PC is not in a squad', None)
        if leader.squad != squadid:
            return (200, False, 'Squad request outside of your scope ({} =/= {})'.format(leader.squad,squadid), None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)

        members    = session.query(PJ).filter(PJ.squad == leader.squad).all()
        maxmembers = 10
        if len(members) == maxmembers:
            return (200,
                    False,
                    'Squad is already full (slots:{}/{})'.format(len(members),maxmembers),
                    None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(leaderid), None)

    if target:
        if target.squad is not None:
            return (200,
                    False,
                    'PC invited is already in a squad (pcid:{},squadid:{})'.format(target.id,target.squad),
                    None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(targetid), None)

    if target and leader:
        try:
            pc = session.query(PJ).filter(PJ.id == target.id).one_or_none()
            pc.squad      = leader.squad
            pc.squad_rank = 'Pending'
            session.commit()
            members    = session.query(PJ).filter(PJ.squad == leader.squad).all()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC Invite failed (slots:{}/{})'.format(len(members),maxmembers),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully invited (slots:{}/{})'.format(len(members),maxmembers),
                    pc)
        finally:
            session.close()
    else:
        return (200,
                False,
                'PC/Leader unknown in DB (leaderid:{},targetid:{})'.format(leaderid,targetid),
                None)

def kick_squad_member(username,leaderid,squadid,targetid):
    (code, success, msg, target) = get_pc(None,targetid)
    (code, success, msg, leader) = get_pc(None,leaderid)
    user                         = get_user(username)
    maxmembers                   = 10
    session                      = Session()

    if leader:
        if leader.squad is None:
            return (200, False, 'PC is not in a squad', None)
        if leader.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope ({} =/= {})'.format(leader.squad,squadid),
                    None)
        if leader.squad_rank != 'Leader':
            return (200, False, 'PC is not the squad Leader', None)
        if leader.id == targetid:
            return (200, False, 'PC target cannot be the squad Leader', None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(leaderid), None)

    if target:
        if target.squad is None:
            return (200,
                    False,
                    'PC have to be in a squad (pcid:{},squadid:{})'.format(target.id,target.squad),
                    None)
    else:
        return (200, False, 'PC unknown in DB (pcid:{})'.format(targetid), None)

    if target and leader:
        try:
            pc = session.query(PJ).filter(PJ.id == target.id).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
            members    = session.query(PJ).filter(PJ.squad == leader.squad).all()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC Kick failed (pcid:{},squadid:{})'.format(target.id,target.squad),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully kicked (slots:{}/{})'.format(len(members),maxmembers),
                    None)
        finally:
            session.close()
    else:
        return (200,
                False,
                'PC/Leader unknown in DB (leaderid:{},targetid:{})'.format(leaderid,targetid),
                None)

def accept_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = get_pc(None,pcid)
    user                         = get_user(username)
    session                      = Session()

    if pc:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        if pc.squad_rank != 'Pending':
            return (200, False, 'PC is not pending in a squad', None)

        try:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
            pc.squad_rank = 'Member'
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC squad invite accept failed (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully accepted squad invite (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        finally:
            session.close()
    else: return (200, False, 'PC unknown in DB (pcid:{})'.format(pcid), None)

def decline_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = get_pc(None,pcid)
    user                         = get_user(username)
    session                      = Session()

    if pc:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        if pc.squad_rank != 'Pending':
            return (200, False, 'PC is not pending in a squad', None)

        try:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC squad invite decline failed (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        else:
            return (201, True, 'PC successfully declined squad invite (pcid:{},squadid:{})'.format(pc.id,squadid), None)
        finally:
            session.close()
    else: return (200, False, 'PC unknown in DB (pcid:{})'.format(pcid), None)

def leave_squad_member(username,pcid,squadid):
    (code, success, msg, pc)     = get_pc(None,pcid)
    user                         = get_user(username)
    session                      = Session()

    if pc:
        # PC is not the Squad member
        if pc.squad != squadid:
            return (200,
                    False,
                    'Squad request outside of your scope (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        if pc.squad_rank == 'Leader':
            return (200,
                    False,
                    'PC cannot be the squad Leader (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)

        try:
            pc = session.query(PJ).filter(PJ.id == pcid).one_or_none()
            pc.squad      = None
            pc.squad_rank = None
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] PC squad leave failed (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        else:
            return (201,
                    True,
                    'PC successfully left (pcid:{},squadid:{})'.format(pc.id,squadid),
                    None)
        finally:
            session.close()
    else: return (200, False, 'PC unknown in DB (pcid:{})'.format(pcid), None)

#
# Queries /map
#

def get_map(mapid):
    session = Session()

    if mapid:
        try:
            map = session.query(Map).filter(Map.id == mapid).one_or_none()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Map query failed (mapid:{})'.format(mapid), None)
        else:
            if map:
                return (200, True, 'Map query successed (mapid:{})'.format(mapid), map)
            else:
                return (200, False, 'Map does not exist (mapid:{})'.format(mapid), None)
        finally:
            session.close()
    else: return (200, False, 'Incorrect mapid (mapid:{})'.format(mapid), None)

#
# Queries /events
#

def get_mypc_event(username,pcid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            log   = session.query(Log)\
                           .filter((Log.src == pc.id) | (Log.dst == pc.id))\
                           .order_by(Log.date.desc())\
                           .limit(50)\
                           .all()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Event query failed (username:{},pcid:{})'.format(username,pcid),
                    None)
        else:
            return (200, True, 'Events successfully retrieved (pcid:{})'.format(pc.id), log)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)

def get_pc_event(creatureid):
    (code, success, msg, creature) = get_pc(None,creatureid)
    session                        = Session()

    if creature is None: return (200, True, 'Creature does not exist (creatureid:{})'.format(creatureid), None)

    try:
        log   = session.query(Log)\
                       .filter(Log.src == creature.id)\
                       .order_by(Log.date.desc())\
                       .limit(50)\
                       .all()
    except Exception as e:
        # Something went wrong during commit
        return (200,
                False,
                '[SQL] Event query failed (creatureid:{})'.format(creature.id),
                None)
    else:
        return (200, True, 'Events successfully retrieved (creatureid:{})'.format(creature.id), log)
    finally:
        session.close()

#
# Queries /action
#

def action_move(username,pcid,path):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    (oldx,oldy)              = pc.x,pc.y
    session                  = Session()

    if pc and pc.account == user.id:

        for coords in path:
            bluepa                   = get_pa(pcid)[3]['blue']['pa']
            x,y                      = map(int, coords.strip('()').split(','))

            if abs(pc.x - x) <= 1 and abs(pc.y - y) <= 1:
                if bluepa > 1:
                    # Enough PA to move
                    set_pa(pcid,0,1) # We consume the blue PA (1) right now
                    pc   = session.query(PJ).filter(PJ.id == pcid).one_or_none()
                    pc.x = x
                    pc.y = y

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200,
                    False,
                    '[SQL] Coords update failed (pcid:{},path:{})'.format(pcid,path),
                    None)
        else:
            clog(pc.id,None,'Moved from ({},{}) to ({},{})'.format(oldx,oldy,x,y))
            return (200, True, 'PC successfully moved', get_pa(pcid)[3])
        finally:
            session.close()
    else: return (409, False, 'Token/username mismatch', None)

def action_attack(username,pcid,weaponid,targetid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    (code, success, msg, tg) = get_pc(None,targetid)

    if tg.targeted_by is not None:
        # Target already taggued by a pc
        (code, success, msg, tag) = get_pc(None,tg.targeted_by)
        if tag.id != pc.id and tag.squad != pc.squad:
            # Target not taggued by the pc itself
            # Target not taggued by a pc squad member
            return (200, False, 'Target does not belong to the PC/Squad', None)

    if pc and pc.account == user.id:
        if weaponid == 0:
            (code, success, msg, tg) = get_pc(None,targetid)
            redpa                    = get_pa(pcid)[3]['red']['pa']
            dmg_wp                   = 20
            action                   = {"failed": True, "hit": False, "critical": False, "damages": None, "killed": False}

            if abs(pc.x - tg.x) <= 1 and abs(pc.y - tg.y) <= 1:
                # Target is on a adjacent tile
                if redpa > 1:
                    # Enough PA to attack
                    set_pa(pcid,4,0) # We consume the red PA (4) right now
                    pc.comcap  = (pc.g + (pc.m + pc.r)/2 )/2

                    if randint(1, 100) <= 97:
                        # Successfull action
                        action['failed'] = False
                        if pc.comcap > tg.r:
                            # The attack successed
                            action['hit'] = True

                            # The target is now acquired to the attacker
                            fn_creature_tag(pc,tg)

                            if randint(1, 100) <= 5:
                                # The attack is a critical Hit
                                dmg_crit = round(150 + pc.r / 10)
                                clog(pc.id,tg.id,'Critically Attacked {}'.format(tg.name))
                                clog(tg.id,None,'Critically Hit by {}'.format(pc.name))
                            else:
                                # The attack is a normal Hit
                                dmg_crit = 100
                                clog(pc.id,tg.id,'Attacked {}'.format(tg.name))
                                clog(tg.id,None,'Hit by {}'.format(pc.name))

                            dmg = round(dmg_wp * dmg_crit / 100) - tg.arm_p
                            if dmg > 0:
                                # The attack deals damage
                                action['damages'] = dmg

                                if tg.hp - dmg >= 0:
                                    # The attack wounds
                                    fn_creature_wound(pc,tg,dmg)
                                else:
                                    # The attack kills
                                    action['killed'] = True
                                    fn_creature_kill(pc,tg)

                                    # Experience points are generated
                                    (ret,msg) = fn_creature_gain_xp(pc,tg)
                                    if ret is not True:
                                        return (200, False, msg, None)

                                    # Loots are given to PCs
                                    (ret,msg) = fn_creature_gain_loot(pc,tg)
                                    if ret is not True:
                                        return (200, False, msg, None)
                            else:
                                clog(tg.id,None,'Suffered no injuries')
                                # The attack does not deal damage
                        else:
                            # The attack missed
                            clog(pc.id,tg.id,'Missed {}'.format(tg.name))
                            clog(tg.id,None,'Avoided {}'.format(pc.name))
                    else:
                        # Failed action
                        clog(pc.id,None,'Failed an attack')
                else:
                    # Not enough PA to attack
                    return (200,
                            False,
                            'Not enough PA to attack',
                            {"red": get_pa(pcid)[3]['red'],
                             "blue": get_pa(pcid)[3]['blue'],
                             "action": None})
            else:
                # Target is too far
                return (200, False, 'Coords incorrect', None)
        return (200,
                True,
                'Target successfully attacked',
                {"red": get_pa(pcid)[3]['red'],
                 "blue": get_pa(pcid)[3]['blue'],
                 "action": action})
    else: return (409, False, 'Token/username mismatch', None)

def action_equip(username,pcid,type,slotname,itemid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        if pc.instance > 0:
            # Meaning we are in a combat zone
            if get_pa(pc.id)[3]['red']['pa'] > 2:
                # Enough PA to equip
                set_pa(pc.id,2,0) # We consume the red PA (2) right now
            else:
                # Not enough PA to equip
                return (200, False, 'Not enough PA to equip', None)

        if itemid > 0:
            # EQUIP
            if   type == 'weapon':
                 item  = session.query(Items).filter(Items.id == itemid, Items.bearer == pc.id).one_or_none()
            elif type == 'armor':
                 item  = session.query(Items).filter(Items.id == itemid, Items.bearer == pc.id).one_or_none()

            equipment = session.query(CreaturesSlots).filter(CreaturesSlots.id == pc.id).one_or_none()

            if item      is None: return (200, False, 'Item not found (itemid:{})'.format(itemid), None)
            if equipment is None: return (200, False, 'Equipement not found (pcid:{})'.format(pc.id), None)

            # The item to equip exists, is owned by the PC, and we retrieved his equipment from DB
            if   slotname == 'head':      equipment.head      = item.id
            elif slotname == 'shoulders': equipment.shoulders = item.id
            elif slotname == 'torso':     equipment.torso     = item.id
            elif slotname == 'hands':     equipment.hands     = item.id
            elif slotname == 'legs':      equipment.legs      = item.id
            elif slotname == 'feet':      equipment.feet      = item.id
            elif slotname == 'ammo':      equipment.ammo      = item.id
            elif slotname == 'holster':
                itemmeta = session.query(MetaWeapons).filter(MetaWeapons.id == item.metaid).one_or_none()
                if itemmeta is None:
                    return (200,
                            False,
                            'ItemMeta not found (itemid:{},metaid:{})'.format(item.id,item.metaid),
                            None)

                sizex,sizey = itemmeta.size.split("x")
                if int(sizex) * int(sizey) <= 4:
                    # It fits inside the holster
                    equipment.holster  = item.id
                else:
                    return (200,
                            False,
                            'Item does not fit in holster (itemid:{},size:{})'.format(item.id,itemmeta.size),
                            None)
            elif slotname == 'righthand':
                itemmeta = session.query(MetaWeapons).filter(MetaWeapons.id == item.metaid).one_or_none()
                if itemmeta is None:
                    return (200,
                            False,
                            'ItemMeta not found (itemid:{},metaid:{})'.format(item.id,item.metaid),
                            None)

                sizex,sizey = itemmeta.size.split("x")
                if int(sizex) * int(sizey) <= 6:
                    # It fits inside the right hand
                    equipment.righthand  = item.id
                else:
                    # It fits inside the BOTH hand
                    equipment.righthand  = item.id
                    equipment.lefthand   = item.id
            elif slotname == 'lefthand':
                itemmeta = session.query(MetaWeapons).filter(MetaWeapons.id == item.metaid).one_or_none()
                if itemmeta is None:
                    return (200,
                            False,
                            'ItemMeta not found (itemid:{},metaid:{})'.format(item.id,item.metatymetaidpe),
                            None)

                sizex,sizey = itemmeta.size.split("x")
                if int(sizex) * int(sizey) <= 4:
                    # It fits inside the left hand
                    equipment.lefthand   = item.id
                else:
                    return (200,
                            False,
                            'Item does not fit in left hand (itemid:{},size:{})'.format(item.id,itemmeta.size),
                            None)

            equipment.date = datetime.now() # We update the date in DB
            item.bound     = True           # In case the item was not bound to PC. Now it is
            item.offsetx   = None           # Now the item is not in inventory anymore
            item.offsety   = None           # Now the item is not in inventory anymore
            item.date      = datetime.now() # We update the date in DB

        elif itemid == 0:
            # UNEQUIP
            equipment = session.query(CreaturesSlots).filter(CreaturesSlots.id == pc.id).one_or_none()
            if equipment is None: return (200, False, 'Equipement not found (pcid:{})'.format(pc.id), None)

            # We retrieved his equipment from DB
            if   slotname == 'head':      equipment.head      = None
            elif slotname == 'shoulders': equipment.shoulders = None
            elif slotname == 'torso':     equipment.torso     = None
            elif slotname == 'hands':     equipment.hands     = None
            elif slotname == 'legs':      equipment.legs      = None
            elif slotname == 'feet':      equipment.feet      = None
            elif slotname == 'ammo':      equipment.ammo      = None
            elif slotname == 'holster':   equipment.holster   = None
            elif slotname == 'righthand':
                if equipment.righthand ==  equipment.lefthand:
                    # If the weapon equipped takes both hands
                    equipment.righthand = None
                    equipment.lefthand  = None
                else:
                    equipment.righthand = None
            elif slotname == 'lefthand':
                if equipment.lefthand ==  equipment.righthand:
                    # If the weapon equipped takes both hands
                    equipment.righthand = None
                    equipment.lefthand  = None
                else:
                    equipment.lefthand = None

            equipment.date = datetime.now()
        else:
            # Weird weaponid
            return (200, False, 'Itemid incorrect (itemid:{})'.format(itemid), None)

        try:
            session.commit()
        except Exception as e:
            # Something went wrong during commit
            return (200, False, '[SQL] Equipment update failed (itemid:{})'.format(itemid), None)
        else:
            equipment = session.query(CreaturesSlots).filter(CreaturesSlots.id == pc.id).one_or_none()
            clog(pc.id,None,'Equipment changed')
            return (200,
                    True,
                    'Equipment successfully updated (itemid:{})'.format(itemid),
                    {"red": get_pa(pcid)[3]['red'], "blue": get_pa(pcid)[3]['blue'], "equipment": equipment})
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)

#
# Queries /view
#
def get_view(username,pcid):
    (code, success, msg, pc) = get_pc(None,pcid)
    user                     = get_user(username)
    session                  = Session()

    if pc and pc.account == user.id:
        try:
            range = 4 + round(pc.p / 50)
            maxx  = pc.x + range
            minx  = pc.x - range
            maxy  = pc.y + range
            miny  = pc.y - range
            view  = session.query(PJ).filter(PJ.instance == pc.instance)\
                                            .filter(PJ.x.between(minx,maxx))\
                                            .filter(PJ.y.between(miny,maxy))\
                                            .all()
        except Exception as e:
            # Something went wrong during query
            return (200,
                    False,
                    '[SQL] View query failed (username:{},pcid:{}) [{}]'.format(username,pcid,e),
                    None)
        else:
            return (200,
                    True,
                    'View successfully retrieved (range:{},x:{},y:{})'.format(range,pc.x,pc.y),
                    view)
        finally:
            session.close()

    else: return (409, False, 'Token/username mismatch', None)
