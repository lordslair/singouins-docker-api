# -*- coding: utf8 -*-

import uuid

from flask import g, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from loguru import logger
from pydantic import BaseModel, ValidationError
from typing import Optional

from nosql.models.RedisPa import RedisPa

from mongo.models.Cosmetic import (
    CosmeticData,
    CosmeticDocument,
)
from mongo.models.Creature import (
    CreatureDocument,
    CreatureHP,
    CreatureSlot,
    CreatureSlots,
    CreatureStats,
    CreatureStatsType,
    CreatureSquad,
    CreatureKorp,
)
from mongo.models.Highscore import (
    HighscoreDocument,
    HighscoreGeneral,
    HighscoreInternal,
    HighscoreInternalGenericResource,
    HighscoreProfession,
)
from mongo.models.Item import ItemDocument
from mongo.models.Profession import ProfessionDocument
from mongo.models.Satchel import (
    SatchelDocument,
    SatchelAmmo,
    SatchelCurrency,
    SatchelResource,
    SatchelShard,
)

from utils.decorators import (
    check_creature_exists,
    check_is_json,
    check_user_exists,
    )

from variables import metaNames


class CosmeticDataSchema(BaseModel):
    hasGender: bool
    beforeArmor: bool
    hideArmor: Optional[bool]  # Allowing null (None) values


class CosmeticSchema(BaseModel):
    metaid: int
    data: CosmeticDataSchema  # Nested model


class EquipmentItemSchema(BaseModel):
    metaid: int
    metatype: str


class EquipmentSchema(BaseModel):
    righthand: EquipmentItemSchema
    lefthand: EquipmentItemSchema


class AddSingouinSchema(BaseModel):
    class: int
    gender: bool
    name: str
    race: int
    cosmetic: CosmeticSchema  # Nested model
    equipment: EquipmentSchema  # Nested model


