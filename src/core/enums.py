from enum import Enum


class SpotStatus(str, Enum):
    OCCUPIED = "occupied"
    AVAILABLE = "available"


class SpotKind(str, Enum):
    UNAVAILABLE = "unavailable"
    ACCESSIBLE = "accessible"
    STANDARD = "standard"
    TRUCK = "truck"


class TariffKind(str, Enum):
    ACCESSIBLE = "accessible"
    STANDARD = "standard"
    HOLIDAY = "holiday"


class VehicleKind(str, Enum):
    BIKE = "bike"
    CAR = "car"
    TRUCK = "truck"


class EventType(str, Enum):
    ENTRY = "entry"
    EXIT = "exit"
    PAY = "pay"
    VIOLATION = "violation"
    SPOT_AVAILABLE = "spot_available"
    SPOT_OCCUPIED = "spot_occupied"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class PaymentType(str, Enum):
    CARD = "card"
    CASH = "cash"
    ANOTHER = "another"


class RuleKind(str, Enum):
    MAX_PARKING_TIME = "max_parking_time"
    ONLY_ACCESSIBLE = "only_accessible"
    NO_OVERNIGHT = "no_overnight"
    ZONE_ONLY = "zone_only"
    TIME_LIMIT = "time_limit"
    DISABLED_ONLY = "disabled_only"
