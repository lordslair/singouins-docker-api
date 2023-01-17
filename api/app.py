#!/usr/bin/env python3
# -*- coding: utf8 -*-

import sys
import time

from flask                         import Flask, jsonify, g
from flask_jwt_extended            import JWTManager
from flask_cors                    import CORS
from flask_uuid                    import FlaskUUID
from flask_swagger_ui              import get_swaggerui_blueprint

from prometheus_flask_exporter     import PrometheusMetrics

from werkzeug.middleware.proxy_fix import ProxyFix

from variables                     import (SEP_SECRET_KEY,
                                           GUNICORN_BIND,
                                           GUNICORN_CHDIR,
                                           GUNICORN_RELOAD,
                                           GUNICORN_THREADS,
                                           GUNICORN_WORKERS)
from utils.gunilog                 import (InterceptHandler,
                                           LOG_LEVEL,
                                           logger,
                                           logging,
                                           StandaloneApplication,
                                           StubbedGunicornLogger)

# Imports of endpoint functions
import routes.internal.creature
import routes.internal.creature.auction
import routes.internal.creature.cds
import routes.internal.creature.context
import routes.internal.creature.effects
import routes.internal.creature.equipment
import routes.internal.creature.highscore
import routes.internal.creature.inventory
import routes.internal.creature.item
import routes.internal.creature.kill
import routes.internal.creature.pa
import routes.internal.creature.position
import routes.internal.creature.stats
import routes.internal.creature.statuses
import routes.internal.creature.user
import routes.internal.creature.view
import routes.internal.creature.wallet
import routes.internal.discord
import routes.internal.instance
import routes.internal.korp
import routes.internal.meta
import routes.internal.squad
import routes.internal.statistics
import routes.internal.up

import routes.external.auth
import routes.external.log
import routes.external.map
import routes.external.meta
import routes.external.mypc
import routes.external.mypc.action
import routes.external.mypc.action_craft
import routes.external.mypc.action_resolver
import routes.external.mypc.cds
import routes.external.mypc.effects
import routes.external.mypc.events
import routes.external.mypc.instance
import routes.external.mypc.item
import routes.external.mypc.inventory
import routes.external.mypc.korp
import routes.external.mypc.pa
import routes.external.mypc.squad
import routes.external.mypc.stats
import routes.external.mypc.statuses
import routes.external.mypc.view
import routes.external.pc

app = Flask(__name__)
CORS(app)                         # We wrap around all the app the CORS
FlaskUUID(app)                    # We wrap around all the app the UUID control
metrics = PrometheusMetrics(app)  # We wrap around all the app the metrics

# Setup the flask_swagger_ui extension
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    '/swagger',
    '/static/swagger.yaml',
    config={'app_name': "S&P Internal API"}
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix='/swagger')

# Setup the ProxyFix to have the Real-IP in the logs
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Setup the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = SEP_SECRET_KEY
jwt = JWTManager(app)


@app.before_request
def before_request_time():
    g.start = time.time()


@app.after_request
def after_request_time(response):
    response.headers["X-Custom-Elapsed"] = time.time() - g.start
    return response


