#from __future__ import annotations ###
from pydantic.dataclasses import dataclass as pydanticdataclass
from typing import Optional, Tuple
from datetime import datetime
from enum import Enum
#import uuid


class EventType(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    PAY = "PAY"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    LOST = "lost"


@pydanticdataclass(frozen=True)
class Zone:
    id: str
    name: str
    # description: Optional[str] = None


@pydanticdataclass(frozen=True)
class Spot:
    id: str
    zone_id: str
    number: int
    kind: str
    features: Tuple[str, ...] = ()


@pydanticdataclass(frozen=True)
class Tariff:
    id: str
    base: int
    kind: str
    per_hour: int
    free_minutes: int
    zone_id: Optional[str] = None


@pydanticdataclass(frozen=True)
class Vehicle:
    id: str
    plate: str
    kind: str


# @pydanticdataclass(frozen=True)
# class Event:
#     id: str
#     type: EventType
#     vehicle_id: str
#     spot_id: str
#     timestamp: datetime
#     amount: Optional[int] = None


@pydanticdataclass(frozen=True)
class Session:
    id: str
    vehicle_id: str
    start: datetime
    spot_id: Optional[str] = None
    end: Optional[datetime] = None
    tariff_id: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE


@pydanticdataclass(frozen=True)
class Payment:
    id: str
    session_id: str
    amount: int
    timestamp: datetime
    method: Optional[str] = None


# @pydanticdataclass(frozen=True)
# class Violation:
#     id: str
#     session_id: Optional[str]
#     rule_id: str
#     timestamp: datetime
#     description: Optional[str] = None
