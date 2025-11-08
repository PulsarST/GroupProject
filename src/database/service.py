from datetime import datetime
from functools import reduce
from typing import AsyncGenerator
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.database import (
    Base,
    Zone,
    Spot,
    Session,
    Payment,
    Tariff,
    SessionStatus,
    SpotStatus,
)

from utils.monads import Maybe

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_relative_path = os.path.join(current_dir, "..", "data", "database.db")
db_absolute_path = os.path.abspath(db_relative_path)

DB_PATH = f"sqlite+aiosqlite:///{db_absolute_path}"
# создаём движок и фабрику сессий
engine = create_async_engine(DB_PATH, echo=True)
SessionDB = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionDB() as session:
        yield session


# --- CRUD --- #


async def get_zones(db: AsyncSession):
    result = await db.execute(select(Zone))
    return result.scalars().all()


async def get_spots(db: AsyncSession, zone_id: str):
    result = await db.execute(select(Spot).where(Spot.zone_id == zone_id))
    return result.scalars().all()


async def get_sessions(db: AsyncSession):
    result = await db.execute(select(Session))
    return result.scalars().all()


async def get_payments(db: AsyncSession):
    result = await db.execute(select(Payment))
    return result.scalars().all()


async def create_session_db(
    db: AsyncSession,
    zone_id: str,
    spot_id: int,
    plate: str,
    tariff_id: int | None = None,
):
    spot = await db.get(Spot, spot_id)
    if not spot or spot.zone_id != zone_id:
        raise ValueError("Invalid zone or spot")

    if spot.status != "available":
        raise ValueError("Spot is occupied")

    session = Session(
        zone_id=zone_id,
        spot_id=spot_id,
        plate=plate,
        tariff_id=tariff_id,
        start_time=datetime.utcnow(),
        status=SessionStatus.active,
    )

    db.add(session)
    spot.status = "occupied"
    await db.commit()
    await db.refresh(session)
    return session


async def close_session_db(db: AsyncSession, session_id: int):
    session = await db.get(Session, session_id)
    if not session or session.status != SessionStatus.active:
        raise ValueError("Active session not found")

    session.status = SessionStatus.completed
    session.end_time = datetime.utcnow()

    spot = await db.get(Spot, session.spot_id)
    spot.status = "available"

    await db.commit()
    await db.refresh(session)
    return session


async def create_payment_db(db: AsyncSession, session_id: int):
    session = await db.get(Session, session_id)
    if not session or session.status != SessionStatus.completed:
        raise ValueError("Completed session not found")

    result = await db.execute(select(Payment).where(Payment.session_id == session_id))
    if result.scalars().first():
        raise ValueError("Payment already exists")

    start = session.start_time
    end = session.end_time or datetime.utcnow()
    hours = (end - start).total_seconds() / 3600
    amount = max(hours * 50, 50)

    payment = Payment(session_id=session_id, amount=round(amount, 2))
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_final_payment_amount(db: AsyncSession) -> int:
    result = await db.execute(select(func.sum(Payment.amount)))
    total = result.scalar() or 0
    return total


async def iter_all_sessions(db: AsyncSession) -> AsyncGenerator[Session, None]:
    """Ленивый генератор всех сессий из базы."""
    result = await db.stream(select(Session))
    async for s in result.scalars():
        yield s


async def iter_active_sessions(db: AsyncSession):
    async for s in iter_all_sessions(db):
        if s.status == SessionStatus.active:
            yield s


async def get_active_sessions(db: AsyncSession):
    result = [s async for s in iter_active_sessions(db)]
    return result


async def get_endtime_sessions(db: AsyncSession) -> list[str]:
    result = await db.execute(select(Session))
    sessions = result.scalars().all()  # <-- получаем объекты Session

    return [
        Maybe(session.end_time).unwrap("Session is not completed")
        for session in sessions
    ]


# --- вспомогательная функция для инициализации БД --- #
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
