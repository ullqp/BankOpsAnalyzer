import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from src.utils import (
    get_current_date_time,
    get_exchange_rate,
    get_operations_data,
    get_operations_data_current,
    get_say_hello,
    get_statistics,
    get_stock_prices,
    get_user_settings,
)


class TestUtils(unittest.TestCase):
    @patch("pandas.read_excel")
    def test_get_operations_data(self, mock_read_excel: MagicMock) -> None:
        """Тестирование функции get_operations_data.

        Проверяет корректность чтения и преобразования данных из Excel.
        """
        mock_read_excel.return_value = pd.DataFrame(
            [
                {
                    "date": "05.02.2019",
                    "amount": 22500.0,
                    "category": "Пополнения",
                    "description": "Пополнение. Тинькофф Банк, 2028 Санкт-Петербург Россия",
                },
                {
                    "date": "05.02.2019",
                    "amount": 500.0,
                    "category": "Бонусы",
                    "description": 'Пополнение. Тинькофф Банк. Бонус по акции "Приведи друга"',
                },
            ]
        )
        result = get_operations_data()
        expected_result = [
            {
                "date": "05.02.2019",
                "amount": 22500.0,
                "category": "Пополнения",
                "description": "Пополнение. Тинькофф Банк, 2028 Санкт-Петербург Россия",
            },
            {
                "date": "05.02.2019",
                "amount": 500.0,
                "category": "Бонусы",
                "description": 'Пополнение. Тинькофф Банк. Бонус по акции "Приведи друга"',
            },
        ]
        self.assertEqual(result, expected_result)


@patch("json.load")
@patch("builtins.open")
def test_get_user_settings(mock_open: MagicMock, mock_load: MagicMock) -> None:
    """Тестирование функции get_user_settings.

    Проверяет корректность чтения пользовательских настроек из файла.
    """
    mock_load.return_value = {
        "user_currencies": ["USD", "EUR"],
        "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"],
    }
    mock_open.return_value.__enter__.return_value = None

    result = get_user_settings()

    assert result == mock_load.return_value
    mock_load.assert_called_once()


def test_get_current_date_time() -> None:
    """Тестирование функции get_current_date_time.

    Проверяет корректность форматирования текущей даты и времени.
    """
    with freeze_time("2019-04-14 19:05:01"):
        result = get_current_date_time()
        assert result == "2019-04-14 19:05:01"


def test_get_operations_data_current(operations: List[Dict[str, Any]], current_date: str) -> None:
    """Тестирование функции get_operations_data_current.

    Проверяет фильтрацию операций по текущей дате.
    """
    result = get_operations_data_current(operations, current_date)
    assert result == [
        {
            "Дата операции": "13.07.2019 00:00:00",
            "Дата платежа": "16.07.2019",
            "Номер карты": "*7195",
            "Статус": "OK",
            "Сумма операции": 189.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 189.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": 1.89,
            "Категория": "Бонусы",
            "MCC": 4121.0,
            "Описание": "Вознаграждение за операции покупок",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 189.0,
        },
        {
            "Дата операции": "02.07.2019 00:00:00",
            "Дата платежа": "16.07.2019",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": 258.3,
            "Валюта операции": "RUB",
            "Сумма платежа": 258.3,
            "Валюта платежа": "RUB",
            "Кэшбэк": 2.58,
            "Категория": "Бонусы",
            "MCC": 4121.0,
            "Описание": "Проценты на остаток по счету",
            "Бонусы (включая кэшбэк)": 0,
            "Округление на инвесткопилку": 0,
            "Сумма операции с округлением": 258.3,
        },
    ]


def test_get_statistics(operations: List[Dict[str, Any]]) -> None:
    """Тестирование функции get_statistics.

    Проверяет корректность расчета статистики по операциям.
    """
    result = get_statistics(operations)
    assert result == [
        {"last_digits": "*7197", "total_spent": 406.3, "cashback": 4.06},
        {"last_digits": "*7195", "total_spent": 189.0, "cashback": 1.89},
    ]


@patch("requests.request")
def test_get_exchange_rate(mock_request: MagicMock, user_settings: Dict[str, List[str]]) -> None:
    """Тестирование функции get_exchange_rate.

    Проверяет корректность получения курсов валют от API.
    """
    # Настраиваем моки для последовательных вызовов
    mock_responses = [{"rate": 82.23}, {"rate": 93.282}]  # Для первого вызова (USD)  # Для второго вызова (EUR)

    # Создаем мок-ответы
    mock_request.side_effect = [
        type("MockResponse", (), {"json": lambda: mock_responses[0], "status_code": 200}),
        type("MockResponse", (), {"json": lambda: mock_responses[1], "status_code": 200}),
    ]

    result = get_exchange_rate(user_settings)

    # Проверяем результат
    assert result == [{"USD": 82.23}, {"EUR": 93.282}]

    # Проверяем количество вызовов
    assert mock_request.call_count == 2


@patch("requests.request")
def test_get_stock_prices_success(mock_request: MagicMock) -> None:
    """Тестирование функции get_stock_prices.

    Проверяет корректность получения цен акций от API.
    """
    # Подготовка тестовых данных
    user_settings = {"user_stocks": ["AAPL", "GOOGL"]}

    # Мок ответа API
    mock_response = {"AAPL": {"price": "175.34"}, "GOOGL": {"price": "135.22"}}

    # Настройка мока
    mock_request.return_value.json.return_value = mock_response

    # Вызов функции
    result = get_stock_prices(user_settings)

    # Проверки
    assert result == [{"stock": "AAPL", "price": 175.34}, {"stock": "GOOGL", "price": 135.22}]
    mock_request.assert_called_once()


@pytest.mark.parametrize(
    "current_date, expected_result",
    [
        ("2019-07-14 19:05:01", "Добрый вечер"),
        ("2020-11-12 07:05:01", "Доброе утро"),
        ("2020-11-12 15:05:01", "Добрый день"),
        ("2020-04-12 04:05:01", "Доброй ночи"),
    ],
)
def test_get_say_hello(current_date: str, expected_result: str) -> None:
    """Параметризованный тест функции get_say_hello.

    Проверяет корректность приветствия в зависимости от времени суток.
    """
    assert get_say_hello(current_date) == expected_result


if __name__ == "__main__":
    unittest.main()
