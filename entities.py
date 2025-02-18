from dataclasses import dataclass


@dataclass
class Book:
    title: str
    available: bool
    price: str
