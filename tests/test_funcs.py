from core.transforms import *
from functools import reduce


# Тесты базовых функций
def test_spot_free_1():
    assert (
        is_spot_free(
            (
                Session(
                    "s-v1-13:53",
                    "v1",
                    "spot_1",
                    "13:53",
                    None,
                    "tariff_1",
                ),
                Session(
                    "s-v2-10:32",
                    "v2",
                    "spot_2",
                    "10:34",
                    "10:48",
                    "tariff_2",
                ),
            ),
            "spot_1",
        )
        == False
    )


def test_spot_free_2():
    assert (
        is_spot_free(
            (
                Session(
                    "s-v1-13:53",
                    "v1",
                    "spot_1",
                    "13:53",
                    "13:54",
                    "tariff_1",
                ),
                Session(
                    "s-v2-10:32",
                    "v2",
                    "spot_2",
                    "10:34",
                    "10:48",
                    "tariff_2",
                ),
            ),
            "spot_1",
        )
        == True
    )


def test_vehicle_free_1():
    assert (
        is_vehicle_free(
            (
                Session(
                    "s-v1-13:53",
                    "v1",
                    "spot_1",
                    "13:53",
                    None,
                    "tariff_1",
                ),
                Session(
                    "s-v2-10:32",
                    "v2",
                    "spot_2",
                    "10:34",
                    "10:48",
                    "tariff_2",
                ),
            ),
            "v1",
        )
        == False
    )


def test_vehicle_free_2():
    assert (
        is_vehicle_free(
            (
                Session(
                    "s-v1-13:53",
                    "v1",
                    "spot_1",
                    "13:53",
                    None,
                    "tariff_1",
                ),
                Session(
                    "s-v2-10:32",
                    "v2",
                    "spot_2",
                    "10:34",
                    "10:48",
                    "tariff_2",
                ),
            ),
            "v2",
        )
        == True
    )


# Тест 1. Сессия на уже занятом месте НЕ должна открыться.
def test_open_session_1():
    assert open_session(
        (
            Session(
                "s-v1-13:53",
                "v1",
                "spot_1",
                "13:53",
                None,
                "tariff_1",
            ),
            Session(
                "s-v2-10:32",
                "v2",
                "spot_2",
                "10:34",
                "10:48",
                "tariff_2",
            ),
        ),
        "v3",
        "spot_1",
        "13:55",
        None,
        "tariff_2",
    ) == (
        Session(
            "s-v1-13:53",
            "v1",
            "spot_1",
            "13:53",
            None,
            "tariff_1",
        ),
        Session(
            "s-v2-10:32",
            "v2",
            "spot_2",
            "10:34",
            "10:48",
            "tariff_2",
        ),
    )


# Тест 2. Открытие сессии на свободной зоне
def test_open_session_2():
    assert open_session(
        (
            Session(
                "s-v1-13:53",
                "v1",
                "spot_1",
                "13:53",
                None,
                "tariff_1",
            ),
            Session(
                "s-v2-10:32",
                "v2",
                "spot_2",
                "10:34",
                "10:48",
                "tariff_2",
            ),
        ),
        "v3",
        "spot_3",
        "13:55",
        None,
        "tariff_2",
    ) == (
        Session(
            "s-v1-13:53",
            "v1",
            "spot_1",
            "13:53",
            None,
            "tariff_1",
        ),
        Session(
            "s-v2-10:32",
            "v2",
            "spot_2",
            "10:34",
            "10:48",
            "tariff_2",
        ),
        Session(
            "s-v3-13:55",
            "v3",
            "spot_3",
            "13:55",
            None,
            "tariff_2",
        ),
    )


# Тест 3. Транспорт, уже занявший своё место не сможет открыть сессию
def test_open_session_3():
    assert open_session(
        (
            Session(
                "s-v1-13:53",
                "v1",
                "spot_1",
                "13:53",
                None,
                "tariff_1",
            ),
            Session(
                "s-v2-10:32",
                "v2",
                "spot_2",
                "10:34",
                "10:48",
                "tariff_2",
            ),
        ),
        "v1",
        "spot_3",
        "13:55",
        None,
        "tariff_2",
    ) == (
        Session(
            "s-v1-13:53",
            "v1",
            "spot_1",
            "13:53",
            None,
            "tariff_1",
        ),
        Session(
            "s-v2-10:32",
            "v2",
            "spot_2",
            "10:34",
            "10:48",
            "tariff_2",
        ),
    )


# Тест 4: обычное закрытие сессии (используется map)
def test_close_session_1():
    assert close_session(
        (
            Session("session_1", "v1", "spot_1", "10:55", None, "tariff_1"),
            Session("session_2", "v2", "spot_2", "10:43", None, "tariff_1"),
        ),
        "session_1",
        "11:05",
    ) == (
        Session("session_1", "v1", "spot_1", "10:55", "11:05", "tariff_1"),
        Session("session_2", "v2", "spot_2", "10:43", None, "tariff_1"),
    )


# Тест 5: попытка закрыть уже закрытую ранее сессию. (НЕ None время не должно измениться на новое)
def test_close_session_2():
    assert close_session(
        (
            Session("session_1", "v1", "spot_1", "10:55", "10:59", "tariff_1"),
            Session("session_2", "v2", "spot_2", "10:43", None, "tariff_1"),
        ),
        "session_1",
        "11:05",
    ) == (
        Session("session_1", "v1", "spot_1", "10:55", "10:59", "tariff_1"),
        Session("session_2", "v2", "spot_2", "10:43", None, "tariff_1"),
    )


# Тест 6: подсчёт итоговой выручки. (используется reduce)
def test_total_revenue():
    assert (
        total_revenue(
            (
                Payment("payment_1", "session_1", 500, "10:55"),
                Payment("payment_2", "session_2", 200, "10:57"),
                Payment("payment_3", "session_3", 900, "10:59"),
                Payment("payment_4", "session_4", 400, "11:05"),
                Payment("payment_5", "session_5", 600, "11:13"),
                Payment("payment_6", "session_6", 800, "11:24"),
            )
        )
        == 3400
    )


# Тест 7: список активных сессий. (используется filter)
def test_active_sessions():
    assert active_sessions(
        (
            Session("s1", "v1", "sp1", "10:22", "10:45", "tariff1"),
            Session("s2", "v2", "sp2", "10:32", None, "tariff1"),
            Session("s3", "v3", "sp3", "10:36", None, "tariff1"),
            Session("s4", "v4", "sp4", "10:37", "10:56", "tariff1"),
            Session("s5", "v5", "sp5", "10:45", None, "tariff1"),
        )
    ) == (
        Session("s2", "v2", "sp2", "10:32", None, "tariff1"),
        Session("s3", "v3", "sp3", "10:36", None, "tariff1"),
        Session("s5", "v5", "sp5", "10:45", None, "tariff1"),
    )
