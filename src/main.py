from src.reports import spending_by_category
from src.services import simple_search
from src.utils import get_current_date_time, get_operations_data
from src.views import main_menu

# import datetime
# current_date = datetime.datetime(2018, 2, 26, 21, 10, 1)
# current_date_str = current_date.strftime("%Y-%m-%d %H:%M:%S")
operations_data = get_operations_data()
current_date_str = get_current_date_time()
search_str = "бонусы"

transactions = main_menu(current_date_str)
print(simple_search(search_str, operations_data))
print(spending_by_category(transactions, "Переводы", "01.03.2019"))
