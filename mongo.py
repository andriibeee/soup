from datetime import datetime
from typing import Annotated, List

import structlog
from beanie import Document, Indexed

from entities import Book


class BookModel(Document):
    title: Annotated[str, Indexed()]
    price: str
    in_stock: bool
    parse_date: Annotated[datetime, Indexed()]

    class Config:
        collection = "books"


def book_to_model(book: Book, date: datetime) -> BookModel:
    return BookModel(
        title=book.title,
        price=book.price,
        in_stock=book.available,
        parse_date=date,
    )


async def insert_books(books: List[Book]):
    log = structlog.get_logger()

    date = datetime.now()
    entities = [book_to_model(b, date) for b in books]
    await BookModel.insert_many(entities, ordered=False)

    log.info(f"Inserted {len(entities)} books")
