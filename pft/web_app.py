from flask import request, abort
from werkzeug.routing import MapAdapter
from web.devtool.Log import Log
import web.app as frontend_app
import Config

###################################################################################################
# CONFIGURATION
###################################################################################################

frontend_app.app.config['SESSION_COOKIE_SECURE'] = True
frontend_app.app.config['SESSION_COOKIE_HTTPONLY'] = True
frontend_app.app.config['REMEMBER_COOKIE_SECURE'] = True
frontend_app.app.config['REMEMBER_COOKIE_HTTPONLY'] = True
frontend_app.app.config['SERVER_NAME'] = f"{Config.Frontend.servername}"
frontend_app.app.name = frontend_app.app.config['SERVER_NAME']
frontend_app.app.config['SESSION_COOKIE_SAMESITE'] = 'None'
frontend_app.app.config['SESSION_COOKIE_DOMAIN'] = f'.{Config.Frontend.servername}'
frontend_app.app.config['WTF_CSRF_SSL_STRICT'] = False

###################################################################################################
# HANDLER
###################################################################################################

methods = ["GET", "POST", "HEAD", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]
@frontend_app.app.route("/", defaults={'path': ''}, subdomain="", methods=methods)
@frontend_app.app.route("/<path:path>", subdomain="", methods=methods)
def handler(path): 
    host = request.host.split(".")
    
    if len(host)<=2:
        subdomain = ""
    else:
        subdomain = "".join(host[:-2])
    
    adapter: MapAdapter = frontend_app.app.url_map.bind(Config.Frontend.servername, "/", subdomain=subdomain)
    
    endpoint, values = adapter.match(f"/{path}")
    
    try:
        return frontend_app.app.view_functions[endpoint](**values)
    except Exception :
        abort(404)

###################################################################################################
# COMPILATION
###################################################################################################

frontend_app.Page.compile_page(frontend_app.app, Config.Frontend.subdomain, Config.Frontend.servername)

###################################################################################################
# SERVER START
###################################################################################################

frontend_app.app.run(debug=True, host=Config.Frontend.ip, port=Config.Frontend.port)