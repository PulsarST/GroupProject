# fill_database.py
import json
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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


DB_URL = "sqlite:////src/data/database.db"
DATA_FILE = "src/data/seed.json"


def fill_database():
    # Загружаем данные из JSON
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Создаем движок и сессию
    engine = create_engine(DB_URL, echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Заполняем зоны
    for zone_data in data["zones"]:
        zone = Zone(
            id=zone_data["id"],
            name=zone_data["name"]
        )
        db.add(zone)

    # Заполняем места (spots) - преобразуем string id в integer
    spot_id_mapping = {}  # Для маппинга старых ID в новые
    spot_counter = 1

    for spot_data in data["spots"]:
        # Преобразуем статус
        status = SpotStatus.available if spot_data["status"] == "available" else SpotStatus.occupied

        # Преобразуем тип (kind) в type
        spot_type = spot_data["kind"]

        spot = Spot(
            id=spot_counter,
            zone_id=spot_data["zone_id"],
            type=spot_type,
            status=status
        )
        db.add(spot)

        # Сохраняем маппинг старых ID на новые
        spot_id_mapping[spot_data["id"]] = spot_counter
        spot_counter += 1

    # Заполняем тарифы - преобразуем string id в integer
    tariff_id_mapping = {}  # Для маппинга старых ID в новые
    tariff_counter = 1

    for tariff_data in data["tariffs"]:
        tariff = Tariff(
            id=tariff_counter,
            name=f"{tariff_data['kind']} - {tariff_data['zone_id'] or 'general'}",
            rate=tariff_data["per_hour"] or 50.0  # Используем per_hour как rate
        )
        db.add(tariff)

        # Сохраняем маппинг
        tariff_id_mapping[tariff_data["id"]] = tariff_counter
        tariff_counter += 1

    # Заполняем сессии - преобразуем данные
    session_id_mapping = {}  # Для маппинга старых ID в новые
    session_counter = 1

    for session_data in data["sessions"]:
        # Преобразуем статус
        status = SessionStatus.completed if session_data["status"] == "closed" else SessionStatus.active

        # Преобразуем даты
        start_time = datetime.fromisoformat(session_data["start"].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(session_data["end"].replace('Z', '+00:00')) if session_data["end"] else None

        # Получаем vehicle данные для plate
        vehicle_id = session_data["vehicle_id"]
        vehicle = next((v for v in data["vehicles"] if v["id"] == vehicle_id), None)
        plate = vehicle["plate"] if vehicle else "UNKNOWN"

        # Получаем новый spot_id
        old_spot_id = session_data["spot_id"]
        new_spot_id = spot_id_mapping.get(old_spot_id, 1)

        # Получаем zone_id из spot
        spot = next((s for s in data["spots"] if s["id"] == old_spot_id), None)
        zone_id = spot["zone_id"] if spot else "A"

        session = Session(
            id=session_counter,
            zone_id=zone_id,
            spot_id=new_spot_id,
            plate=plate,
            tariff_id=1,  # Используем первый тариф по умолчанию
            start_time=start_time,
            end_time=end_time,
            status=status
        )
        db.add(session)

        # Сохраняем маппинг
        session_id_mapping[session_data["id"]] = session_counter
        session_counter += 1

    # Заполняем платежи
    payment_counter = 1

    for payment_data in data["payments"]:
        # Преобразуем дату
        ts = datetime.fromisoformat(payment_data["ts"].replace('Z', '+00:00'))

        # Получаем новый session_id
        old_session_id = payment_data["session_id"]
        new_session_id = session_id_mapping.get(old_session_id, 1)

        payment = Payment(
            id=payment_counter,
            session_id=new_session_id,
            amount=payment_data["amount"],
            ts=ts
        )
        db.add(payment)
        payment_counter += 1

    # Коммитим все изменения
    db.commit()
    db.close()

    print("✅ База успешно заполнена!")
    print(f"Добавлено:")
    print(f"- Зон: {len(data['zones'])}")
    print(f"- Мест: {len(data['spots'])}")
    print(f"- Тарифов: {len(data['tariffs'])}")
    print(f"- Сессий: {len(data['sessions'])}")
    print(f"- Платежей: {len(data['payments'])}")


if __name__ == "__main__":
    fill_database()