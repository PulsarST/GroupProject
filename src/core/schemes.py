# from __future__ import annotations ###
from typing import Optional, Dict
from pydantic import BaseModel
from datetime import datetime
from core.enums import (
    SpotStatus,
    SpotType,
    TariffKind,
    VehicleKind,
    EventType,
    SessionStatus,
    PaymentType,
)


class Spot(BaseModel):
    """
    Spot is a place where cars stands
    SpotKind is a kind of Spot if it's
    UNAVAILABLE, ACCESSIBLE, STANDARD or if it for TRUCK

    exmplae:
    id: "zone1_id"
    """
    id: str
    status: SpotStatus
    type:  SpotType


class Tariff(BaseModel):
    """
    Tariff describes a rate of the Spot,
    how many time a car's going to stands and amount of money
    kind: ACCESSIBLE, STANDARD, HOLIDAY
    """
    id: str
    base: int  # базовая ставка
    kind: TariffKind
    per_hour: int
    free_minutes: int
    zone_id: Optional[str] = None


class Vehicle(BaseModel):
    """
    describes a vehicle model
    kind: BIKE, CAR, TRUCK
    """
    id: str
    plate: str  # example: 123ABC05
    kind: VehicleKind


class Event(BaseModel):
    """
    Event is a model for all events which can happen
    type: ENTRY, EXIT, PAY, VIOLATION, SPOT_AVAILABLE
    and SPOT_OCCUPIED
    """
    id: str
    type: EventType
    ts: datetime
    payload: Optional[Dict] = None


class Session(BaseModel):
    id: str
    start: datetime  # utime
    spot_status: SpotStatus
    spot_id: Optional[str] = None
    end: Optional[datetime] = None
    tariff_id: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE


class Payment(BaseModel):
    id: str
    session_id: str
    amount: int
    ts: datetime
    method: Optional[PaymentType] = None


# class Violation(BaseModel):  # нарушение
#    id: str
#    session_id: Optional[str]
#    plate: str
#   ts: datetime
#    code: str
#    amount: Optional[int] = None
#    reason: Optional[str] = None


# class Rule(BaseModel):
#    id: str
#    kind: RuleKind
#    payload: dict  # параметры правила (например {"hours": 3} или {"zone": "A"})

