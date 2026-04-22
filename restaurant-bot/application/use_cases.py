from dataclasses import dataclass

from domain.entities import (
    MenuItem,
    Order,
    OrderLine,
    Reservation,
)
from domain.repositories import (
    MenuRepository,
    OrderRepository,
    ReservationRepository,
)


@dataclass
class GetMenuUseCase:
    repo: MenuRepository

    def execute(self, category: str | None = None) -> list[MenuItem]:
        if category:
            return self.repo.find_by_category(category)
        return self.repo.list_all()


@dataclass
class MakeReservationUseCase:
    repo: ReservationRepository

    def execute(self, name: str, date: str, time: str, party_size: int) -> Reservation:
        return self.repo.save(name, date, time, party_size)


@dataclass
class PlaceOrderUseCase:
    menu_repo: MenuRepository
    order_repo: OrderRepository

    def execute(self, items: list[tuple[int, int]]) -> Order:
        lines: list[OrderLine] = []
        total = 0
        for menu_id, quantity in items:
            item = self.menu_repo.find_by_id(menu_id)
            if item is None:
                raise ValueError(f"메뉴 ID {menu_id}를 찾을 수 없습니다")
            line_price = item.price * quantity
            lines.append(OrderLine(item.id, item.name, quantity, line_price))
            total += line_price
        order = Order(id=len(lines), lines=lines, total_price=total)
        return self.order_repo.save(order)
