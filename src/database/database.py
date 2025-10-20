from sqlalchemy import DateTime, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from typing import List
from datetime import datetime

from core.enums import SessionStatus, SpotStatus, TariffKind


class Base(DeclarativeBase):
    pass


class Spot(Base):
    __tablename__ = "spots"

    id: Mapped[int] = mapped_column(
            Integer, primary_key=True)

    zone_id: Mapped[int] = mapped_column(
            Integer, ForeignKey("zones.id"))

    zone: Mapped["Zone"] = relationship("Zone", back_populates="spots")

    spot_type: Mapped[SpotStatus] = mapped_column(
            SQLEnum(SpotStatus),
            default=SpotStatus.AVAILABLE,
            nullable=False)


class Zone(Base):
    __tablename__ = "zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    spots: Mapped[List[Spot]] = relationship("Spot", uselist=True,
                                             back_populates="zone")


class Tariff(Base):
    __tablename__ = "tarrifs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    base: Mapped[int] = mapped_column(Integer, default=0)
    kind: Mapped[TariffKind] = mapped_column(
            SQLEnum(TariffKind),
            default=None)

    per_hour: Mapped[int] = mapped_column(Integer, default=0)
    free_minutes: Mapped[int] = mapped_column(Integer, default=15)
    zone_id: Mapped[int] = mapped_column(Integer, ForeignKey("zones.id"))
    

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start: Mapped[datetime] = mapped_column(DateTime, default=None)
    end: Mapped[datetime] = mapped_column(DateTime, default=None)
    status: Mapped[SessionStatus] = mapped_column(
            SQLEnum(SessionStatus),
            default=SessionStatus.ACTIVE,
            nullable=False)

    spot_status: Mapped[SpotStatus] = mapped_column(
            SQLEnum(SpotStatus),
            default=SpotStatus.AVAILABLE,
            nullable=None)

    tarriff_id: Mapped[int] = mapped_column(
            Integer,
            ForeignKey("tarrifs.id"))



