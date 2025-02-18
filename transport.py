import httpx

import stamina
import structlog
from httpx import AsyncClient

from exceptions import NotFoundError


@stamina.retry(on=httpx.HTTPError, attempts=3)
async def get_page(client: AsyncClient, page: int = 1) -> str:
    log = structlog.get_logger()

    resp = await client.get(f"https://books.toscrape.com/catalogue/page-{page}.html")
    log.debug("HTTP GET request called", url=resp.url, status_code=resp.status_code)
    if resp.status_code == httpx.codes.NOT_FOUND:
        raise NotFoundError("The server have responded with 404 error")

    resp.raise_for_status()

    return resp.text
