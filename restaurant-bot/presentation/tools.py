from agents import RunContextWrapper, function_tool
from pydantic import BaseModel

from application.context import AppContext


class OrderItem(BaseModel):
    menu_id: int
    quantity: int


@function_tool
async def get_menu(
    ctx: RunContextWrapper[AppContext],
    category: str | None = None,
) -> str:
    """레스토랑의 메뉴를 조회합니다.

    Args:
        category: 필터할 카테고리 (main, side, dessert, beverage). 생략 시 전체 메뉴.
    """
    items = ctx.context.get_menu.execute(category)
    if not items:
        return "해당 카테고리의 메뉴가 없습니다."
    lines = [f"- [{m.id}] {m.name} ({m.category}, ₩{m.price:,}): {m.description}" for m in items]
    return "\n".join(lines)


@function_tool
async def make_reservation(
    ctx: RunContextWrapper[AppContext],
    name: str,
    date: str,
    time: str,
    party_size: int,
) -> str:
    """예약을 생성합니다.

    Args:
        name: 예약자 이름
        date: 예약 날짜 (YYYY-MM-DD)
        time: 예약 시간 (HH:MM)
        party_size: 인원 수
    """
    reservation = ctx.context.make_reservation.execute(name, date, time, party_size)
    return (
        f"예약 완료! (번호: {reservation.id})\n"
        f"- 예약자: {reservation.name}\n"
        f"- 일시: {reservation.date} {reservation.time}\n"
        f"- 인원: {reservation.party_size}명"
    )


@function_tool
async def place_order(
    ctx: RunContextWrapper[AppContext],
    items: list[OrderItem],
) -> str:
    """주문을 생성합니다.

    Args:
        items: 주문 항목 리스트. 각 항목은 menu_id와 quantity를 포함합니다.
    """
    parsed = [(item.menu_id, item.quantity) for item in items]
    order = ctx.context.place_order.execute(parsed)
    lines = [f"- {line.menu_item_name} x{line.quantity}: ₩{line.price:,}" for line in order.lines]
    return "주문 완료!\n" + "\n".join(lines) + f"\n합계: ₩{order.total_price:,}"


