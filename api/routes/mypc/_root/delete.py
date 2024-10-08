# -*- coding: utf8 -*-

from flask import g, jsonify
from flask_jwt_extended import jwt_required
from loguru import logger

from mongo.models.Cosmetic import CosmeticDocument
from mongo.models.Creature import CreatureDocument
from mongo.models.Highscore import HighscoreDocument
from mongo.models.Item import ItemDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Satchel import SatchelDocument

from utils.decorators import check_creature_exists
from utils.redis import r
from variables import API_ENV


# API: DELETE /mypc/<uuid:creatureuuid>
@jwt_required()
# Custom decorators
@check_creature_exists
def mypc_del(creatureuuid):
    if g.Creature.instance:
        msg = f'{g.h} Cannot be in an Instance({g.Creature.instance})'
        logger.debug(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        # We start do delete PC elements
        # Redis PA
        for color in ['blue', 'red']:
            r.delete(f"{API_ENV}:pas:{creatureuuid}:{color}")
        # SatchelDocument
        if SatchelDocument.objects(_id=g.Creature.id):
            logger.debug(f'{g.h} SatchelDocument deletion >>')
            SatchelDocument.objects(_id=g.Creature.id).get().delete()
            logger.debug(f'{g.h} SatchelDocument deletion OK')
        # HighscoreDocument
        if HighscoreDocument.objects(_id=g.Creature.id):
            logger.debug(f'{g.h} HighscoreDocument deletion >>')
            HighscoreDocument.objects(_id=g.Creature.id).get().delete()
            logger.debug(f'{g.h} HighscoreDocument deletion OK')
        # ProfessionDocument
        if ProfessionDocument.objects(_id=g.Creature.id):
            logger.debug(f'{g.h} ProfessionDocument deletion >>')
            ProfessionDocument.objects(_id=g.Creature.id).get().delete()
            logger.debug(f'{g.h} ProfessionDocument deletion OK')
        # CosmeticDocument
        if CosmeticDocument.objects(bearer=g.Creature.id):
            try:
                logger.debug(f'{g.h} CosmeticDocument(s) deletion >>')
                CosmeticDocument.objects(bearer=g.Creature.id).delete()
            except Exception as e:
                logger.error(f'{g.h} CosmeticDocument(s) delete KO [{e}]')
            else:
                logger.debug(f'{g.h} CosmeticDocument(s) deletion OK')
        # ItemDocument
        if ItemDocument.objects(bearer=g.Creature.id):
            try:
                logger.debug(f'{g.h} ItemDocument(s) deletion >>')
                ItemDocument.objects(bearer=g.Creature.id).delete()
            except Exception as e:
                logger.error(f'{g.h} ItemDocument(s) delete KO [{e}]')
            else:
                logger.debug(f'{g.h} ItemDocument(s) deletion OK')

        # Now we can delete the Creature itself
        if CreatureDocument.objects(_id=g.Creature.id).count() == 1:
            logger.debug(f'{g.h} CreatureDocument deletion >>')
            CreatureDocument.objects(_id=g.Creature.id).first().delete()
            logger.debug(f'{g.h} CreatureDocument deletion OK')
    except Exception as e:
        msg = f'{g.h} Creature delete KO [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Creature delete OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": None,
            }
        ), 200
