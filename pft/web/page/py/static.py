from flask import redirect, make_response, request
from web.devtool import Page, render_template, CODE_ERRORE
import jinja2

route_base = Page.Route("/")
@route_base.get()
def base_get():
    return redirect("/view")

env_css = jinja2.Environment(loader=jinja2.FileSystemLoader("web/page/css"))
env_js = jinja2.Environment(loader=jinja2.FileSystemLoader("web/page/js"))
env_broken = jinja2.Environment(loader=jinja2.FileSystemLoader("web/page/html"))

route_css = Page.Route("/css/<path:path>")
route_js = Page.Route("/js/<path:path>")

route_broken = Page.Route("/error")

@route_css.get()
def css_get(path):
    r = make_response(render_template(env_css, path))
    r.headers["Content-Type"] = "text/css; charset=utf-8"
    return r

@route_js.get()
def js_get(path):
    r = make_response(render_template(env_js, path))
    r.headers["Content-Type"] = "application/javascript; charset=utf-8"
    return r

@route_broken.get()
def broken_get():
    code = request.args.get("code")
    message = CODE_ERRORE.get(code, CODE_ERRORE.get(None))
    r = make_response(render_template(env_broken, "broken.html", message=message))
    r.headers["Content-Type"] = "text/html; charset=utf-8"
    return r