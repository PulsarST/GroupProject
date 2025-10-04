from .transforms import *

# ---- Фильтры ----


def make_by_zone(spots: Tuple[Spot, ...]):
    def by_zone(zone_id: str) -> Tuple[Spot, ...]:
        return tuple(filter(lambda spot : spot.zone_id == zone_id, spots))

    return by_zone

def make_by_kind(spots: Tuple[Spot, ...]):
    def by_kind(kind: SpotKind) -> Tuple[Spot, ...]:
        return tuple(filter(lambda spot : spot.kind == kind, spots))

    return by_kind

# Смотрит активные сесси на период
def make_by_time_range(sessions: Tuple[Session, ...]):
    def by_time_range(start: datetime, end: datetime) -> Tuple[Session, ...]:
        return tuple(filter(lambda session: (session.end == None or start < session.end) and end >= session.start, sessions))

    return by_time_range