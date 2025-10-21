import json
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# ---------- Настройка ----------
DB_URL = "sqlite:////home/artz/PycharmProjects/PythonProject1/GroupProject/src/data/database.db"
DATA_FILE = "src/data/seed.json"  # имя JSON-файла с твоими данными

# ---------- ORM ----------
Base = declarative_base()


class Zone(Base):
    __tablename__ = "zones"
    id = Column(String, primary_key=True)
    name = Column(String)


class Spot(Base):
    __tablename__ = "spots"
    id = Column(String, primary_key=True)
    zone_id = Column(String, ForeignKey("zones.id"))
    number = Column(Integer)
    status = Column(String)
    kind = Column(String)
    features = Column(JSON)
    zone = relationship("Zone")


class Tariff(Base):
    __tablename__ = "tariffs"
    id = Column(String, primary_key=True)
    zone_id = Column(String, ForeignKey("zones.id"), nullable=True)
    kind = Column(String)
    base = Column(Float)
    per_hour = Column(Float)
    free_minutes = Column(Integer)
    zone = relationship("Zone")


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(String, primary_key=True)
    plate = Column(String)
    kind = Column(String)


class Rule(Base):
    __tablename__ = "rules"
    id = Column(String, primary_key=True)
    kind = Column(String)
    payload = Column(JSON)


class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    vehicle_id = Column(String, ForeignKey("vehicles.id"))
    start = Column(DateTime)
    end = Column(DateTime, nullable=True)
    spot_id = Column(String, ForeignKey("spots.id"))
    status = Column(String)
    vehicle = relationship("Vehicle")
    spot = relationship("Spot")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    amount = Column(Float)
    ts = Column(DateTime)
    method = Column(String)
    session = relationship("Session")


class Violation(Base):
    __tablename__ = "violations"
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    plate = Column(String)
    code = Column(String)
    ts = Column(DateTime)
    amount = Column(Float)
    reason = Column(String)
    session = relationship("Session")


class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    ts = Column(DateTime)
    type = Column(String)
    payload = Column(JSON)


# ---------- Заполнение ----------
def parse_datetime(ts):
    return datetime.fromisoformat(ts) if ts else None


def fill_database(data):
    engine = create_engine(DB_URL, echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # Вставка данных
    db.bulk_insert_mappings(Zone, data["zones"])
    db.bulk_insert_mappings(Spot, data["spots"])
    db.bulk_insert_mappings(Tariff, data["tariffs"])
    db.bulk_insert_mappings(Vehicle, data["vehicles"])
    db.bulk_insert_mappings(Rule, data["rules"])

    # Конвертация ISO-даты в datetime для событий и сессий
    for item in data["events"]:
        item["ts"] = parse_datetime(item["ts"])
    for item in data["sessions"]:
        item["start"] = parse_datetime(item["start"])
        item["end"] = parse_datetime(item["end"])
    for item in data["payments"]:
        item["ts"] = parse_datetime(item["ts"])
    for item in data["violations"]:
        item["ts"] = parse_datetime(item["ts"])

    db.bulk_insert_mappings(Event, data["events"])
    db.bulk_insert_mappings(Session, data["sessions"])
    db.bulk_insert_mappings(Payment, data["payments"])
    db.bulk_insert_mappings(Violation, data["violations"])

    db.commit()
    db.close()
    print("✅ База успешно заполнена!")


if __name__ == "__main__":
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    fill_database(data)
