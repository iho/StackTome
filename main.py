import aiohttp_jinja2
import jinja2
from aiohttp import web

import utils
import views


def init():
    app = web.Application()
    app["news"] = []
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader("./templates"))
    app.router.add_get("/", views.index)
    app.on_startup.append(utils.init_func)
    return app


web.run_app(init())
