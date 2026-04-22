from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItem:
    id: int
    name: str
    price: int
    category: str
    description: str


@dataclass
class Reservation:
    id: int
    name: str
    date: str
    time: str
    party_size: int


@dataclass
class OrderLine:
    menu_item_id: int
    menu_item_name: str
    quantity: int
    price: int


@dataclass
class Order:
    id: int
    lines: list[OrderLine]
    total_price: int
