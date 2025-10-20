from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from core.enums import SessionStatus, TariffKind
from core.schemes import Tariff
from database.database import Base, Session, Spot

engine = create_async_engine(
    "sqlite:///.../data/database.db",
    echo=True
)

SessionDB = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with SessionDB() as session:
        yield session


async def create_session(
    db: AsyncSession,
    start: datetime,
    end: datetime,
    tariff_kind: TariffKind
) -> Session:
    tariff = Tariff(
        base=2000,
        kind=tariff_kind,
        per_hour=200,
        free_minutes=15
    )

    db.add(tariff)
    await db.flush()

    session = Session(
        start = start,
        end = end,
        tarriff_id = tariff.id
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def close_session(db: AsyncSession, id: int):
    session = await db.get(Session, id)
    if not session:
        raise ValueError("session not found")

    if session.status == SessionStatus.CLOSED:
        raise ValueError("session is already close")

    session.status = SessionStatus.CLOSED
    await db.commit()


async def get_active_sessions(db: AsyncSession) -> list[Session]:
    stmt = select(Session).where(Session.status == SessionStatus.ACTIVE)
    result = await db.execute(stmt)
    return list(result.scalars().all())

