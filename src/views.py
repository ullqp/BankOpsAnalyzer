import json

import pandas as pd

from logger.logger_config import logger
from src.utils import (
    get_current_date_time,
    get_exchange_rate,
    get_operations_data,
    get_operations_data_current,
    get_say_hello,
    get_statistics,
    get_stock_prices,
    get_top_operations,
    get_user_settings,
)


def main_menu() -> pd.DataFrame:
    logger.info("ЗАПУСК ГЛАВНОГО МЕНЮ.")
    current_date = get_current_date_time()
    user_settings = get_user_settings()
    operations_data = get_operations_data()
    operations_data_current = get_operations_data_current(operations_data, current_date)
    card_statistics = get_statistics(operations_data_current)
    top_operations = get_top_operations(operations_data_current)
    currency_rates = get_exchange_rate(user_settings)
    stock_prices = get_stock_prices(user_settings)
    say_hello = get_say_hello(current_date)

    transactions = pd.DataFrame(operations_data)

    main_text: dict = {
        "greeting": say_hello,
        "cards": card_statistics,
        "top_transactions": top_operations,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    main_text_json = json.dumps(main_text, indent=4, ensure_ascii=False)
    print(main_text_json)
    logger.info("ЗАВЕРШЕНИЕ ГЛАВНОГО МЕНЮ.")

    return transactions
