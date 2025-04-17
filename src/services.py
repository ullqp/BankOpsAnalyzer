import json

from logger.logger_config import logger
from src.utils import get_operations_data


def simple_search() -> str:
    """Функция, которая фильтрует операции по введенному слову."""
    logger.info('ЗАПУСК СЕРВИСА "ПРОСТОЙ ПОИСК"')
    operations_data = get_operations_data()
    search_str = input("Введите строчку, по которой выполнен будет поиск транзакций.").lower()
    founded_operations: list = []
    for operation in operations_data:
        category = str(operation.get("Категория", "")).lower()
        description = str(operation.get("Описание", "")).lower()

        if search_str in category or search_str in description:
            founded_operations.append(operation)

    founded_operations_json = json.dumps(founded_operations, indent=4, ensure_ascii=False)

    logger.info("Операции отфильтрованы по введенному слову.")
    logger.info('ЗАВЕРШЕНИЕ СЕРВИСА "ПРОСТОЙ ПОИСК"')

    return founded_operations_json
