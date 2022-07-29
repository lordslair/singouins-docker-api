#!/usr/bin/env python3
# -*- coding: utf8 -*-

from flask                         import Flask, jsonify, request
from flask_jwt_extended            import (JWTManager,
                                           jwt_required,
                                           get_jwt_identity)
from flask_cors                    import CORS
from flask_swagger_ui              import get_swaggerui_blueprint

from prometheus_flask_exporter     import PrometheusMetrics

from werkzeug.middleware.proxy_fix import ProxyFix

from nosql.initialize              import initialize_redis
from mysql.initialize              import initialize_db

from variables                     import *
from utils.gunilog                 import *

# Imports of endpoint functions
import                      routes.internal.creature
import                      routes.internal.creature.cds
import                      routes.internal.creature.effects
import                      routes.internal.creature.equipment
import                      routes.internal.creature.pa
import                      routes.internal.creature.position
import                      routes.internal.creature.stats
import                      routes.internal.creature.statuses
import                      routes.internal.creature.wallet
import                      routes.internal.discord
import                      routes.internal.korp
import                      routes.internal.meta
import                      routes.internal.squad
import                      routes.internal.up

import                      routes.external.auth
import                      routes.external.log
import                      routes.external.map
import                      routes.external.meta
import                      routes.external.mypc
import                      routes.external.mypc.action
import                      routes.external.mypc.action_resolver
import                      routes.external.mypc.cds
import                      routes.external.mypc.effects
import                      routes.external.mypc.events
import                      routes.external.mypc.instance
import                      routes.external.mypc.item
import                      routes.external.mypc.inventory
import                      routes.external.mypc.korp
import                      routes.external.mypc.mp
import                      routes.external.mypc.pa
import                      routes.external.mypc.squad
import                      routes.external.mypc.stats
import                      routes.external.mypc.statuses
import                      routes.external.mypc.view
import                      routes.external.pc

app = Flask(__name__)
CORS(app)                        # We wrap around all the app the CORS
metrics = PrometheusMetrics(app) # We wrap around all the app the metrics

# Setup the flask_swagger_ui extension
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    '/swagger',
    '/static/swagger.yaml',
    config = { 'app_name': "S&P Internal API" }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix='/swagger')

# Setup the ProxyFix to have the Real-IP in the logs
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = SEP_SECRET_KEY
jwt = JWTManager(app)

#
# Routes /check (k8s livenessProbe)
#
@app.route('/check', methods=['GET'])
def check():
    return jsonify({"msg": f'UP and running',
                    "success": True,
                    "payload": None}), 200

#
# Routes /auth
#
app.add_url_rule('/auth/confirm/<string:token>',
                 methods=['GET'],
                 view_func=routes.external.auth.auth_confirm)
app.add_url_rule('/auth/delete',
                 methods=['DELETE'],
                 view_func=routes.external.auth.auth_delete)
app.add_url_rule('/auth/forgotpassword',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_forgotpassword)
app.add_url_rule('/auth/infos',
                 methods=['GET'],
                 view_func=routes.external.auth.auth_infos)
app.add_url_rule('/auth/login',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_login)
app.add_url_rule('/auth/refresh',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_refresh)
app.add_url_rule('/auth/register',
                 methods=['POST'],
                 view_func=routes.external.auth.auth_register)
#
# Routes /meta
#
app.add_url_rule('/meta/item/<string:metatype>',
                 methods=['GET'],
                 view_func=routes.external.meta.external_meta_get_one)
#
# Routes: /pc
#
app.add_url_rule('/pc/<int:creatureid>',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_get_one)

app.add_url_rule('/pc/<int:creatureid>/item',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_item_get_all)

app.add_url_rule('/pc/<int:creatureid>/event',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_event_get_all)
#
# Routes: /mypc
#
app.add_url_rule('/mypc',
                 methods=['POST'],
                 view_func=routes.external.mypc.mypc_add)
app.add_url_rule('/mypc',
                 methods=['GET'],
                 view_func=routes.external.mypc.mypc_get_all)
