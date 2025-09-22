from core.transforms import *
from functools import reduce


# Тесты базовых функций
def test_spot_avaliable_1():
    (s1, s2) = (
        Session(
            "s1",
            "v1",
            "2025-09-23T13:53:00",
            SpotStatus.OCCUPIED,
            "spot_1",
            None,
            "tariff_1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s2",
            "v2",
            "2025-09-23T10:34:00",
            SpotStatus.AVAILABLE,
            "spot_2",
            "2025-09-23T10:48:00",
            "tariff_2",
            SessionStatus.CLOSED,
        ),
    )
    assert (
        is_spot_avaliable(
            (s1, s2),
            "spot_1",
        )
        == False
    )


def test_spot_free_2():
    (s1, s2) = (
        Session(
            "s1",
            "v1",
            "2025-09-23T13:53:00",
            SpotStatus.OCCUPIED,
            "spot_1",
            None,
            "tariff_1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s2",
            "v2",
            "2025-09-23T10:34:00",
            SpotStatus.AVAILABLE,
            "spot_2",
            "2025-09-23T10:48:00",
            "tariff_2",
            SessionStatus.CLOSED,
        ),
    )
    assert (
        is_spot_avaliable(
            (s1, s2),
            "spot_2",
        )
        == True
    )


def test_vehicle_free_1():
    (s1, s2) = (
        Session(
            "s1",
            "v1",
            "2025-09-23T13:53:00",
            SpotStatus.OCCUPIED,
            "spot_1",
            None,
            "tariff_1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s2",
            "v2",
            "2025-09-23T10:34:00",
            SpotStatus.AVAILABLE,
            "spot_2",
            "2025-09-23T10:48:00",
            "tariff_2",
            SessionStatus.CLOSED,
        ),
    )
    assert (
        is_vehicle_free(
            (s1, s2),
            "v1",
        )
        == False
    )


def test_vehicle_free_2():
    (s1, s2) = (
        Session(
            "s1",
            "v1",
            "2025-09-23T13:53:00",
            SpotStatus.OCCUPIED,
            "spot_1",
            None,
            "tariff_1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s2",
            "v2",
            "2025-09-23T10:34:00",
            SpotStatus.AVAILABLE,
            "spot_2",
            "2025-09-23T10:48:00",
            "tariff_2",
            SessionStatus.CLOSED,
        ),
    )
    assert (
        is_vehicle_free(
            (s1, s2),
            "v2",
        )
        == True
    )


# Тест 1. Сессия на уже занятом месте НЕ должна открыться.
def test_open_session_1():
    (s1, s2) = (
        Session(
            "s1",
            "v1",
            "2025-09-23T13:53:00",
            SpotStatus.OCCUPIED,
            "spot_1",
            None,
            "tariff_1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s2",
            "v2",
            "2025-09-23T10:34:00",
            SpotStatus.AVAILABLE,
            "spot_2",
            "2025-09-23T10:48:00",
            "tariff_2",
            SessionStatus.CLOSED,
        ),
    )

    assert open_session(
        (s1, s2),
        "v3",
        "spot_1",
        SpotStatus.AVAILABLE,
        "2025-09-23T13:55:00",
        "s3",
        "tariff_2",
    ) == (
        s1,
        s2,
    )


# Тест 2. Открытие сессии на свободной зоне
def test_open_session_2():
    (s1, s2) = (
        Session(
            "s1",
            "v1",
            "2025-09-23T13:53:00",
            SpotStatus.AVAILABLE,
            "spot_1",
            None,
            "tariff_1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s2",
            "v2",
            "2025-09-23T10:34:00",
            SpotStatus.AVAILABLE,
            "spot_2",
            "2025-09-23T10:48:00",
            "tariff_2",
            SessionStatus.CLOSED,
        ),
    )

    result = open_session(
        (s1, s2),
        "v3",
        "spot_3",
        SpotStatus.AVAILABLE,
        "2025-09-23T13:55:00",
        "s3",
        "tariff_2",
    )

    assert result == (
        s1,
        s2,
        Session(
            "s3",
            "v3",
            "2025-09-23T13:55:00",
            SpotStatus.AVAILABLE,
            "spot_3",
            None,
            "tariff_2",
            SessionStatus.ACTIVE,
            result[2].uid,
        ),
    )


