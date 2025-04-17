import datetime
from typing import Optional

import pandas as pd

from logger.logger_config import logger
from src.utils import get_operations_data

transactions = get_operations_data()


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Фильтрует траты по категории за последние 3 месяца. Возвращает DataFrame с результатами или сообщением об ошибке."""
    logger.info('ЗАПУСК ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')

    try:
        # Проверка на пустой DataFrame
        if transactions.empty:
            logger.warning("Передан пустой DataFrame! Нет данных для анализа.")
            logger.info('ЗАВЕРШЕНИЕ ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')
            return pd.DataFrame({"Сообщение": ["Нет данных для анализа"]})

        # Проверка наличия колонок
        required_columns = ["Дата платежа", "Категория"]
        if not all(col in transactions.columns for col in required_columns):
            missing = [col for col in required_columns if col not in transactions.columns]
            logger.error(f"Не хватает колонок: {missing}")
            logger.info('ЗАВЕРШЕНИЕ ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')

            return pd.DataFrame({"Ошибка": [f"В данных отсутствуют колонки: {', '.join(missing)}"]})

        # Преобразование даты
        transactions["Дата платежа"] = pd.to_datetime(
            transactions["Дата платежа"], format="%d.%m.%Y", errors="coerce"
        ).dt.date

        # Установка диапазона дат
        end_date = datetime.date.today() if date is None else datetime.datetime.strptime(date, "%d.%m.%Y").date()
        start_date = end_date - datetime.timedelta(days=90)

        # Фильтрация
        mask = (
            (transactions["Категория"].str.lower() == category.lower())
            & (transactions["Дата платежа"] >= start_date)
            & (transactions["Дата платежа"] <= end_date)
        )
        filtered_data = transactions[mask]

        # Проверка результата
        if filtered_data.empty:
            logger.info(f"Нет данных по категории '{category}' за период с {start_date} по {end_date}.")
            logger.info('ЗАВЕРШЕНИЕ ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')

            return pd.DataFrame({"Информация": [f"Нет трат по категории '{category}' за указанный период"]})

        logger.info(f"Найдено {len(filtered_data)} записей.")
        logger.info('ЗАВЕРШЕНИЕ ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')

        return filtered_data

    except Exception as ex:
        logger.error(f"Ошибка: {ex}", exc_info=True)
        logger.info('ЗАВЕРШЕНИЕ ОТЧЕТА "ТРАТЫ ПО КАТЕГОРИИ"')

        return pd.DataFrame({"Ошибка": [f"Произошла ошибка: {str(ex)}"]})
