from itertools import count

from domain.entities import (
    MenuItem,
    Order,
    Reservation,
)
from domain.repositories import (
    MenuRepository,
    OrderRepository,
    ReservationRepository,
)


_MENU: list[MenuItem] = [
    MenuItem(1, "트러플 파스타", 28000, "main", "블랙 트러플 오일과 버섯 크림 파스타"),
    MenuItem(2, "마르게리타 피자", 22000, "main", "토마토 소스와 모짜렐라, 바질의 클래식 피자"),
    MenuItem(3, "스테이크", 45000, "main", "200g 채끝 등심 스테이크, 감자 퓨레 곁들임"),
    MenuItem(4, "시저 샐러드", 15000, "side", "로메인, 파마산, 앤초비 드레싱"),
    MenuItem(5, "감바스", 18000, "side", "매콤한 올리브유 새우 요리"),
    MenuItem(6, "티라미수", 9000, "dessert", "마스카포네 치즈와 에스프레소의 클래식 디저트"),
    MenuItem(7, "크렘 브륄레", 10000, "dessert", "바닐라빈 커스터드와 캐러멜 토핑"),
    MenuItem(8, "하우스 와인", 12000, "beverage", "레드/화이트 선택 가능"),
]


class InMemoryMenuRepository(MenuRepository):
    def list_all(self) -> list[MenuItem]:
        return list(_MENU)

    def find_by_id(self, menu_id: int) -> MenuItem | None:
        return next((m for m in _MENU if m.id == menu_id), None)

    def find_by_category(self, category: str) -> list[MenuItem]:
        return [m for m in _MENU if m.category == category]


class InMemoryReservationRepository(ReservationRepository):
    def __init__(self):
        self._data: list[Reservation] = []
        self._id = count(1)

    def save(self, name: str, date: str, time: str, party_size: int) -> Reservation:
        reservation = Reservation(
            id=next(self._id),
            name=name,
            date=date,
            time=time,
            party_size=party_size,
        )
        self._data.append(reservation)
        return reservation

    def list_all(self) -> list[Reservation]:
        return list(self._data)


class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._data: list[Order] = []

    def save(self, order: Order) -> Order:
        self._data.append(order)
        return order
