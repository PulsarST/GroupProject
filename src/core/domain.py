# from __future__ import annotations
from pydantic.dataclasses import dataclass as pydanticdataclass
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid
from dataclasses import field


class EventType(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    PAY = "PAY"
    VIOLATION = "VIOLATION"
    SPOT_AVAILABLE = "SPOT_AVAILABLE"
    SPOT_OCCUPIED = "SPOT_OCCUPIED"


class PaymentType(str, Enum):
    CARD = "CARD"
    CASH = "CASH"
    ANOTHER = "ANOTHER"


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


@pydanticdataclass(frozen=True)
class Zone:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str


@pydanticdataclass(frozen=True)
class Spot:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    zone_id: str
    number: int
    status: str  # (occupied / available)
    kind: str    # (unavailable / accessible / standard / truck)


@pydanticdataclass(frozen=True)
class Tariff:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    id: str
    base: int              # базовая ставка
    kind: str              # (accessible / standard / holiday)
    per_minutes: int
    free_minutes: int
    zone_id: Optional[str] = None


@pydanticdataclass(frozen=True)
class Vehicle:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    id: str
    plate: str             # example: 123ABC05
    kind: str              # (bike / car / truck)


@pydanticdataclass(frozen=True)
class Event:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    id: str
    type: EventType
    spot_id: str
    ts: datetime
    amount: Optional[int] = None
    vehicle_id: Optional[str] = None


@pydanticdataclass(frozen=True)
class Session:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    id: str
    vehicle_id: str
    start: datetime        # utime
    spot_id: Optional[str] = None
    end: Optional[datetime] = None
    tariff_id: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE


@pydanticdataclass(frozen=True)
class Payment:
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    id: str
    session_id: str
    amount: int
    ts: datetime
    method: Optional[PaymentType] = None


@pydanticdataclass(frozen=True)
class Violation:  # нарушение
    uid: uuid.UUID = field(default_factory=uuid.uuid4)
    id: str
    session_id: Optional[str]
    # rule_id: str # TODO
    ts: datetime
    description: Optional[str] = None
