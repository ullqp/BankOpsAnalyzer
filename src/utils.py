import datetime
import heapq
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd
import requests
from dotenv import load_dotenv

from logger.logger_config import logger


# Путь к файлу operations.xlsx относительно src/utils.py
def get_operations_data() -> list[dict]:
    """Функция, которая возвращает данные из excel-файла."""
    operations_data: list = []
    try:
        current_dir = os.path.dirname(__file__)  # Директория src/
        project_root = os.path.dirname(current_dir)  # Поднимаемся в корень проекта
        file_path = os.path.join(project_root, "data", "operations.xlsx")

        excel_data = pd.read_excel(file_path)
        operations_data = excel_data.to_dict(orient="records")
        logger.info("Данные из exel-файла успешно получены.")
    except Exception as ex:
        logger.error(f"Ошибка в функции get_operations_data: {str(ex)}", exc_info=True)
    return operations_data


def get_user_settings() -> Optional[Dict[str, Any]]:
    """Функция, которая возвращает пользовательские настройки из json-файла."""

    project_root = Path(__file__).parent.parent  # Поднимаемся на два уровня вверх из src/
    settings_path = project_root / "user_settings.json"

    try:
        # Читаем и загружаем JSON файл
        with open(settings_path, "r", encoding="utf-8") as f:
            user_settings: Dict[str, Any] = json.load(f)
            logger.info("Настройки пользователя из json-файла успешно получены.")
            return user_settings
    except Exception as ex:
        logger.error(f"Ошибка в функции get_user_settings: {str(ex)}", exc_info=True)
        return None


def get_current_date_time() -> str:
    """Функция, которая возвращает текущее время."""
    current_date = datetime.datetime.now()
    current_date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Текущее время: {current_date_str} успешно получено.")
    return current_date_str


def get_operations_data_current(operations_data: list, current_date: str) -> list:
    """Функция, которая фильтрует операции за текущий месяц."""

    operations_data_period: list = []
    try:
        current_date_parsed = datetime.datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S")
    except Exception:
        logger.error("Ошибка в функции get_user_settings: Некорректный формат current_date!")
        return operations_data_period  # Возвращаем пустой список, если дата не распарсилась

    for operation in operations_data:
        try:
            operation_date_str = operation.get("Дата операции")
            if not operation_date_str:  # Пропускаем, если нет даты
                continue

            operation_date = datetime.datetime.strptime(operation_date_str, "%d.%m.%Y %H:%M:%S")

            # Сравниваем уже распарсенные даты
            if (
                operation_date.year == current_date_parsed.year
                and operation_date.month == current_date_parsed.month
                and operation_date <= current_date_parsed
            ):
                operations_data_period.append(operation)
        except Exception:
            continue

    logger.info(f"Операции за текущий месяц отфильтрованы. Найдено: {len(operations_data_period)}")
    return operations_data_period


def get_statistics(operations_data_current: list) -> list:
    """Функция, которая возвращает статистику по операциям за текущий месяц."""
    cards: list = []

    for operation in operations_data_current:
        last_digits = operation.get("Номер карты")

        if isinstance(last_digits, float) and math.isnan(last_digits):
            continue

        if last_digits is None or (isinstance(last_digits, str) and last_digits.strip() == ""):
            continue

        if not any(card["last_digits"] == last_digits for card in cards):

            spent = abs(float(operation.get("Сумма платежа")))
            cards.append({"last_digits": last_digits, "total_spent": spent})

        else:
            for card in cards:
                if card["last_digits"] == last_digits:

                    spent = abs(float(operation.get("Сумма платежа")))
                    card["total_spent"] += spent

        for card in cards:
            card["cashback"] = round(card["total_spent"] * 0.01, 2)
    logger.info("Статистика по операциям за текущий месяц успешно получена.")
    return cards


def get_top_operations(operations_data_current: list) -> list:
    """Функция, которая возвращает топ-5 операций по сумме платежа за текущий месяц."""
    top_operations = []
    top_five = heapq.nlargest(5, operations_data_current, key=lambda x: x["Сумма платежа"])

    for operation in top_five:
        date = operation.get("Дата платежа", "")
        amount = abs(float(operation.get("Сумма платежа", "")))
        category = operation.get("Категория", "")
        description = operation.get("Описание", "")

        top_operations.append(
            {
                "date": date,
                "amount": amount,
                "category": category,
                "description": description,
            }
        )
    logger.info("Топ-5 операций по сумме платежа успешно отфильтрованы.")
    return top_operations


def get_exchange_rate(user_settings: dict | None) -> list:
    """Функция, которая возвращает курс валют, выбранных пользователем."""
    if user_settings is None:
        return []
    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    headers = {"apikey": API_KEY}

    currency_rates = []

    user_currencies = user_settings["user_currencies"]
    for currency in user_currencies:
        url = f"https://api.twelvedata.com/exchange_rate?symbol={currency}/RUB&apikey={API_KEY}"
        try:
            response = requests.request("GET", url, headers=headers)
            rate = response.json()["rate"]
            currency_rates.append({currency: rate})
            logger.info("Курс валют успешно получен.")
        except Exception as ex:
            logger.error(f"Ошибка в функции get_exchange_rate: {str(ex)}", exc_info=True)

    return currency_rates


def get_stock_prices(user_setting: dict | None) -> list:
    """Функция, которая возвращает стоимости акций, выбранных пользователем."""
    if user_setting is None:
        return []
    load_dotenv()

    API_KEY = os.getenv("API_KEY")
    headers = {"apikey": API_KEY}
    tickers = user_setting["user_stocks"]
    stock_prices = []

    url = f"https://api.twelvedata.com/price?symbol={','.join(tickers)}&apikey={API_KEY}"
    try:
        response = requests.request("GET", url, headers=headers)
        tickers_prices = response.json()

    except Exception:
        tickers_prices = {0}
    try:
        for ticker in tickers_prices:
            stock_prices.append(
                {
                    "stock": ticker,
                    "price": round(float(tickers_prices[ticker]["price"]), 2),
                }
            )
        logger.info("Стоимости акций успешно получены.")
    except Exception as ex:
        logger.error(f"Ошибка в функции get_stock_prices: {str(ex)}", exc_info=True)

    return stock_prices


def get_say_hello(current_date_str: str) -> str:
    """Функция, которая возвращает приветствие в зависимости от времени суток."""
    current_date = datetime.datetime.strptime(current_date_str, "%Y-%m-%d %H:%M:%S")
    hour = current_date.hour
    logger.info("Приветствие успешно получено.")
    if 6 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    if 18 <= hour < 24:
        return "Добрый вечер"
    return "Доброй ночи"
