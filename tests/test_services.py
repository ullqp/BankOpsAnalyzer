import json
from typing import Any, Dict, List
from unittest.mock import call, patch

import pytest

from src.services import simple_search


def test_simple_search(operations: List[Dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
    """Тест успешного поиска операций"""

    # Мок ввода пользователя
    def mock_input(prompt: str) -> str:
        return "транспорт"

    monkeypatch.setattr("builtins.input", mock_input)

    with patch("src.services.logger") as mock_logger:
        # Вызываем функцию с аргументами
        result_json: str = simple_search(search_str="транспорт", operations_data=operations)
        result: List[Dict[str, Any]] = json.loads(result_json)

        assert len(result) == 1
        assert all("транспорт" in op["Категория"].lower() for op in result)

        # Проверяем все логинги по порядку
        expected_calls = [
            call('ЗАПУСК СЕРВИСА "ПРОСТОЙ ПОИСК"'),
            call("Операции отфильтрованы по введенному слову."),
            call('ЗАВЕРШЕНИЕ СЕРВИСА "ПРОСТОЙ ПОИСК"'),
        ]
        mock_logger.info.assert_has_calls(expected_calls, any_order=False)


def test_simple_search_no_results(operations: List[Dict[str, Any]], monkeypatch: pytest.MonkeyPatch) -> None:
    """Тест случая, когда операции не найдены"""

    monkeypatch.setattr("builtins.input", lambda _: "кредит")

    with patch("src.services.logger") as mock_logger:
        # Вызываем функцию с аргументами
        result_json: str = simple_search(search_str="кредит", operations_data=operations)
        result: List[Dict[str, Any]] = json.loads(result_json)

        assert len(result) == 0

        # Проверяем все логи, как в оригинальной функции
        expected_calls = [
            call('ЗАПУСК СЕРВИСА "ПРОСТОЙ ПОИСК"'),
            call("Операции отфильтрованы по введенному слову."),
            call('ЗАВЕРШЕНИЕ СЕРВИСА "ПРОСТОЙ ПОИСК"'),
        ]
        mock_logger.info.assert_has_calls(expected_calls, any_order=False)
