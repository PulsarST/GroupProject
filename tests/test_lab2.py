from core.filter import *
from core.transforms import *

spots = (
        Spot(
            "s1",
            "z1",
            1,
            SpotStatus.AVAILABLE,
            SpotKind.STANDARD,
            []
        ),
        Spot(
            "s2",
            "z2",
            2,
            SpotStatus.AVAILABLE,
            SpotKind.TRUCK,
            []
        ),
        Spot(
            "s3",
            "z2",
            3,
            SpotStatus.AVAILABLE,
            SpotKind.ACCESSIBLE,
            []
        ),
        Spot(
            "s4",
            "z3",
            4,
            SpotStatus.AVAILABLE,
            SpotKind.ACCESSIBLE,
            []
        ),
        Spot(
            "s5",
            "z4",
            5,
            SpotStatus.AVAILABLE,
            SpotKind.STANDARD,
            []
        ),
    )


sessions = (
    Session(
    "se1",
    "v1",
    "2025-09-20T09:00:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:01:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:02:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:03:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:04:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:05:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:06:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:07:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:08:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:09:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:00:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:10:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:00:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:05:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:06:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:10:00",
    "t1",
    SessionStatus.CLOSED
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:02:00",
    SpotStatus.AVAILABLE,
    "s1",
    None,
    "t1",
    SessionStatus.ACTIVE
    ),
    Session(
    "se1",
    "v1",
    "2025-09-20T09:09:00",
    SpotStatus.AVAILABLE,
    "s1",
    None,
    "t1",
    SessionStatus.ACTIVE
    ),
)

def test_zone_id_filter_1():
    testing_by_zone = make_by_zone(spots)
    assert is_tuple_data_same(
        testing_by_zone("z2"),
        (
            spots[1],
            spots[2],
        )
    )

def test_zone_id_filter_2():
    testing_by_zone = make_by_zone(spots)
    assert is_tuple_data_same(
        testing_by_zone("z3"),
        (
            spots[3],
        )
    )

def test_kind_filter_1():
    testing_by_kind = make_by_kind(spots)
    assert is_tuple_data_same(
        testing_by_kind(SpotKind.ACCESSIBLE),
        (
            spots[2],
            spots[3],
        )
    )

def test_kind_filter_2():
    testing_by_kind = make_by_kind(spots)
    assert is_tuple_data_same(
        testing_by_kind(SpotKind.STANDARD),
        (
            spots[0],
            spots[4],
        )
    )

def test_kind_filter_3():
    testing_by_kind = make_by_kind(spots)
    assert is_tuple_data_same(
        testing_by_kind(SpotKind.TRUCK),
        (
            spots[1],
        )
    )

def test_time_range_1():
    testing_by_time_range = make_by_time_range(sessions)
    assert is_tuple_data_same(
        testing_by_time_range(date("2025-09-20T09:00:00"),date("2025-09-20T09:10:00")),
        sessions
    )

def test_time_range_2():
    testing_by_time_range = make_by_time_range(sessions)
    assert is_tuple_data_same(
        testing_by_time_range(date("2025-09-20T09:02:00"),date("2025-09-20T09:07:00")),
        (
            sessions[1],
            sessions[2],
            sessions[3],
            sessions[5],
            sessions[6],
            sessions[7],
            sessions[8],
        )
    )