# Тест 3. Может быть только одна активная сессия на транспорт
# Но при этом неважно занял ли он место или нет
def test_open_session_3():
    (s1, s2) = (
        Session(
            "s-v1-13:53",
            "v1",
            "2025-09-13T13:53:00",
            SpotStatus.AVAILABLE,
            "spot_1",
            None,
            "tariff_1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s-v2-10:32",
            "v2",
            "2025-09-13T10:34:00",
            SpotStatus.AVAILABLE,
            "spot_2",
            "2025-09-13T10:48:00",
            "tariff_2",
            SessionStatus.CLOSED,
        ),
    )

    assert open_session(
        (s1, s2),
        "v1",
        "spot_3",
        SpotStatus.AVAILABLE,
        "2025-09-13T13:55:00",
        None,
        "tariff_2",
    ) == (s1, s2)


# Тест 4: обычное закрытие сессии (используется map)
def test_close_session_1():

    a: Session = Session(
        "session_1",
        "v1",
        "2025-09-13T10:55:00",
        SpotStatus.AVAILABLE,
        "spot_1",
        None,
        "tariff_1",
        SessionStatus.ACTIVE,
    )
    b: Session = Session(
        "session_2",
        "v2",
        "2025-09-13T10:43:00",
        SpotStatus.OCCUPIED,
        "spot_2",
        None,
        "tariff_1",
        SessionStatus.ACTIVE,
    )

    assert close_session(
        (a, b),
        "session_1",
        "2025-09-13T11:05:00",
    ) == (
        Session(
            "session_1",
            "v1",
            "2025-09-13T10:55:00",
            SpotStatus.AVAILABLE,
            "spot_1",
            "2025-09-13T11:05:00",
            "tariff_1",
            SessionStatus.CLOSED,
            a.uid,
        ),
        b,
    )


# Тест 5: попытка закрыть уже закрытую ранее сессию. (НЕ None время не должно измениться на новое)
def test_close_session_2():

    a: Session = Session(
        "session_1",
        "v1",
        "2025-09-13T10:55:00",
        SpotStatus.AVAILABLE,
        "spot_1",
        "2025-09-13T10:59:00",
        "tariff_1",
        SessionStatus.CLOSED,
    )
    b: Session = Session(
        "session_2",
        "v2",
        "2025-09-13T10:43:00",
        SpotStatus.OCCUPIED,
        "spot_2",
        None,
        "tariff_1",
        SessionStatus.ACTIVE,
    )

    assert close_session(
        (a, b),
        "session_1",
        "2025-09-13T11:05:00",
    ) == (
        a,
        b,
    )


# Тест 6: подсчёт итоговой выручки. (используется reduce)
def test_total_revenue():
    assert (
        total_revenue(
            (
                Payment("payment_1", "session_1", 500, "2025-09-13T10:55:00"),
                Payment("payment_2", "session_2", 200, "2025-09-13T10:57:00"),
                Payment("payment_3", "session_3", 900, "2025-09-13T10:59:00"),
                Payment("payment_4", "session_4", 400, "2025-09-13T11:05:00"),
                Payment("payment_5", "session_5", 600, "2025-09-13T11:13:00"),
                Payment("payment_6", "session_6", 800, "2025-09-13T11:24:00"),
            )
        )
        == 3400
    )


# Тест 7: список активных сессий. (используется filter)
#
def test_active_sessions():

    (s1, s2, s3, s4, s5) = (
        Session(
            "s1",
            "v1",
            "2025-09-13T10:22:00",
            SpotStatus.AVAILABLE,
            "sp1",
            "2025-09-13T10:45:00",
            "tariff1",
            SessionStatus.CLOSED,
        ),
        Session(
            "s2",
            "v2",
            "2025-09-13T10:32:00",
            SpotStatus.AVAILABLE,
            "sp2",
            None,
            "tariff1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s3",
            "v3",
            "2025-09-13T10:36:00",
            SpotStatus.AVAILABLE,
            "sp3",
            None,
            "tariff1",
            SessionStatus.ACTIVE,
        ),
        Session(
            "s4",
            "v4",
            "2025-09-13T10:37:00",
            SpotStatus.AVAILABLE,
            "sp4",
            "2025-09-13T10:56:00",
            "tariff1",
            SessionStatus.CLOSED,
        ),
        Session(
            "s5",
            "v5",
            "2025-09-13T10:45:00",
            SpotStatus.AVAILABLE,
            "sp5",
            None,
            "tariff1",
            SessionStatus.ACTIVE,
        ),
    )

    assert active_sessions((s1, s2, s3, s4, s5)) == (s2, s3, s5)
