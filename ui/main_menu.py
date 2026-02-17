from ui.admin_menu import AdminMenu
from ui.customer_menu import CustomerMenu

class MainMenu:
    def __init__(self, bank):
        self.bank = bank

    def show(self):
        
        current_user = self.bank.current_user

        if current_user["role"] == "user":
             CustomerMenu(self.bank).show()
        else:
            AdminMenu(self.bank).show()
