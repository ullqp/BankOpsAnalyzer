# BankOpsAnalyzer
Bank Operations Analyzer

## Описание:

Проект "Bank Operations Analyzer" - Приложение для анализа банковских операций. 
В проекте реализовано логирование, что позволяет отслеживать события и ошибки в процессе работы приложения.


## Установка:

Клонируйте репозиторий:
```
git clone https://github.com/ullqp/BankOpsAnalyzer.git
```

## Использование:

Примеры использования src/main.py:

```python
from src.views import main_menu
from src.services import simple_search
from src.reports import spending_by_category

# Пример использования main_menu
transactions = main_menu()

# Пример использования simple_search
print(simple_search())

# Пример использования spending_by_category
print(spending_by_category(transactions, "Переводы", "01.03.2019"))
```

### Тестирование

Для тестирования проекта используется библиотека `pytest`. Чтобы запустить тесты, выполните команду:

```bash
pytest
```

Тесты покрывают следующие модули и функции:
- `utils`: функции `get_current_date_time`,
    `get_exchange_rate`,
    `get_operations_data`,
    `get_operations_data_current`,
    `get_say_hello`,
    `get_statistics`,
    `get_stock_prices`,
    `get_user_settings`.
- `reports`: функции `spending_by_category`.
- `services`: функции `simple_search`. 
Покрытие тестами составляет более 80% кода проекта.

---