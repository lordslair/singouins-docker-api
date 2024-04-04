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

import routes.external.mypc.action
import routes.external.mypc.action.profession
import routes.external.mypc.instance

import routes.external.auth
import routes.external.log
import routes.external.map
import routes.external.meta
import routes.external.mypc
import routes.external.mypc.cds
import routes.external.mypc.effects
import routes.external.mypc.events
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
    config={'app_name': "Singouins API"}
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
    return jsonify(
        {
            "msg": 'UP and running',
            "success": True,
            "payload": None,
            }
        ), 200


#
# Routes /auth
#
app.add_url_rule(
    '/auth/confirm/<string:token>',
    methods=['GET'],
    view_func=routes.external.auth.confirm,
    )
app.add_url_rule(
    '/auth/delete',
    methods=['DELETE'],
    view_func=routes.external.auth.delete,
    )
app.add_url_rule(
    '/auth/forgotpassword',
    methods=['POST'],
    view_func=routes.external.auth.forgot_password,
    )
app.add_url_rule(
    '/auth/infos',
    methods=['GET'],
    view_func=routes.external.auth.infos,
    )
app.add_url_rule(
    '/auth/login',
    methods=['POST'],
    view_func=routes.external.auth.login,
    )
app.add_url_rule(
    '/auth/refresh',
    methods=['POST'],
    view_func=routes.external.auth.refresh,
    )
app.add_url_rule(
    '/auth/register',
    methods=['POST'],
    view_func=routes.external.auth.auth_register,
    )
#
# Routes /meta
#
app.add_url_rule(
    '/meta/item/<string:metatype>',
    methods=['GET'],
    view_func=routes.external.meta.external_meta_get_one,
    )
#
# Routes: /pc
#
app.add_url_rule(
    '/pc/<uuid:creatureuuid>',
    methods=['GET'],
    view_func=routes.external.pc.pc_get_one,
    )
app.add_url_rule(
    '/pc/<uuid:creatureuuid>/item',
    methods=['GET'],
    view_func=routes.external.pc.pc_item_get_all,
    )
app.add_url_rule(
    '/pc/<uuid:creatureuuid>/event',
    methods=['GET'],
    view_func=routes.external.pc.pc_event_get_all,
    )
#
# Routes: /mypc
#
app.add_url_rule(
    '/mypc',
    methods=['POST'],
    view_func=routes.external.mypc.mypc_add,
    )
app.add_url_rule(
    '/mypc',
    methods=['GET'],
    view_func=routes.external.mypc.mypc_get_all,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>',
    methods=['DELETE'],
    view_func=routes.external.mypc.mypc_del,
    )
#
# Routes: /pa
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/pa',
    methods=['GET'],
    view_func=routes.external.mypc.pa.pa_get,
    )
#
# Routes: /stats
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/stats',
    methods=['GET'],
    view_func=routes.external.mypc.stats.stats_get,
    )
#
# Routes: /cds
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/cds',
    methods=['GET'],
    view_func=routes.external.mypc.cds.cds_get,
    )
#
# Routes: /effects
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/effects',
    methods=['GET'],
    view_func=routes.external.mypc.effects.effects_get,
    )
#
# Routes: /statuses
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/statuses',
    methods=['GET'],
    view_func=routes.external.mypc.statuses.statuses_get,
    )
#
# Routes: /view
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/view',
    methods=['GET'],
    view_func=routes.external.mypc.view.view_get,
    )
#
# Routes /item
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/item',
    methods=['GET'],
    view_func=routes.external.mypc.item.item_get,
    )
#
# Routes /inventory/item
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/equip/<string:type>/<string:slotname>',
    methods=['POST'],
    view_func=routes.external.mypc.inventory.inventory_item_equip,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/offset/<int:offsetx>/<int:offsety>',
    methods=['POST'],
    view_func=routes.external.mypc.inventory.inventory_item_offset,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/offset',
    methods=['DELETE'],
    view_func=routes.external.mypc.inventory.inventory_item_offset,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/inventory/item/<uuid:itemuuid>/unequip/<string:type>/<string:slotname>',
    methods=['POST'],
    view_func=routes.external.mypc.inventory.inventory_item_unequip,
    )
#
# Routes: /instance
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/instance',
    methods=['PUT'],
    view_func=routes.external.mypc.instance.add,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>',
    methods=['GET'],
    view_func=routes.external.mypc.instance.get,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>/join',
    methods=['POST'],
    view_func=routes.external.mypc.instance.join,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/instance/<uuid:instanceuuid>/leave',
    methods=['POST'],
    view_func=routes.external.mypc.instance.leave,
    )
#
# Routes: /action/resolver
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/action/resolver/context',
    methods=['POST'],
    view_func=routes.external.mypc.action.resolver.context,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/action/resolver/move',
    methods=['POST'],
    view_func=routes.external.mypc.action.resolver.move,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/action/resolver/skill/<string:skill_name>',
    methods=['PUT'],
    view_func=routes.external.mypc.action.resolver.skill,
    )
#
# Routes: /action
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/action/reload/<uuid:itemuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.action.reload,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/action/unload/<uuid:itemuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.action.unload,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/action/profession/skinning/<uuid:resourceuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.action.profession.skinning,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/action/profession/recycling/<uuid:itemuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.action.profession.recycling,
    )
#
# Routes: /events
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/event',
    methods=['GET'],
    view_func=routes.external.mypc.events.mypc_event_get_all,
    )
#
# Routes /korp
#
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp/<uuid:korpuuid>',
    methods=['GET'],
    view_func=routes.external.mypc.korp.korp_get_one,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp',
    methods=['POST'],
    view_func=routes.external.mypc.korp.korp_create,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp/<uuid:korpuuid>',
    methods=['DELETE'],
    view_func=routes.external.mypc.korp.korp_delete,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp/<uuid:korpuuid>/invite/<uuid:targetuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.korp.korp_invite,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp/<uuid:korpuuid>/kick/<uuid:targetuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.korp.korp_kick,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp/<uuid:korpuuid>/accept',
    methods=['POST'],
    view_func=routes.external.mypc.korp.korp_accept,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp/<uuid:korpuuid>/leave',
    methods=['POST'],
    view_func=routes.external.mypc.korp.korp_leave,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/korp/<uuid:korpuuid>/decline',
    methods=['POST'],
    view_func=routes.external.mypc.korp.korp_decline,
    )

#
# Routes /squad
#

app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>',
    methods=['GET'],
    view_func=routes.external.mypc.squad.squad_get_one,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad',
    methods=['POST'],
    view_func=routes.external.mypc.squad.squad_create,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>',
    methods=['DELETE'],
    view_func=routes.external.mypc.squad.squad_delete,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>/invite/<uuid:targetuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.squad.squad_invite,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>/kick/<uuid:targetuuid>',
    methods=['POST'],
    view_func=routes.external.mypc.squad.squad_kick,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>/accept',
    methods=['POST'],
    view_func=routes.external.mypc.squad.squad_accept,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>/leave',
    methods=['POST'],
    view_func=routes.external.mypc.squad.squad_leave,
    )
app.add_url_rule(
    '/mypc/<uuid:creatureuuid>/squad/<uuid:squaduuid>/decline',
    methods=['POST'],
    view_func=routes.external.mypc.squad.squad_decline,
    )
#
# Routes /map
#
app.add_url_rule(
    '/map/<int:mapid>',
    methods=['GET'],
    view_func=routes.external.map.map_get,
    )
#
# Routes /log
#
app.add_url_rule(
    '/log',
    methods=['POST'],
    view_func=routes.external.log.front,
    )

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
