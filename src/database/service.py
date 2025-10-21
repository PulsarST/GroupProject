from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.database import Base, Zone, Spot, Session, Payment, Tariff, SessionStatus

# путь к БД
DB_PATH = "sqlite+aiosqlite:////home/artz/PycharmProjects/PythonProject1/GroupProject/src/data/database.db"

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


async def create_session_db(db: AsyncSession, zone_id: str, spot_id: int, plate: str, tariff_id: int | None = None):
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
        status=SessionStatus.active
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


# --- вспомогательная функция для инициализации БД --- #
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
