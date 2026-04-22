from abc import ABC, abstractmethod

from domain.entities import MenuItem, Order, Reservation


class MenuRepository(ABC):
    @abstractmethod
    def list_all(self) -> list[MenuItem]: ...

    @abstractmethod
    def find_by_id(self, menu_id: int) -> MenuItem | None: ...

    @abstractmethod
    def find_by_category(self, category: str) -> list[MenuItem]: ...


class ReservationRepository(ABC):
    @abstractmethod
    def save(self, name: str, date: str, time: str, party_size: int) -> Reservation: ...

    @abstractmethod
    def list_all(self) -> list[Reservation]: ...


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> Order: ...
