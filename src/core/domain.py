# from __future__ import annotations
from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import Optional, Set, List, Dict
from datetime import datetime
from enum import Enum
from enums import *
import uuid

@dataclass(frozen=True)
class Zone:
    name: str
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Spot:
    id: str
    zone_id: uuid.UUID
    number: int
    status: SpotStatus
    kind: SpotKind
    features: Optional[List[str]] = Field(default_factory=list)
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Tariff:
    id: str
    base: int              # базовая ставка
    kind: TariffKind
    per_minutes: int
    free_minutes: int
    zone_id: Optional[uuid.UUID] = None
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class Vehicle:
    id: str
    plate: str             # example: 123ABC05
    kind: VehicleKind
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Event:
    id: str
    type: EventType
    ts: datetime
    payload: Optional[Dict] = None
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Session:
    id: str
    vehicle_id: str
    start: datetime        # utime
    spot_id: Optional[str] = None
    end: Optional[datetime] = None
    tariff_id: Optional[str] = None
    status: SessionStatus = SessionStatus.ACTIVE
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class Payment:
    id: str
    session_id: str
    amount: int
    ts: datetime
    method: Optional[PaymentType] = None
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Violation:  # нарушение
    id: str
    session_id: Optional[str]
    amount: int
    plate: str
    ts: datetime
    code: str
    reason: Optional[str] = None
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class Rule:
    id: str
    kind: RuleKind
    payload: dict   # параметры правила (например {"hours": 3} или {"zone": "A"})
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)