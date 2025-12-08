from flask import request, Flask, abort
from .Log import Log
from .Error_Message import BAD_REQUEST
from werkzeug.exceptions import HTTPException
from jinja2 import Environment
from flask_sock import Sock
import traceback

def render_template(env: Environment, template, **contexts):
    temp = env.get_template(template)
    return temp.render(**contexts)

class WS_Rule:
    def __init__(self, url, subdomain, func):
        self.url = url
        self.subdomain = subdomain
        self.func = func

class Page:
    socket = None

    class Route:
        def __init__(self, route: str, **options) -> None:
            self.commands = {}
            self.full_route = False
            self._get = lambda client, **options: ""
            self.f_route = route
            self.options = {"methods":["GET", "POST"], "endpoint":self.f_route}
            self.options.update(options)
            self.subdomain = self.options.get("subdomain")
            self.host = self.options.get("host")
            Page.routes.append(self)
            
        def compile_page(self, app: Flask, subdomain=None, host=None):
            if "subdomain" not in self.options.keys():
                if self.subdomain is not None:
                    self.options["subdomain"] = self.subdomain
                elif subdomain is not None:
                    self.subdomain = subdomain
                    self.options["subdomain"] = subdomain

                if self.host is not None:
                    self.options["host"] = self.host
                elif host is not None:
                    self.host = host
                    self.options["host"] = host

            endpoint = self.options.pop("endpoint", None)
            app.add_url_rule(rule=self.f_route, endpoint=endpoint, view_func=self.work, **self.options)

        def work(self, **options):
            print(request)
            try:
                if request.method == "GET" or self.full_route:
                    if self._get:
                        return self._get(**options)
                    else:
                        Log.print(f'"GET REQUEST ON {request.url} but GET in Null" not response -', style=Log.YELLOW)
                elif request.method == "POST":
                    if request.content_type == "application/json":
                        data = request.get_json()
                        if data.get("type"):
                            if self.commands.get(request.method):
                                func = self.commands.get(request.method).get(data["type"])
                                func_data = data.get("data")
                                if func and func_data is not None:
                                    if func.get("func"):
                                        return func.get("func")(func_data)
                                    else:
                                        Log.print(f'"POST REQUEST ON {request.url} but POST in Null" not response -', style=Log.YELLOW)
                                        return {"status":"command function not found"}
                                else:
                                    return {"status":"command not found"}
                            else:
                                return {"status":"bad request methode"}
                        else:
                            return BAD_REQUEST
                    else:
                        abort(403)
                else:
                    abort(404)
            except HTTPException as e:
                Log.print(f"{traceback.format_exc()}")
                raise e
            except Exception as e:
                Log.print(f"{traceback.format_exc()}")
                raise e
                abort(500)

        def get(self):
            def apply(func):
                self._get = func
                return func
            return apply       
        
        def command(self, method: str= "POST"):
            """
            Decorator to add a route, syntaxe is :
            @command:
            def command_name(client: Client \ None, data: dict)
            """
            def apply(func):
                if isinstance(method, str):
                    if not self.commands.get(method):
                        self.commands.update({method:{}})                        
                    self.commands.get(method).update({func.__name__:{"func":func}})
                        
                return func
            return apply
        
        def route(self):
            def apply(func):
                self.full_route = True
                self._get = func
                return func
            return apply     
        
        def __str__(self) -> str:
            return self.f_route
    
    routes: list[Route] = []
    websockets = []

    def websocket(url, subdomain):
        def apply(func):
            Page.websockets.append(WS_Rule(url, subdomain, func)) 
        return apply
    
    def compile_page(app: Flask, subdomain=None, host=None):
        Page.socket = Sock(app)
        
        Log.print("Compiling WebSocket : ")
        for ws_rule in Page.websockets:

            try:
                @Page.socket.route(ws_rule.url)
                def ws_work(ws):
                    ws_rule.func(ws)

                Log.print(f"═╦ Setting WebSocket '{ws_rule.subdomain}.{app.name}{ws_rule.url}' : {Log.color('done', color=Log.GREEN)}")
            except Exception as e:
                Log.print(f"═╦ Setting WebSocket '{ws_rule.subdomain}.{app.name}{ws_rule.url}' : {Log.color('fail', color=Log.RED)} {e}")
                
        Log.print("Compiling Pages & Routes : ")
        for route in Page.routes:
            try:
                route.compile_page(app, subdomain, host)
                Log.print(f"═╦ Setting route '{app.name}{route}' : {Log.color('done', color=Log.GREEN)}")
                for i, c in enumerate([route.commands.get(key, []) for key in route.commands.keys()]):
                    Log.print(f" {'╚═╣' if i==0 else '  ║'} Founded command '{c}'")
            except Exception as e:
                Log.print(f"═╦ Setting route '{app.name}{route}' : {Log.color('fail', color=Log.RED)} {e} {route.options}")