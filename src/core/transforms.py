from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from typing import Tuple, Optional
import json
from functools import reduce
from datetime import datetime
from copy import copy

from .domain import *
from .enums import *

# ---- Сокращённый создатель datetime бъекта ----
date = lambda str: datetime.strptime(str, "%Y-%m-%dT%H:%M:%S")


# ---- Загрузчик сид-данных ----
def _to_tuple(cls, items):
    return tuple(cls(**it) for it in items)


def load_seed(
    path: str,
) -> Tuple[
    Tuple[Zone, ...],
    Tuple[Spot, ...],
    Tuple[Tariff, ...],
    Tuple[Vehicle, ...],
    Tuple[Event, ...],
    Tuple[Rule, ...],
    Tuple[Session, ...],
    Tuple[Payment, ...],
    Tuple[Violation, ...],
]:
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    zones = _to_tuple(Zone, j.get("zones", []))
    spots = _to_tuple(Spot, j.get("spots", []))
    tariffs = _to_tuple(Tariff, j.get("tariffs", []))
    vehicles = _to_tuple(Vehicle, j.get("vehicles", []))
    events = _to_tuple(Event, j.get("events", []))
    rules = _to_tuple(Rule, j.get("rules", []))
    sessions: Tuple[Session, ...] = tuple()
    payments: Tuple[Payment, ...] = tuple()
    violations: Tuple[Violation, ...] = tuple()
    return (
        zones,
        spots,
        tariffs,
        vehicles,
        events,
        rules,
        sessions,
        payments,
        violations,
    )


# ---- Манипуляции с сессиями ----
# def open_session(
#     sessions: Tuple[Session, ...],
#     vehicle_id: str,
#     spot_id: str,
#     start: str,
#     sid: Optional[str] = None,
#     tariff_id: Optional[str] = None,
# ) -> Tuple[Session, ...]:

#     sid = sid or f"s-{vehicle_id}-{start}"
#     new = Session(id=sid, vehicle_id=vehicle_id, spot_id=spot_id, start=start, end=None, tariff_id=tariff_id)
#     return tuple(list(sessions) + [new])


def open_session(
    sessions: Tuple[Session, ...],
    vehicle_id: str,
    spot_id: str,
    spot_status: SpotStatus,
    start: datetime,
    sid: Optional[str] = None,
    tariff_id: Optional[str] = None,
) -> Tuple[Session, ...]:
    sid = sid or f"s-{vehicle_id}-{start}"

    new = Session(
        id=sid,
        vehicle_id=vehicle_id,
        start=start,
        spot_status=spot_status,
        spot_id=spot_id,
        end=None,
        tariff_id=tariff_id,
    )

    correct = is_session_by_spot_active(sessions, spot_id) and is_vehicle_free(
        sessions, vehicle_id
    )

    return tuple(list(sessions) + [new]) if correct else sessions


# def close_session(
#     sessions: Tuple[Session, ...], sid: str, end: str
# ) -> Tuple[Session, ...]:
#     def _close(s: Session):
#         return replace(s, end=end) if s.id == sid else s

#     return tuple(map(_close, sessions))


def close_session(
    sessions: Tuple[Session, ...], sid: str, end: datetime
) -> Tuple[Session, ...]:
    def _close(s: Session):
        return (
            replace(replace(s, end=end), status=SessionStatus.CLOSED)
            if s.id == sid and is_session_active(s)
            else s
        )

    return tuple(map(_close, sessions))


def assign_spot(
    sessions: Tuple[Session, ...], sid: str, spot_id: str
) -> Tuple[Session, ...]:
    def _assign(s: Session):
        return replace(s, spot_id=spot_id) if s.id == sid else s

    return tuple(map(_assign, sessions))


# ---- Финансовые операции ----
def total_revenue(payments: Tuple[Payment, ...]) -> int:
    return reduce(lambda acc, p: acc + p.amount, payments, 0)


def is_session_active(s: Session) -> bool:
    return s.status == SessionStatus.ACTIVE


def is_session_by_spot_active(sessions: Tuple[Session, ...], spot_id: str) -> bool:
    return not tuple(
        filter(
            lambda session: is_session_active(session) and session.spot_id == spot_id,
            sessions,
        )
    )


def active_sessions(sessions: Tuple[Session, ...]) -> Tuple[Session, ...]:
    return tuple(filter(is_session_active, sessions))


def is_spot_avaliable(sessions: Tuple[Session, ...], spot_id: str) -> bool:
    _is_occupied = (
        lambda session: session.spot_id == spot_id
        and session.spot_status == SpotStatus.OCCUPIED
    )
    return not tuple(filter(_is_occupied, sessions))


def is_vehicle_free(sessions: Tuple[Session, ...], vehicle_id: str) -> bool:
    _is_occupied = lambda session: session.vehicle_id == vehicle_id and (
        session.status == SessionStatus.ACTIVE
    )
    return not tuple(filter(_is_occupied, sessions))


def duration_minutes(s: Session) -> int:
    if s.end is None:
        return 0
    # убираем Z, чтобы fromisoformat понимал строку
    start_dt = datetime.fromisoformat(s.start.replace("Z", ""))
    end_dt = datetime.fromisoformat(s.end.replace("Z", ""))
    return int((end_dt - start_dt).total_seconds() / 60)


def avg_session_duration(sessions: Tuple[Session, ...]) -> float:
    closed = tuple(filter(lambda s: s.end is not None, sessions))
    if not closed:
        return 0.0

    durations = tuple(map(duration_minutes, closed))
    total = reduce(lambda acc, x: acc + x, durations, 0)
    return total / len(durations)


def is_obj_data_same(a: object, b: object) -> bool:
    a_dict = copy(a.__dict__)
    b_dict = copy(b.__dict__)
    a_dict.pop("uid")
    b_dict.pop("uid")

    return reduce(
        lambda acc, next: acc and next,
        [i == b_dict[key_i] for key_i, i in a_dict.items()],
    )


def is_tuple_data_same(a: Tuple[object, ...], b: Tuple[object, ...]) -> bool:
    return len(a) == len(b) and reduce(
        lambda acc, next: acc and next,
        [is_obj_data_same(a[i], b[i]) for i in range(len(a))],
    )
