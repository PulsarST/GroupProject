# session_generator.py
import asyncio
import random
from datetime import datetime, timedelta
import os
import sys

# database.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()


class SpotStatus(str, enum.Enum):
    available = "available"
    occupied = "occupied"


class SessionStatus(str, enum.Enum):
    active = "active"
    completed = "completed"


class Zone(Base):
    __tablename__ = "zones"
    id = Column(String, primary_key=True)
    name = Column(String)
    spots = relationship("Spot", back_populates="zone")


class Spot(Base):
    __tablename__ = "spots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    type = Column(String)  # standard, accessible, truck, etc.
    status = Column(Enum(SpotStatus), default=SpotStatus.available)
    zone = relationship("Zone", back_populates="spots")


class Tariff(Base):
    __tablename__ = "tariffs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    rate = Column(Float)


class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    spot_id = Column(Integer, ForeignKey("spots.id"))
    plate = Column(String)
    tariff_id = Column(Integer, ForeignKey("tariffs.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.active)

    zone = relationship("Zone")
    spot = relationship("Spot")
    tariff = relationship("Tariff")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    amount = Column(Float)
    ts = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session")


from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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


# session_generator.py
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import text
import os
import sys

# Добавляем путь для импортов
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


async def generate_sessions():
    """Генерирует сессии для 50% случайных спотов"""

    # Список тестовых автомобильных номеров
    test_plates = [
        "А123ВС777", "Е001КХ750", "О777ОО177", "У333НН777",
        "Т123ТТ777", "Х987ХХ777", "С555СС777", "М111ММ777",
        "Р222РР777", "В444ВВ777", "А555АА777", "Е666ЕЕ777",
        "О888ОО777", "У999УУ777", "Т000ТТ777", "К111КК777"
    ]

    async for db in get_db():
        try:
            # Получаем все доступные споты
            result = await db.execute(text("SELECT * FROM spots WHERE status = 'available'"))
            available_spots = result.fetchall()

            print(f"Всего доступных спотов: {len(available_spots)}")

            # Выбираем случайные 50% спотов
            spots_to_occupy_count = max(1, len(available_spots) // 2)
            spots_to_occupy = random.sample(available_spots, spots_to_occupy_count)

            print(f"Будем занимать {len(spots_to_occupy)} спотов")

            created_sessions = 0

            for spot_row in spots_to_occupy:
                try:
                    # Получаем объект Spot из строки
                    spot = Spot(
                        id=spot_row.id,
                        zone_id=spot_row.zone_id,
                        type=spot_row.type,
                        status=spot_row.status
                    )

                    # Случайный автомобильный номер
                    plate = random.choice(test_plates)

                    # Создаем сессию через сервис
                    session_data = {
                        "zone_id": spot.zone_id,
                        "spot_id": spot.id,
                        "plate": plate,
                        "tariff_id": 1  # Используем первый тариф
                    }

                    session = await create_session_db(db, **session_data)

                    created_sessions += 1
                    print(f"✅ Создана сессия для спота {spot.id} (Зона {spot.zone_id}), автомобиль: {plate}")

                except Exception as e:
                    print(f"❌ Ошибка при создании сессии для спота {spot_row.id}: {e}")
                    continue

            print(f"\n🎉 Успешно создано {created_sessions} сессий")
            print(f"📊 Статистика:")
            print(f"   - Всего спотов: {len(available_spots)}")
            print(f"   - Занято спотов: {created_sessions}")
            print(f"   - Свободных спотов: {len(available_spots) - created_sessions}")

        except Exception as e:
            print(f"❌ Общая ошибка: {e}")


async def check_spots_status():
    """Проверяет статус спотов после генерации"""
    async for db in get_db():
        result = await db.execute(text("""
            SELECT 
                zone_id,
                status,
                COUNT(*) as count
            FROM spots 
            GROUP BY zone_id, status
            ORDER BY zone_id, status
        """))
        stats = result.fetchall()

        print("\n📊 Статус спотов по зонам:")
        for stat in stats:
            print(f"   Зона {stat.zone_id}: {stat.status} - {stat.count} спотов")


async def check_sessions():
    """Показывает созданные сессии"""
    async for db in get_db():
        result = await db.execute(text("""
            SELECT 
                s.id as session_id,
                s.zone_id,
                s.spot_id,
                s.plate,
                s.start_time,
                sp.type as spot_type
            FROM sessions s
            JOIN spots sp ON s.spot_id = sp.id
            ORDER BY s.zone_id, s.spot_id
        """))
        sessions = result.fetchall()

        print(f"\n📋 Созданные сессии ({len(sessions)}):")
        for session in sessions:
            print(
                f"   Сессия {session.session_id}: зона {session.zone_id}, спот {session.spot_id} ({session.spot_type}), авто: {session.plate}")


async def update_sessions_start_time():
    """Обновляет время начала у существующих сессий на случайное"""

    async for db in get_db():
        try:
            # Получаем все активные сессии
            result = await db.execute(text("SELECT * FROM sessions WHERE status = 'active'"))
            sessions = result.fetchall()

            print(f"Найдено {len(sessions)} активных сессий для обновления времени")

            updated_count = 0
            for session_row in sessions:
                try:
                    # Случайное время начала (от 1 часа до 7 дней назад)
                    hours_ago = random.randint(1, 168)  # 1 час - 7 дней
                    start_time = datetime.utcnow() - timedelta(hours=hours_ago)

                    # Обновляем время начала
                    await db.execute(
                        text("UPDATE sessions SET start_time = :start_time WHERE id = :id"),
                        {"start_time": start_time, "id": session_row.id}
                    )
                    updated_count += 1

                    print(f"✅ Обновлено время сессии {session_row.id}: {start_time}")

                except Exception as e:
                    print(f"❌ Ошибка при обновлении сессии {session_row.id}: {e}")
                    continue

            await db.commit()
            print(f"🎉 Обновлено {updated_count} сессий")

        except Exception as e:
            print(f"❌ Общая ошибка: {e}")
            await db.rollback()


if __name__ == "__main__":
    print("🚗 Генератор сессий для парковки")
    print("=" * 50)

    # Основная генерация сессий
    asyncio.run(generate_sessions())

    # Проверка статуса
    asyncio.run(check_spots_status())

    # Показать созданные сессии
    asyncio.run(check_sessions())

    # Опционально: обновить время начала
    answer = input("\n🕐 Хотите обновить время начала сессий на случайное? (y/n): ")
    if answer.lower() == 'y':
        asyncio.run(update_sessions_start_time())
        asyncio.run(check_sessions())