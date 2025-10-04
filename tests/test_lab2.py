from core.filter import *
from core.transforms import *


#Кортеж спотов который будет использоваться в тестах
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

#Кортеж сессий который будет использоваться в тестах
sessions = (
    Session(
    "se1",
    "v1",
    "2025-09-20T09:00:00",
    SpotStatus.AVAILABLE,
    "s1",
    "2025-09-20T09:02:00",
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

#########################
# ---Тесты замыкания--- #
#########################

def test_zone_id_filter_1():
    """ Проверка корректности работы фильтра
        спотов по id зоны.
    """
    testing_by_zone = make_by_zone(spots)
    assert reduce(
        lambda acc, spot : acc and spot.zone_id == "z2",
        testing_by_zone("z2")
    )

def test_kind_filter_1():
    """ Проверка корректности работы фильтра
        спотов по его типу.
    """
    testing_by_kind = make_by_kind(spots)
    assert reduce(
        lambda acc, spot : acc and spot.kind == SpotKind.ACCESSIBLE,
        testing_by_kind(SpotKind.ACCESSIBLE)
    )

def test_time_range_1():
    """ Проверка корректности работы фильтра при
        вводе диапазона, включающего все сессии.

        Функция должна вернуть полный кортеж
        сессий.
    """
    testing_by_time_range = make_by_time_range(sessions)
    assert is_tuple_data_same(
        testing_by_time_range(date("2025-09-20T09:00:00"),date("2025-09-20T09:10:00")),
        sessions
    )

def test_time_range_2():
    """ Проверка корректности работы фильтра случайного
        диапазона, задевающего несколько сессий.

        Функция должна вернуть кортеж сессий, которые были
        активны на данный период.

        Также она уверяет, что сессия sessions[0]
        не войдёт, т.к в 09:02 она уже 
        считается закрытой, то есть неактивной.
    """
    testing_by_time_range = make_by_time_range(sessions)
    assert is_tuple_data_same(
        testing_by_time_range(date("2025-09-20T09:02:00"),date("2025-09-20T09:05:00")),
        (
            sessions[1],
            sessions[2],
            sessions[5],
            sessions[6],
            sessions[8],
        )
    )

def test_time_range_3():
    """ Проверка корректности работы фильтра активных 
        на данный момент сессий, которые начались вне указанной 
        в фильтре зоны.

        Активная сессия началась в 2025 году, 
        а ищем мы по периоду великой отечественной войны.

        Функция должна вернуть пустой кортеж.
    """
    testing_by_time_range = make_by_time_range(sessions)
    assert not testing_by_time_range(date("1941-09-01T04:00:00"),date("1945-05-9T09:07:00"))