#
# Routes /mypc/*
#
# API: POST /mypc
@jwt_required()
# Custom decorators
@check_is_json
@check_user_exists
def mypc_add():
    g.h = f'[User.id:{g.User.id}]'

    try:
        Singouin = AddSingouinSchema(**request.json)  # Validate and parse the JSON data
    except ValidationError as e:
        return jsonify(
            {
                "success": False,
                "msg": "Validation and parsing error",
                "payload": e.errors(),
            }
        ), 400

    if CreatureDocument.objects(name=Singouin.name).count() != 0:
        msg = f'{g.h} Creature already exists (Creature.name:{Singouin.name})'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    # Define the mapping of classes to their specifications
    specs = {
        1: {'spec_b':  0, 'spec_g':  0, 'spec_m': 10, 'spec_p':  0, 'spec_r':  0, 'spec_v':  0},
        2: {'spec_b':  0, 'spec_g':  0, 'spec_m':  0, 'spec_p':  0, 'spec_r': 10, 'spec_v':  0},
        3: {'spec_b':  0, 'spec_g': 10, 'spec_m':  0, 'spec_p':  0, 'spec_r':  0, 'spec_v':  0},
        4: {'spec_b':  0, 'spec_g':  0, 'spec_m':  0, 'spec_p':  0, 'spec_r':  0, 'spec_v': 10},
        5: {'spec_b':  0, 'spec_g':  0, 'spec_m':  0, 'spec_p': 10, 'spec_r':  0, 'spec_v':  0},
        6: {'spec_b': 10, 'spec_g':  0, 'spec_m':  0, 'spec_p':  0, 'spec_r':  0, 'spec_v':  0}
    }

    # We grab the race wanted from metaRaces
    metaRace = metaNames['race'][Singouin.race]
    if metaRace is None:
        msg = f'{g.h} MetaRace not found (race:{Singouin.race})'
        logger.warning(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200

    try:
        Creature = CreatureDocument(
            _id=uuid.uuid3(uuid.NAMESPACE_DNS, Singouin.name),
            account=g.User.id,
            gender=Singouin.gender,
            hp=CreatureHP(
                base=specs[Singouin.class]['spec_m'] + metaRace['min_m'] + 100,
                current=specs[Singouin.class]['spec_m'] + metaRace['min_m'] + 100,
                max=specs[Singouin.class]['spec_m'] + metaRace['min_m'] + 100,
                ),
            korp=CreatureKorp(),
            name=Singouin.name,
            race=Singouin.race,
            squad=CreatureSquad(),
            slots=CreatureSlots(),
            stats=CreatureStats(
                spec=CreatureStatsType(
                    b=specs[Singouin.class]['spec_b'],
                    g=specs[Singouin.class]['spec_g'],
                    m=specs[Singouin.class]['spec_m'],
                    p=specs[Singouin.class]['spec_p'],
                    r=specs[Singouin.class]['spec_r'],
                    v=specs[Singouin.class]['spec_v'],
                ),
                race=CreatureStatsType(
                    b=metaRace['min_b'],
                    g=metaRace['min_g'],
                    m=metaRace['min_m'],
                    p=metaRace['min_p'],
                    r=metaRace['min_r'],
                    v=metaRace['min_v'],
                ),
                total=CreatureStatsType(
                    b=specs[Singouin.class]['spec_b'] + metaRace['min_b'],
                    g=specs[Singouin.class]['spec_g'] + metaRace['min_g'],
                    m=specs[Singouin.class]['spec_m'] + metaRace['min_m'],
                    p=specs[Singouin.class]['spec_p'] + metaRace['min_p'],
                    r=specs[Singouin.class]['spec_r'] + metaRace['min_r'],
                    v=specs[Singouin.class]['spec_v'] + metaRace['min_v'],
                ),
            ),
        )
        Creature.save()
    except Exception as e:
        msg = f'{g.h} Creature creation KO ({Singouin.name}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        try:
            Satchel = SatchelDocument(
                _id=uuid.uuid3(uuid.NAMESPACE_DNS, Creature.name),
                ammo=SatchelAmmo(),
                currency=SatchelCurrency(),
                resource=SatchelResource(),
                shard=SatchelShard(),
                )
            Satchel.save()
        except Exception as e:
            msg = f'{g.h} SatchelDocument creation KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.debug(f'{g.h} SatchelDocument creation OK')

        try:
            Cosmetic = CosmeticDocument(
                bearer=Creature.id,
                metaid=Singouin.cosmetic.metaid,
                data=CosmeticData(
                    beforeArmor=Singouin.cosmetic.data.beforeArmor,
                    hasGender=Singouin.cosmetic.data.hasGender,
                    hideArmor=Singouin.cosmetic.data.hideArmor,
                    )
                )
            Cosmetic.save()
        except Exception as e:
            msg = f'{g.h} CosmeticDocument creation KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.trace(f'{g.h} CosmeticDocument creation OK')

        try:
            newHighscore = HighscoreDocument(
                _id=Creature.id,
                general=HighscoreGeneral(),
                internal=HighscoreInternal(
                    fur=HighscoreInternalGenericResource(),
                    item=HighscoreInternalGenericResource(),
                    leather=HighscoreInternalGenericResource(),
                    meat=HighscoreInternalGenericResource(),
                    ore=HighscoreInternalGenericResource(),
                    shard=HighscoreInternalGenericResource(),
                    skin=HighscoreInternalGenericResource(),
                    ),
                profession=HighscoreProfession(),
            )
            newHighscore.save()
        except Exception as e:
            msg = f'{g.h} HighscoreDocument creation KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.debug(f'{g.h} HighscoreDocument creation OK')

        try:
            newProfession = ProfessionDocument(
                _id=Creature.id,
                recycling=0,
            )
            newProfession.save()
        except Exception as e:
            msg = f'{g.h} ProfessionDocument creation KO [{e}]'
            logger.error(msg)
            return jsonify(
                {
                    "success": False,
                    "msg": msg,
                    "payload": None,
                }
            ), 200
        else:
            logger.debug(f'{g.h} ProfessionDocument creation OK')

        # Loop over the equipment fields dynamically and get the field names
        for slot, value in Singouin.equipment.__dict__.items():
            # slot is 'righthand' or 'lefthand'
            # value is the actual EquipmentItem instance (meta_id, meta_type)

            EquipmentItem = getattr(Singouin.equipment, slot)
            itemmeta = metaNames[EquipmentItem.metatype][EquipmentItem.metaid]
            ammo = None

            """
            Gruik: This is done only for Alpha/Beta
            It is needed as players can't either find/buy/craft ammo
            So we fill the weapon when we create it
            """
            if EquipmentItem.metatype == 'weapon' and itemmeta['ranged']:
                ammo = itemmeta['max_ammo']
            """
            # TODO: Delete the block above for poduction
            """

            try:
                Item = ItemDocument(
                    _id=uuid.uuid4(),
                    ammo=ammo,
                    bearer=Creature.id,
                    metatype=EquipmentItem.metatype,
                    metaid=EquipmentItem.metaid,
                    )
                Item.save()
                # We put the item in the slot
                setattr(
                    Creature.slots,
                    slot,
                    CreatureSlot(
                        id=Item.id,
                        metaid=Item.metaid,
                        metatype=Item.metatype,
                        )
                )
                Creature.save()
            except Exception as e:
                msg = f'{g.h} ItemDocument creation KO [{e}]'
                logger.error(msg)
                return jsonify(
                    {
                        "success": False,
                        "msg": msg,
                        "payload": None,
                    }
                ), 200
            else:
                logger.debug(f'{g.h} ItemDocument({slot}) creation OK')

        # Everything went well
        msg = f'{g.h} Creature creation OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": Creature.to_mongo().to_dict(),
            }
        ), 201


# API: GET /mypc
@jwt_required()
# Custom decorators
@check_user_exists
def mypc_get_all():
    g.h = f'[User.id:{g.User.id}]'
    try:
        Creatures = CreatureDocument.objects(account=g.User.id)
    except Exception as e:
        msg = f'{g.h} Creatures query KO (username:{get_jwt_identity()}) [{e}]'
        logger.error(msg)
        return jsonify(
            {
                "success": False,
                "msg": msg,
                "payload": None,
            }
        ), 200
    else:
        msg = f'{g.h} Creatures Query OK'
        logger.debug(msg)
        return jsonify(
            {
                "success": True,
                "msg": msg,
                "payload": [Creature.to_mongo() for Creature in Creatures],
            }
        ), 200


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
        if RedisPa(creatureuuid=g.Creature.id).destroy():
            logger.trace(f'{g.h} RedisPa delete OK')
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
