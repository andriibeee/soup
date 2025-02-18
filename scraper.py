import re
from typing import List

import structlog
from bs4 import PageElement, Tag, NavigableString, BeautifulSoup

from entities import Book
from exceptions import (
    InvalidPriceError,
    FuckedUpMarkupError,
    InvalidPagerTextError,
    InvalidAvailabilityClassError,
    MissingPriceError,
    MissingAvailabilityError,
    MissingTitleError,
    MissingCriticalElementError,
)


def parse_book(book_container: Tag | NavigableString) -> Book:
    title = book_container.select_one("h3 a")
    if not title:
        raise MissingTitleError(
            "Missing 'h3 a' element for title in the provided document"
        )

    title_str = title.get("title")
    if not title_str:
        raise MissingTitleError(
            "Missing 'title' attribute in 'h3 a' element for book title"
        )

    try:
        available = gauge_availability(book_container)
    except FuckedUpMarkupError as e:
        raise MissingAvailabilityError(
            f"Error determining availability for book: {title_str}. Details: {str(e)}"
        )

    price = book_container.select_one(".price_color")
    if not price:
        raise MissingPriceError(
            "Missing '.price_color' element for price in the provided document"
        )

    price_text = price.text.strip()
    if not price_text:
        raise InvalidPriceError(
            "Empty or invalid price text found in '.price_color' element"
        )

    return Book(title=title_str.strip(), price=price_text, available=available)


def gauge_availability(book_container: PageElement | Tag | NavigableString):
    avail = book_container.select_one("p.availability")
    if not avail:
        raise FuckedUpMarkupError(
            "Missing the root .availability element in the provided document"
        )
    states = {
        "instock": True,
        "outofstock": False,
    }
    has_class = [clazz in states for clazz in avail.get("class")]
    if not any(has_class):
        raise InvalidAvailabilityClassError(
            f"Unexpected availability class in element: {avail.get('class', [])}. Expected 'instock' or 'outofstock'"
        )
    for clazz in avail.get("class"):
        if clazz in states:
            return states.get(clazz)
    return False


def parse_pages_count(src: str) -> int:
    txt = src.strip()
    if not txt:
        raise InvalidPagerTextError("Empty string provided")
    m = re.match(r"^Page\s+[0-9,]+\s+of\s+([0-9,]+)\s*\+?$", txt)
    if not m:
        raise InvalidPagerTextError(f"Could not extract pages count from string: {txt}")
    return int(m.group(1))


async def parse_page(layout: str | Tag | NavigableString) -> List[Book]:
    log = structlog.get_logger()
    soup = layout is str and BeautifulSoup(layout, "html.parser") or layout
    prod = soup.find_all("article", class_="product_pod")
    out = []
    for p in prod:
        try:
            out.append(parse_book(p))
        except (
            MissingTitleError,
            MissingAvailabilityError,
            MissingAvailabilityError,
            MissingPriceError,
        ) as e:
            log.error(e)
        except MissingCriticalElementError as e:
            log.critical(e)
    return out
