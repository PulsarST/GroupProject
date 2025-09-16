# Заготовка без иммутабельности!


from typing import Optional, List, Dict, Tuple
from pydantic import BaseModel, Field

# Зона парковки (A, B, C)
class Zone(BaseModel):
    id: int
    name: str


# Место (kind: regular/disabled/ev; features: charger, covered)
class Spot(BaseModel):
    id: int
    zone_id: int
    number: int
    kind: str
    features: Tuple[str, ...] = ()


# Тариф (цены в тыйын/копейках)
class Tariff(BaseModel):
    id: int
    zone_id: Optional[int] = None
    kind: str
    base: int
    per_hour: int
    free_minutes: int


# Транспорт (car, van, ev)
class Vehicle(BaseModel):
    id: int
    plate: str
    kind: str


# Событие (ENTRY, EXIT, PAY, VIOLATION, SENSOR_OCCUPIED, SENSOR_FREE)
class Event(BaseModel):
    id: int
    ts: str
    name: str
    payload: Dict


# Сессия (active|closed|lost)
class Session(BaseModel):
    id: int
    vehicle_id: int
    spot_id: Optional[int] = None
    start: str
    end: Optional[str] = None
    status: str


# Платёж
class Payment(BaseModel):
    id: int
    session_id: int
    amount: int
    ts: str
    method: str


# Нарушение
class Violation(BaseModel):
    id: int
    session_id: Optional[int] = None
    plate: str
    code: str
    ts: str
    amount: int
    reason: str


# Правило (напр. «макс. время стоянки 3 часа», «только EV»)
class Rule(BaseModel):
    id: int
    kind: str
    payload: Dict
