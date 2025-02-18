import asyncio

import httpx
import structlog
from bs4 import BeautifulSoup
from httpx import AsyncClient

from motor.motor_asyncio import AsyncIOMotorClient

from beanie import init_beanie

from config import MONGODB_URI
from exceptions import MissingCriticalElementError
from mongo import BookModel, insert_books
from scraper import parse_pages_count, parse_page
from transport import get_page


async def scrape_page(client: AsyncClient, page: int):
    log = structlog.get_logger()
    log.info("Scraping page", page=page)
    txt = await get_page(client, page + 1)
    soup = BeautifulSoup(txt, "html.parser")
    return await insert_books(await parse_page(soup))


async def main():
    log = structlog.get_logger()
    log.info("Connecting to database")
    client = AsyncIOMotorClient(MONGODB_URI)
    await init_beanie(database=client.db_name, document_models=[BookModel])
    log.info("Starting the parsing process")

    async with httpx.AsyncClient() as client:
        soup = BeautifulSoup(await get_page(client, 1), "html.parser")
        await insert_books(await parse_page(soup))

        try:
            cur = soup.select_one(".pager li.current")
            if not cur:
                raise MissingCriticalElementError("can't find li.current")
            cunt = parse_pages_count(cur.text.strip())
            tasks = [
                scrape_page(client, page) for page in range(1, cunt)
            ]
            await asyncio.gather(*tasks)
        except MissingCriticalElementError as e:
            log.critical(e)


if __name__ == "__main__":
    asyncio.run(main())
