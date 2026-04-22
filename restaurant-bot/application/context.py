from dataclasses import dataclass

from application.use_cases import (
    GetMenuUseCase,
    MakeReservationUseCase,
    PlaceOrderUseCase,
)


@dataclass
class AppContext:
    get_menu: GetMenuUseCase
    make_reservation: MakeReservationUseCase
    place_order: PlaceOrderUseCase
