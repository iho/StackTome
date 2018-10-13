import asyncio
import re
from datetime import datetime
from itertools import chain
from time import mktime

import aiohttp
import async_timeout
import feedparser
from lxml import etree

import config


async def get_google_trends(session):
    feed = feedparser.parse(await fetch(session, config.google_trends_url))
    root = etree.fromstring(feed.entries[0].content[0].value)
    return root.xpath("//a/text()")


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()


def clean_string(string):
    return re.sub("[^ A-Za-z0-9]+", "", string.lower())


def contains_trend(title, trends):
    for trend in trends:
        if clean_string(trend) in clean_string(title):
            return trend
    return False


async def get_news_entries(session, url):
    return feedparser.parse(await fetch(session, url))["entries"]


async def update_news(app):
    print("Feching data...")
    news_list = []
    async with aiohttp.ClientSession() as session:
        trends = await get_google_trends(session)
        for news_entry in chain.from_iterable(
            await asyncio.gather(
                *[get_news_entries(session, url) for url in config.rss_urls]
            )
        ):

            title = news_entry["title"]
            summary = news_entry.get("summary")
            if title:
                trend = contains_trend(title, trends)
                if not trend and summary:
                    trend = contains_trend(summary, trends)

            if trend:

                date = news_entry.get("published_parsed")
                if date:
                    date = datetime.fromtimestamp(mktime(date))

                new_news_entry = {
                    "title": title,
                    "link": news_entry["link"],
                    "date": date,
                    "trend": trend,
                    "image_url": None,
                }
                media_content = news_entry.get("media_content")
                if media_content:
                    new_news_entry["image_url"] = media_content[0]["url"]
                news_list.append(new_news_entry)
    app["news"].clear()
    app["news"].extend(news_list)


async def run_in_background(async_func, params):
    while True:
        await asyncio.sleep(config.INTERVAL)
        await async_func(*params)


async def init_func(app):
    await update_news(app)
    asyncio.ensure_future(run_in_background(update_news, [app]))
