import json
from unittest.mock import call, patch

from src.services import simple_search


def test_simple_search(monkeypatch):
    """Тест успешного поиска операций"""

    # Мок данных
    def mock_get_operations_data():
        return [
            {"Категория": "Пополнения", "Описание": "Пополнение счета"},
            {"Категория": "Платеж", "Описание": "Оплата услуг"},
            {"Категория": "Пополнения", "Описание": "Бонусное пополнение"},
        ]

    # Мок ввода пользователя
    def mock_input(prompt):
        return "пополнение"

    monkeypatch.setattr("src.services.get_operations_data", mock_get_operations_data)
    monkeypatch.setattr("builtins.input", mock_input)

    with patch("src.services.logger") as mock_logger:
        result_json = simple_search()
        result = json.loads(result_json)

        assert len(result) == 2
        assert all("пополн" in op["Категория"].lower() for op in result)

        # Проверяем все логинги по порядку
        expected_calls = [
            call('ЗАПУСК СЕРВИСА "ПРОСТОЙ ПОИСК"'),
            call("Операции отфильтрованы по введенному слову."),
            call('ЗАВЕРШЕНИЕ СЕРВИСА "ПРОСТОЙ ПОИСК"'),
        ]
        mock_logger.info.assert_has_calls(expected_calls, any_order=False)


def test_simple_search_no_results(monkeypatch):
    """Тест случая, когда операции не найдены"""

    def mock_get_operations_data():
        return [{"Категория": "Платеж", "Описание": "Оплата услуг"}]

    monkeypatch.setattr("src.services.get_operations_data", mock_get_operations_data)
    monkeypatch.setattr("builtins.input", lambda _: "кредит")

    with patch("src.services.logger") as mock_logger:
        result_json = simple_search()
        result = json.loads(result_json)

        assert len(result) == 0

        # Проверяем только последнее сообщение
        mock_logger.info.assert_called_with('ЗАВЕРШЕНИЕ СЕРВИСА "ПРОСТОЙ ПОИСК"')
