from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Enum
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
    type = Column(String)
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