app.add_url_rule('/mypc/<int:pcid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.mypc_del)

#
# Routes: /pa
#
app.add_url_rule('/mypc/<int:pcid>/pa',
                 methods=['GET'],
                 view_func=routes.external.mypc.pa.pa_get)

#
# Routes: /stats
#
app.add_url_rule('/mypc/<int:pcid>/stats',
                 methods=['GET'],
                 view_func=routes.external.mypc.stats.stats_get)

#
# Routes: /cds
#         /effects
#         /statuses
#
app.add_url_rule('/mypc/<int:pcid>/cds',
                 methods=['GET'],
                 view_func=routes.external.mypc.cds.cds_get)
app.add_url_rule('/mypc/<int:pcid>/effects',
                 methods=['GET'],
                 view_func=routes.external.mypc.effects.effects_get)
app.add_url_rule('/mypc/<int:pcid>/statuses',
                 methods=['GET'],
                 view_func=routes.external.mypc.statuses.statuses_get)

#
# Routes: /view
#
app.add_url_rule('/mypc/<int:pcid>/view',
                 methods=['GET'],
                 view_func=routes.external.mypc.view.view_get)

#
# Routes: /mp
#
app.add_url_rule('/mypc/<int:pcid>/mp',
                 methods=['POST'],
                 view_func=routes.external.mypc.mp.mp_add)
app.add_url_rule('/mypc/<int:pcid>/mp/<int:mpid>',
                 methods=['GET'],
                 view_func=routes.external.mypc.mp.mp_get_one)
app.add_url_rule('/mypc/<int:pcid>/mp/<int:mpid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.mp.mp_del)
app.add_url_rule('/mypc/<int:pcid>/mp',
                 methods=['GET'],
                 view_func=routes.external.mypc.mp.mp_get_all)
app.add_url_rule('/mypc/<int:pcid>/mp/addressbook',
                 methods=['GET'],
                 view_func=routes.external.mypc.mp.addressbook_get)

#
# Routes /item
#
app.add_url_rule('/mypc/<int:pcid>/item',
                 methods=['GET'],
                 view_func=routes.external.mypc.item.item_get)

#
# Routes /inventory/item
#
app.add_url_rule('/mypc/<int:pcid>/inventory/item/<int:itemid>/dismantle',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_dismantle)
app.add_url_rule('/mypc/<int:pcid>/inventory/item/<int:itemid>/equip/<string:type>/<string:slotname>',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_equip)
app.add_url_rule('/mypc/<int:pcid>/inventory/item/<int:itemid>/offset/<int:offsetx>/<int:offsety>',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_offset)
app.add_url_rule('/mypc/<int:pcid>/inventory/item/<int:itemid>/offset',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.inventory.inventory_item_offset)
app.add_url_rule('/mypc/<int:pcid>/inventory/item/<int:itemid>/unequip/<string:type>/<string:slotname>',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_unequip)

#
# Routes: /instance
#
app.add_url_rule('/mypc/<int:pcid>/instance',
                 methods=['PUT'],
                 view_func=routes.external.mypc.instance.instance_add)
app.add_url_rule('/mypc/<int:pcid>/instance/<int:instanceid>',
                 methods=['GET'],
                 view_func=routes.external.mypc.instance.instance_get)
app.add_url_rule('/mypc/<int:pcid>/instance/<int:instanceid>/join',
                 methods=['POST'],
                 view_func=routes.external.mypc.instance.instance_join)
app.add_url_rule('/mypc/<int:pcid>/instance/<int:instanceid>/leave',
                 methods=['POST'],
                 view_func=routes.external.mypc.instance.instance_leave)
#
# Routes: /action/resolver
#
app.add_url_rule('/mypc/<int:pcid>/action/resolver/context',
                 methods=['POST'],
                 view_func=routes.external.mypc.action_resolver.action_resolver_context)
app.add_url_rule('/mypc/<int:pcid>/action/resolver/move',
                 methods=['POST'],
                 view_func=routes.external.mypc.action_resolver.action_resolver_move)
app.add_url_rule('/mypc/<int:pcid>/action/resolver/skill/<string:skill_name>',
                 methods=['PUT'],
                 view_func=routes.external.mypc.action_resolver.action_resolver_skill)

#
# Routes: /action
#
@app.route('/mypc/<int:pcid>/action/move', methods=['POST'])
@jwt_required()
def api_mypc_action_move(pcid):
    return jsonify({"msg": 'DEPRECATED', "success": True, "payload": RedisPa(fn_creature_get(None,pcid)[3]).get()}), 200
@app.route('/mypc/<int:pcid>/action/attack/<int:weaponid>/<int:targetid>', methods=['POST'])
@jwt_required()
def api_mypc_action_attack(pcid,weaponid,targetid):
    return jsonify({"msg": 'DEPRECATED', "success": True, "payload": None}), 200

app.add_url_rule('/mypc/<int:pcid>/action/reload/<int:weaponid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.action.action_weapon_reload)
app.add_url_rule('/mypc/<int:pcid>/action/unload/<int:weaponid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.action.action_weapon_unload)

#
# Routes: /events
#
app.add_url_rule('/mypc/<int:pcid>/event',
                 methods=['GET'],
                 view_func=routes.external.mypc.events.mypc_event_get_all)

#
# Routes /korp
#
app.add_url_rule('/mypc/<int:pcid>/korp/<int:korpid>',
                 methods=['GET'],
                 view_func=routes.external.mypc.korp.korp_get_one)
app.add_url_rule('/mypc/<int:pcid>/korp',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_create)
app.add_url_rule('/mypc/<int:pcid>/korp/<int:korpid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.korp.korp_delete)
app.add_url_rule('/mypc/<int:pcid>/korp/<int:korpid>/invite/<int:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_invite)
app.add_url_rule('/mypc/<int:pcid>/korp/<int:korpid>/kick/<int:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_kick)
app.add_url_rule('/mypc/<int:pcid>/korp/<int:korpid>/accept',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_accept)
app.add_url_rule('/mypc/<int:pcid>/korp/<int:korpid>/leave',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_leave)
app.add_url_rule('/mypc/<int:pcid>/korp/<int:korpid>/decline',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_decline)

#
# Routes /squad
#

app.add_url_rule('/mypc/<int:pcid>/squad/<int:squadid>',
                 methods=['GET'],
                 view_func=routes.external.mypc.squad.squad_get_one)
app.add_url_rule('/mypc/<int:pcid>/squad',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_create)
app.add_url_rule('/mypc/<int:pcid>/squad/<int:squadid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.squad.squad_delete)
app.add_url_rule('/mypc/<int:pcid>/squad/<int:squadid>/invite/<int:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_invite)
app.add_url_rule('/mypc/<int:pcid>/squad/<int:squadid>/kick/<int:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_kick)
app.add_url_rule('/mypc/<int:pcid>/squad/<int:squadid>/accept',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_accept)
app.add_url_rule('/mypc/<int:pcid>/squad/<int:squadid>/leave',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_leave)
app.add_url_rule('/mypc/<int:pcid>/squad/<int:squadid>/decline',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_decline)

#
# Routes /map
#
app.add_url_rule('/map/<int:mapid>',
                 methods=['GET'],
                 view_func=routes.external.map.map_get)
#
# Routes /log
#
app.add_url_rule('/log',
                 methods=['POST'],
                 view_func=routes.external.log.front)
#
# Routes /internal
#
# Routes /internal/creature/*
app.add_url_rule('/internal/creature',
                 methods=['PUT'],
                 view_func=routes.internal.creature.creature_add)
# Routes /internal/creature/{creatureid}
app.add_url_rule('/internal/creature/<int:creatureid>',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_get_one)
app.add_url_rule('/internal/creature/<int:creatureid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.creature_del)
# Routes /internal/creature/{creatureid}/cd/*
app.add_url_rule('/internal/creature/<int:creatureid>/cd/<string:skill_name>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.cds.creature_cd_add)
app.add_url_rule('/internal/creature/<int:creatureid>/cd/<string:skill_name>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.cds.creature_cd_del)
app.add_url_rule('/internal/creature/<int:creatureid>/cd/<string:skill_name>',
                 methods=['GET'],
                 view_func=routes.internal.creature.cds.creature_cd_get_one)
app.add_url_rule('/internal/creature/<int:creatureid>/cds',
                 methods=['GET'],
                 view_func=routes.internal.creature.cds.creature_cd_get_all)
# Routes /internal/creature/{creatureid}/equipment/*
app.add_url_rule('/internal/creature/<int:creatureid>/equipment',
                 methods=['GET'],
                 view_func=routes.internal.creature.equipment.creature_equipment)
app.add_url_rule('/internal/creature/<int:creatureid>/equipment/<int:itemid>/ammo/<string:operation>/<int:count>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.equipment.creature_equipment_modifiy)
# Routes /internal/creature/{creatureid}/effect/*
app.add_url_rule('/internal/creature/<int:creatureid>/effect/<string:effect_name>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.effects.creature_effect_add)
app.add_url_rule('/internal/creature/<int:creatureid>/effect/<string:effect_name>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.effects.creature_effect_del)
app.add_url_rule('/internal/creature/<int:creatureid>/effect/<string:effect_name>',
                 methods=['GET'],
                 view_func=routes.internal.creature.effects.creature_effect_get_one)
app.add_url_rule('/internal/creature/<int:creatureid>/effects',
                 methods=['GET'],
                 view_func=routes.internal.creature.effects.creature_effect_get_all)
# Routes /internal/creature/{creatureid}/kill/*
app.add_url_rule('/internal/creature/{creatureid}/kill/{victimid}',
                 methods=['POST'],
                 view_func=routes.internal.creature.pa.creature_pa_get)
# Routes /internal/creature/{creatureid}/pa/*
app.add_url_rule('/internal/creature/<int:creatureid>/pa',
                 methods=['GET'],
                 view_func=routes.internal.creature.pa.creature_pa_get)
app.add_url_rule('/internal/creature/<int:creatureid>/pa/consume/<int:redpa>/<int:bluepa>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.pa.creature_pa_consume)
app.add_url_rule('/internal/creature/<int:creatureid>/pa/reset',
                 methods=['PUT'],
                 view_func=routes.internal.creature.pa.creature_pa_reset)
# Routes /internal/creature/{creatureid}/position/*
app.add_url_rule('/internal/creature/<int:creatureid>/position/<int:x>/<int:y>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.position.creature_position_set)
# Routes /internal/creature/{creatureid}/status/*
app.add_url_rule('/internal/creature/<int:creatureid>/status/<string:status_name>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.statuses.creature_status_add)
app.add_url_rule('/internal/creature/<int:creatureid>/status/<string:status_name>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.statuses.creature_status_del)
app.add_url_rule('/internal/creature/<int:creatureid>/status/<string:status_name>',
                 methods=['GET'],
                 view_func=routes.internal.creature.statuses.creature_status_get_one)
app.add_url_rule('/internal/creature/<int:creatureid>/statuses',
                 methods=['GET'],
                 view_func=routes.internal.creature.statuses.creature_status_get_all)
# Routes /internal/creature/{creatureid}/stats/*
app.add_url_rule('/internal/creature/<int:creatureid>/stats',
                 methods=['GET'],
                 view_func=routes.internal.creature.stats.creature_stats)
app.add_url_rule('/internal/creature/<int:creatureid>/stats/hp/<string:operation>/<int:count>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.stats.creature_stats_hp_modify)
# Routes /internal/creature/{creatureid}/wallet/*
app.add_url_rule('/internal/creature/<int:creatureid>/wallet',
                 methods=['GET'],
                 view_func=routes.internal.creature.wallet.creature_wallet)
app.add_url_rule('/internal/creature/<int:creatureid>/wallet/<string:caliber>/<string:operation>/<int:count>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.wallet.creature_wallet_modify)
# Routes /internal/creatures/*
app.add_url_rule('/internal/creatures',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_get_all)
# Routes /internal/discord/*
app.add_url_rule('/internal/discord/link',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_link)
app.add_url_rule('/internal/discord/creature',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_creature_get_one)
app.add_url_rule('/internal/discord/creatures',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_creature_get_all)
app.add_url_rule('/internal/discord/user',
                 methods=['POST'],
                 view_func=routes.internal.discord.discord_user)
# Routes /internal/korp/*
app.add_url_rule('/internal/korp/<int:korpid>',
                 methods=['GET'],
                 view_func=routes.internal.korp.internal_korp_get_one)
app.add_url_rule('/internal/korps',
                 methods=['GET'],
                 view_func=routes.internal.korp.internal_korp_get_all)
# Routes /internal/meta/*
app.add_url_rule('/internal/meta/<string:metatype>',
                 methods=['GET'],
                 view_func=routes.internal.meta.internal_meta_get_one)
# Routes /internal/squad/*
app.add_url_rule('/internal/squad/<int:squadid>',
                 methods=['GET'],
                 view_func=routes.internal.squad.internal_squad_get_one)
app.add_url_rule('/internal/squads',
                 methods=['GET'],
                 view_func=routes.internal.squad.internal_squad_get_all)
# Routes /internal/up/*
app.add_url_rule('/internal/up',
                 methods=['GET'],
                 view_func=routes.internal.up.up_get)

if __name__ == '__main__':
    intercept_handler = InterceptHandler()
    logging.root.setLevel(LOG_LEVEL)

    seen = set()
    for name in [
        *logging.root.manager.loggerDict.keys(),
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
    ]:
        if name not in seen:
            seen.add(name.split(".")[0])
            logging.getLogger(name).handlers = [intercept_handler]

    logger.configure(handlers=[{"sink": sys.stdout}])

    options = {
        "bind":         GUNICORN_BIND,
        "workers":      GUNICORN_WORKERS,
        "threads":      GUNICORN_THREADS,
        "accesslog":    "-",
        "errorlog":     "-",
        "logger_class": StubbedGunicornLogger,
        "reload":       GUNICORN_RELOAD,
        "chdir":        GUNICORN_CHDIR
    }

    StandaloneApplication(app, options).run()
