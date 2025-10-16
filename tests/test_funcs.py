from core.transforms import *
from functools import reduce

###############################
# ---Тесты базовых функций--- #
###############################

#   Т.к у нас у моделей есть uid, то пришлось написать функцию,
#   Которая будет сравнивать 2 объекта, при этом игнорируя
#   Аттрибут uid


def test_same_data():
    assert is_obj_data_same(
        Payment("p1", "s1", 600, "2025-10-10T10:00:00", PaymentType.CARD),
        Payment("p1", "s1", 600, "2025-10-10T10:00:00", PaymentType.CARD),
    )


#   В классе сессии есть два аттрибута состояний:
#   Статус сессии и статус места
#   Данные тесты показывают, что функция
#   Отличает состояние сессии от состояния места


def test_spot_avaliable_1():
    (s1, s2) = (
        Session(
            "s1",
            "v1",
            "2025-09-23T13:53:00",
            SpotStatus.OCCUPIED,
            "spot_1",
            "2025-09-23T13:58:00",
            "tariff_1",
            SessionStatus.CLOSED,
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


#   Тесты показывают, что имея кортеж сессий, мы можем понять,
#   есть ли сессия на транспорт


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


##########################
# ---Основные функции--- #
##########################

#   Открытие сессии на споте, на котором
#   уже открыта сессия. Тест показывает,
#   что открыть данную сессию невозможно.


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

    assert is_tuple_data_same(
        open_session(
            (s1, s2),
            "v3",
            "spot_1",
            SpotStatus.AVAILABLE,
            "2025-09-23T13:55:00",
            "s3",
            "tariff_2",
        ),
        (
            s1,
            s2,
        ),
    )


#   Открытие сессии на споте, сессия на котором была,
#   но уже закрыта + на одном и том же транспорте, что
#   и напредыдущей сессии. Сессия должна открыться.


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
        "v2",
        "spot_2",
        SpotStatus.AVAILABLE,
        "2025-09-23T13:55:00",
        "s3",
        "tariff_2",
    )

    assert is_tuple_data_same(
        result,
        (
            s1,
            s2,
            Session(
                "s3",
                "v2",
                "2025-09-23T13:55:00",
                SpotStatus.AVAILABLE,
                "spot_2",
                None,
                "tariff_2",
                SessionStatus.ACTIVE,
            ),
        ),
    )


#   Транспорт хочет открыть вторую активную сессию.
#   Тест показывает, что на транспорт должно быть
#   не больше одной активной сессии в одно время


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

    assert is_tuple_data_same(
        open_session(
            (s1, s2),
            "v1",
            "spot_3",
            SpotStatus.AVAILABLE,
            "2025-09-13T13:55:00",
            None,
            "tariff_2",
        ),
        (s1, s2),
    )


############################
# ---ИСПОЛЬЗУЕТСЯ map()--- #
############################

#   Закрытие активной сессии.
#   Статус сессии должен измениться на CLOSED,
#   конец сессии меняется с None на заданное время


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

    assert is_tuple_data_same(
        close_session(
            (a, b),
            "session_1",
            "2025-09-13T11:05:00",
        ),
        (
            Session(
                "session_1",
                "v1",
                "2025-09-13T10:55:00",
                SpotStatus.AVAILABLE,
                "spot_1",
                "2025-09-13T11:05:00",
                "tariff_1",
                SessionStatus.CLOSED,
            ),
            b,
        ),
    )


#   Закрытие уже закрытой сессии
#   Время конца сессии не должно измениться


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

    assert is_tuple_data_same(
        close_session(
            (a, b),
            "session_1",
            "2025-09-13T11:05:00",
        ),
        (
            a,
            b,
        ),
    )


###############################
# ---ИСПОЛЬЗУЕТСЯ reduce()--- #
###############################

#   Подсчёт общей суммы дохода.
#   Функция должна сложить значения amount
#   во всех объектах Payment.


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


###############################
# ---ИСПОЛЬЗУЕТСЯ filter()--- #
###############################

#   Отфильтровывание активных сессий
#   Функция должна вернуть кортеж
#   активных сессий.


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

    assert is_tuple_data_same(active_sessions((s1, s2, s3, s4, s5)), (s2, s3, s5))
