import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional

from schemes import Spot, Tariff, Vehicle, Event, Session, Payment
from enums import SpotStatus, EventType, SessionStatus, VehicleKind, PaymentType, SpotType, TariffKind

# --- Асинхронная шина событий --- #
class AsyncEventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type: EventType, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    async def publish(self, event: Event, state: dict):
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                new_state = await handler(event, state)
                state.update(new_state)
        return state

# --- Состояние системы --- #
state = {
    "spots": {},      # spot_id -> Spot
    "sessions": {},   # session_id -> Session
    "payments": {},   # payment_id -> Payment
    "vehicles": {},   # vehicle_id -> Vehicle
}

# --- Чистые обработчики событий --- #
async def handle_entry(event: Event, state: dict) -> dict:
    vehicle: Vehicle = event.payload["vehicle"]
    spot: Spot = event.payload["spot"]
    tariff: Optional[Tariff] = event.payload.get("tariff")

    # Создаём новую сессию
    session_id = str(uuid.uuid4())
    session = Session(
        id=session_id,
        start=event.ts,
        spot_status=SpotStatus.OCCUPIED,
        spot_id=spot.id,
        tariff_id=tariff.id if tariff else None,
        status=SessionStatus.ACTIVE,
    )

    # Обновляем состояние
    state["sessions"][session_id] = session
    spot.status = SpotStatus.OCCUPIED
    state["spots"][spot.id] = spot
    state["vehicles"][vehicle.id] = vehicle

    print(f"[ENTRY] Vehicle {vehicle.plate} entered spot {spot.id}")
    return state

async def handle_exit(event: Event, state: dict) -> dict:
    session_id: str = event.payload["session_id"]
    session: Session = state["sessions"][session_id]
    session.end = event.ts
    session.status = SessionStatus.CLOSED

    # Освобождаем место
    spot: Spot = state["spots"][session.spot_id]
    spot.status = SpotStatus.AVAILABLE
    state["spots"][spot.id] = spot

    state["sessions"][session_id] = session
    print(f"[EXIT] Session {session_id} ended at {event.ts}")
    return state

async def handle_payment(event: Event, state: dict) -> dict:
    session_id: str = event.payload["session_id"]
    session: Session = state["sessions"][session_id]

    # Рассчитываем оплату
    end_time = session.end or datetime.utcnow()
    duration_hours = (end_time - session.start).total_seconds() / 3600
    amount = max(int(duration_hours * 50), 50)  # пример расчёта

    payment_id = str(uuid.uuid4())
    payment = Payment(
        id=payment_id,
        session_id=session_id,
        amount=amount,
        ts=event.ts,
        method=PaymentType.CARD,
    )

    state["payments"][payment_id] = payment
    print(f"[PAYMENT] Payment {payment_id} for session {session_id}, amount={amount}")
    return state





# --- Симуляция событий --- #
async def simulate_events(bus: AsyncEventBus):
    # Создаём несколько машин и мест
    vehicle1 = Vehicle(id="v1", plate="ABC123", kind=VehicleKind.CAR)
    vehicle2 = Vehicle(id="v2", plate="XYZ789", kind=VehicleKind.TRUCK)

    spot1 = Spot(id="s1", status=SpotStatus.AVAILABLE, type=SpotType.STANDARD)
    spot2 = Spot(id="s2", status=SpotStatus.AVAILABLE, type=SpotType.STANDARD)

    tariff1 = Tariff(id="t1", base=50, per_hour=50, free_minutes=0, kind=TariffKind.STANDARD)

    state["spots"][spot1.id] = spot1
    state["spots"][spot2.id] = spot2

    # --- ENTRY события ---
    e1 = Event(id=str(uuid.uuid4()), type=EventType.ENTRY, ts=datetime.utcnow(),
               payload={"vehicle": vehicle1, "spot": spot1, "tariff": tariff1})
    await bus.publish(e1, state)
    await asyncio.sleep(0.5)

    e2 = Event(id=str(uuid.uuid4()), type=EventType.ENTRY, ts=datetime.utcnow() + timedelta(seconds=1),
               payload={"vehicle": vehicle2, "spot": spot2, "tariff": tariff1})
    await bus.publish(e2, state)
    await asyncio.sleep(0.5)

    # Берём ID первой сессии для EXIT и PAYMENT
    session_id1 = list(state["sessions"].keys())[0]

    # --- EXIT событие ---
    e3 = Event(id=str(uuid.uuid4()), type=EventType.EXIT, ts=datetime.utcnow() + timedelta(seconds=5),
               payload={"session_id": session_id1})
    await bus.publish(e3, state)
    await asyncio.sleep(0.5)

    # --- PAYMENT событие ---
    e4 = Event(id=str(uuid.uuid4()), type=EventType.PAY, ts=datetime.utcnow() + timedelta(seconds=6),
               payload={"session_id": session_id1})
    await bus.publish(e4, state)

# --- Основная функция --- #
async def main():
    bus = AsyncEventBus()
    bus.subscribe(EventType.ENTRY, handle_entry)
    bus.subscribe(EventType.EXIT, handle_exit)
    bus.subscribe(EventType.PAY, handle_payment)

    await simulate_events(bus)

if __name__ == "__main__":
    asyncio.run(main())
