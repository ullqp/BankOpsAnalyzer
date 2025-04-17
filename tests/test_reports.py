import unittest
from unittest.mock import patch

import pandas as pd

from src.reports import spending_by_category  # Замените на реальный импорт


class TestSpendingByCategory(unittest.TestCase):

    def setUp(self):
        # Тестовые данные
        self.test_data = pd.DataFrame(
            {
                "Дата платежа": ["01.05.2024", "15.05.2024", "20.04.2024"],
                "Категория": ["Еда", "Еда", "Транспорт"],
                "Сумма": [1000, 500, 300],
            }
        )

    @patch("src.reports.logger")  # Мокаем логгер
    def test_successful_filtering(self, mock_logger):
        """Тест успешной фильтрации данных"""
        # Вызываем функцию с тестовыми данными
        result = spending_by_category(transactions=self.test_data, category="Еда", date="15.05.2024")

        # Проверяем результат
        self.assertEqual(len(result), 2)  # Должно найти 2 записи
        self.assertTrue(all(result["Категория"] == "Еда"))

        # Проверяем, что логи вызывались
        mock_logger.info.assert_any_call('ЗАПУСК ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')
        mock_logger.info.assert_any_call('ЗАВЕРШЕНИЕ ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')

    @patch("src.reports.logger")
    @patch("src.reports.pd.to_datetime")
    def test_error_handling(self, mock_to_datetime, mock_logger):
        """Тест обработки ошибки при преобразовании даты"""
        # Настраиваем мок для вызова ошибки
        mock_to_datetime.side_effect = ValueError("Invalid date format")

        # Вызываем функцию с невалидными данными
        result = spending_by_category(transactions=self.test_data, category="Еда", date="invalid_date")

        # Проверяем результат
        self.assertTrue("Ошибка" in result.columns)
        self.assertIn("Invalid date format", result.iloc[0]["Ошибка"])

        # Проверяем логирование ошибки
        mock_logger.error.assert_called()
        mock_logger.info.assert_any_call('ЗАВЕРШЕНИЕ ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')


if __name__ == "__main__":
    unittest.main()
