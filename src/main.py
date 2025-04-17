from src.reports import spending_by_category
from src.services import simple_search
from src.views import main_menu

transactions = main_menu()

print(simple_search())
print(spending_by_category(transactions, "Переводы", "01.03.2019"))
