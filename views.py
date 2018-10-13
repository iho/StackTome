import aiohttp_jinja2


@aiohttp_jinja2.template("index.jinja2")
async def index(request):
    return {"news": request.app["news"]}