#
# Routes /check (k8s livenessProbe)
#
@app.route('/check', methods=['GET'])
def check():
    return jsonify({"msg": 'UP and running',
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
app.add_url_rule('/pc/<uuid:creatureuuid>',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_get_one)

app.add_url_rule('/pc/<uuid:creatureuuid>/item',
                 methods=['GET'],
                 view_func=routes.external.pc.pc_item_get_all)

app.add_url_rule('/pc/<uuid:creatureuuid>/event',
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
app.add_url_rule('/mypc/<uuid:pcid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.mypc_del)

#
# Routes: /pa
#
app.add_url_rule('/mypc/<uuid:pcid>/pa',
                 methods=['GET'],
                 view_func=routes.external.mypc.pa.pa_get)

#
# Routes: /stats
#
app.add_url_rule('/mypc/<uuid:pcid>/stats',
                 methods=['GET'],
                 view_func=routes.external.mypc.stats.stats_get)

#
# Routes: /cds
#         /effects
#         /statuses
#
app.add_url_rule('/mypc/<uuid:creatureuuid>/cds',
                 methods=['GET'],
                 view_func=routes.external.mypc.cds.cds_get)
app.add_url_rule('/mypc/<uuid:creatureuuid>/effects',
                 methods=['GET'],
                 view_func=routes.external.mypc.effects.effects_get)
app.add_url_rule('/mypc/<uuid:creatureuuid>/statuses',
                 methods=['GET'],
                 view_func=routes.external.mypc.statuses.statuses_get)

#
# Routes: /view
#
app.add_url_rule('/mypc/<uuid:pcid>/view',
                 methods=['GET'],
                 view_func=routes.external.mypc.view.view_get)

#
# Routes /item
#
app.add_url_rule('/mypc/<uuid:pcid>/item',
                 methods=['GET'],
                 view_func=routes.external.mypc.item.item_get)

#
# Routes /inventory/item
#
app.add_url_rule('/mypc/<uuid:pcid>/inventory/item/<uuid:itemid>/dismantle',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_dismantle)
app.add_url_rule('/mypc/<uuid:pcid>/inventory/item/<uuid:itemid>/equip/<string:type>/<string:slotname>',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_equip)
app.add_url_rule('/mypc/<uuid:pcid>/inventory/item/<uuid:itemid>/offset/<int:offsetx>/<int:offsety>',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_offset)
app.add_url_rule('/mypc/<uuid:pcid>/inventory/item/<uuid:itemid>/offset',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.inventory.inventory_item_offset)
app.add_url_rule('/mypc/<uuid:pcid>/inventory/item/<uuid:itemid>/unequip/<string:type>/<string:slotname>',
                 methods=['POST'],
                 view_func=routes.external.mypc.inventory.inventory_item_unequip)

#
# Routes: /instance
#
app.add_url_rule('/mypc/<uuid:pcid>/instance',
                 methods=['PUT'],
                 view_func=routes.external.mypc.instance.instance_add)
app.add_url_rule('/mypc/<uuid:pcid>/instance/<uuid:instanceid>',
                 methods=['GET'],
                 view_func=routes.external.mypc.instance.instance_get)
app.add_url_rule('/mypc/<uuid:pcid>/instance/<uuid:instanceid>/join',
                 methods=['POST'],
                 view_func=routes.external.mypc.instance.instance_join)
app.add_url_rule('/mypc/<uuid:pcid>/instance/<uuid:instanceid>/leave',
                 methods=['POST'],
                 view_func=routes.external.mypc.instance.instance_leave)
#
# Routes: /action/resolver
#
app.add_url_rule('/mypc/<uuid:creatureuuid>/action/resolver/context',
                 methods=['POST'],
                 view_func=routes.external.mypc.action_resolver.action_resolver_context)
app.add_url_rule('/mypc/<uuid:creatureuuid>/action/resolver/move',
                 methods=['POST'],
                 view_func=routes.external.mypc.action_resolver.action_resolver_move)
app.add_url_rule('/mypc/<uuid:creatureuuid>/action/resolver/skill/<string:skill_name>',
                 methods=['PUT'],
                 view_func=routes.external.mypc.action_resolver.action_resolver_skill)

#
# Routes: /action
#
app.add_url_rule('/mypc/<uuid:pcid>/action/reload/<uuid:weaponid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.action.action_weapon_reload)
app.add_url_rule('/mypc/<uuid:pcid>/action/unload/<uuid:weaponid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.action.action_weapon_unload)
app.add_url_rule('/mypc/<uuid:pcid>/action/craft/consumable/<int:recipeid>',
                 methods=['PUT'],
                 view_func=routes.external.mypc.action_craft.action_craft_consumable)

#
# Routes: /events
#
app.add_url_rule('/mypc/<uuid:pcid>/event',
                 methods=['GET'],
                 view_func=routes.external.mypc.events.mypc_event_get_all)

#
# Routes /korp
#
app.add_url_rule('/mypc/<uuid:pcid>/korp/<uuid:korpid>',
                 methods=['GET'],
                 view_func=routes.external.mypc.korp.korp_get_one)
app.add_url_rule('/mypc/<uuid:pcid>/korp',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_create)
app.add_url_rule('/mypc/<uuid:pcid>/korp/<uuid:korpid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.korp.korp_delete)
app.add_url_rule('/mypc/<uuid:pcid>/korp/<uuid:korpid>/invite/<uuid:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_invite)
app.add_url_rule('/mypc/<uuid:pcid>/korp/<uuid:korpid>/kick/<uuid:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_kick)
app.add_url_rule('/mypc/<uuid:pcid>/korp/<uuid:korpid>/accept',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_accept)
app.add_url_rule('/mypc/<uuid:pcid>/korp/<uuid:korpid>/leave',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_leave)
app.add_url_rule('/mypc/<uuid:pcid>/korp/<uuid:korpid>/decline',
                 methods=['POST'],
                 view_func=routes.external.mypc.korp.korp_decline)

#
# Routes /squad
#

app.add_url_rule('/mypc/<uuid:pcid>/squad/<uuid:squadid>',
                 methods=['GET'],
                 view_func=routes.external.mypc.squad.squad_get_one)
app.add_url_rule('/mypc/<uuid:pcid>/squad',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_create)
app.add_url_rule('/mypc/<uuid:pcid>/squad/<uuid:squadid>',
                 methods=['DELETE'],
                 view_func=routes.external.mypc.squad.squad_delete)
app.add_url_rule('/mypc/<uuid:pcid>/squad/<uuid:squadid>/invite/<uuid:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_invite)
app.add_url_rule('/mypc/<uuid:pcid>/squad/<uuid:squadid>/kick/<uuid:targetid>',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_kick)
app.add_url_rule('/mypc/<uuid:pcid>/squad/<uuid:squadid>/accept',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_accept)
app.add_url_rule('/mypc/<uuid:pcid>/squad/<uuid:squadid>/leave',
                 methods=['POST'],
                 view_func=routes.external.mypc.squad.squad_leave)
app.add_url_rule('/mypc/<uuid:pcid>/squad/<uuid:squadid>/decline',
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
app.add_url_rule('/internal/creature/<uuid:creatureid>',
                 methods=['GET'],
                 view_func=routes.internal.creature.creature_get_one)
app.add_url_rule('/internal/creature/<uuid:creatureid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.creature_del)
# Routes /internal/creature/{creatureid}/auction/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/auction/<uuid:itemid>',
                 methods=['POST'],
                 view_func=routes.internal.creature.auction.creature_auction_buy)
app.add_url_rule('/internal/creature/<uuid:creatureid>/auction/<uuid:itemid>',
                 methods=['GET'],
                 view_func=routes.internal.creature.auction.creature_auction_get)
app.add_url_rule('/internal/creature/<uuid:creatureid>/auction/<uuid:itemid>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.auction.creature_auction_sell)
app.add_url_rule('/internal/creature/<uuid:creatureid>/auction/<uuid:itemid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.auction.creature_auction_remove)
# Routes /internal/creature/{creatureid}/auction/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/auctions',
                 methods=['POST'],
                 view_func=routes.internal.creature.auction.creature_auctions_search)
# Routes /internal/creature/{creatureid}/cd/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/cd/<string:skill_name>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.cds.creature_cd_add)
app.add_url_rule('/internal/creature/<uuid:creatureid>/cd/<string:skill_name>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.cds.creature_cd_del)
app.add_url_rule('/internal/creature/<uuid:creatureid>/cd/<string:skill_name>',
                 methods=['GET'],
                 view_func=routes.internal.creature.cds.creature_cd_get_one)
app.add_url_rule('/internal/creature/<uuid:creatureid>/cds',
                 methods=['GET'],
                 view_func=routes.internal.creature.cds.creature_cd_get_all)
# Routes /internal/creature/{creatureid}/context/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/context',
                 methods=['GET'],
                 view_func=routes.internal.creature.context.creature_context_get)
# Routes /internal/creature/{creatureid}/equipment/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/equipment',
                 methods=['GET'],
                 view_func=routes.internal.creature.equipment.creature_equipment)
app.add_url_rule('/internal/creature/<uuid:creatureid>/equipment/<uuid:itemid>/ammo/<string:operation>/<int:count>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.equipment.creature_equipment_modifiy)
# Routes /internal/creature/{creatureid}/effect/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/effect/<string:effect_name>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.effects.creature_effect_add)
app.add_url_rule('/internal/creature/<uuid:creatureid>/effect/<string:effect_name>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.effects.creature_effect_del)
app.add_url_rule('/internal/creature/<uuid:creatureid>/effect/<string:effect_name>',
                 methods=['GET'],
                 view_func=routes.internal.creature.effects.creature_effect_get_one)
app.add_url_rule('/internal/creature/<uuid:creatureid>/effects',
                 methods=['GET'],
                 view_func=routes.internal.creature.effects.creature_effect_get_all)
# Routes /internal/creature/{creatureid}/highscore/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/highscore',
                 methods=['GET'],
                 view_func=routes.internal.creature.highscore.creature_highscore_get)
# Routes /internal/creature/{creatureid}/inventory/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/inventory',
                 methods=['GET'],
                 view_func=routes.internal.creature.inventory.creature_inventory_get)
# Routes /internal/creature/{creatureid}/item/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/item',
                 methods=['PUT'],
                 view_func=routes.internal.creature.item.creature_item_add)
app.add_url_rule('/internal/creature/<uuid:creatureid>/item/<uuid:itemid>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.item.creature_item_del)
# Routes /internal/creature/{creatureid}/kill/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/kill/<uuid:victimid>',
                 methods=['POST'],
                 view_func=routes.internal.creature.kill.creature_kill)
# Routes /internal/creature/{creatureid}/pa/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/pa',
                 methods=['GET'],
                 view_func=routes.internal.creature.pa.creature_pa_get)
app.add_url_rule('/internal/creature/<uuid:creatureid>/pa/consume/<int:redpa>/<int:bluepa>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.pa.creature_pa_consume)
app.add_url_rule('/internal/creature/<uuid:creatureid>/pa/reset',
                 methods=['PUT'],
                 view_func=routes.internal.creature.pa.creature_pa_reset)
# Routes /internal/creature/{creatureid}/position/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/position/<int:x>/<int:y>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.position.creature_position_set)
# Routes /internal/creature/{creatureid}/status/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/status/<string:status_name>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.statuses.creature_status_add)
app.add_url_rule('/internal/creature/<uuid:creatureid>/status/<string:status_name>',
                 methods=['DELETE'],
                 view_func=routes.internal.creature.statuses.creature_status_del)
app.add_url_rule('/internal/creature/<uuid:creatureid>/status/<string:status_name>',
                 methods=['GET'],
                 view_func=routes.internal.creature.statuses.creature_status_get_one)
app.add_url_rule('/internal/creature/<uuid:creatureid>/statuses',
                 methods=['GET'],
                 view_func=routes.internal.creature.statuses.creature_status_get_all)
# Routes /internal/creature/{creatureid}/stats/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/stats',
                 methods=['GET'],
                 view_func=routes.internal.creature.stats.creature_stats)
app.add_url_rule('/internal/creature/<uuid:creatureid>/stats/hp/<string:operation>/<int:count>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.stats.creature_stats_hp_modify)
# Routes /internal/creature/{creatureid}/wallet/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/wallet',
                 methods=['GET'],
                 view_func=routes.internal.creature.wallet.creature_wallet)
app.add_url_rule('/internal/creature/<uuid:creatureid>/wallet/<string:caliber>/<string:operation>/<int:count>',
                 methods=['PUT'],
                 view_func=routes.internal.creature.wallet.creature_wallet_modify)
# Routes /internal/creature/{creatureid}/user/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/user',
                 methods=['GET'],
                 view_func=routes.internal.creature.user.creature_user)
# Routes /internal/creature/{creatureid}/view/*
app.add_url_rule('/internal/creature/<uuid:creatureid>/view',
                 methods=['GET'],
                 view_func=routes.internal.creature.view.creature_view_get)
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
# Routes /internal/instance/*
app.add_url_rule('/internal/instances',
                 methods=['GET'],
                 view_func=routes.internal.instance.internal_instance_get_all)
# Routes /internal/korp/*
app.add_url_rule('/internal/korp/<uuid:korpid>',
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
app.add_url_rule('/internal/squad/<uuid:squadid>',
                 methods=['GET'],
                 view_func=routes.internal.squad.internal_squad_get_one)
app.add_url_rule('/internal/squads',
                 methods=['GET'],
                 view_func=routes.internal.squad.internal_squad_get_all)
# Routes /internal/statistics/*
app.add_url_rule('/internal/statistics/highscores',
                 methods=['GET'],
                 view_func=routes.internal.statistics.statistics_highscores)
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
        "bind": GUNICORN_BIND,
        "workers": GUNICORN_WORKERS,
        "threads": GUNICORN_THREADS,
        "accesslog": "-",
        "errorlog": "-",
        "logger_class": StubbedGunicornLogger,
        "reload": GUNICORN_RELOAD,
        "chdir": GUNICORN_CHDIR
    }

    StandaloneApplication(app, options).run()
