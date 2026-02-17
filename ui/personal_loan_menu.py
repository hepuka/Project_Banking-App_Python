from repositories.account_repository import AccountRepository
from services.helper_service import Helpers
from ui.base_menu import BaseMenu


class PersonalLoanMenu(BaseMenu):

    def __init__(self, bank):
        super().__init__(bank)

    @property
    def customer(self):
            return self.bank.current_customer

    def show(self):
        menu = {
            "1": ("Kölcsön igénylés", self.request_personal_loan),
            "2": ("Törlesztés", self.repay_personal_loan),
            "0": ("Vissza az ügyfél menübe", self.back_to_customer_actions_menu),
        }

        self.run(menu, "Hitel")


    def request_personal_loan(self):
        current_customer = self.bank.current_customer.id
        account = AccountRepository.find_by_customer_id(current_customer)
        amount = int(input("Kölcsön összege: "))

        if account.request_personal_loan(current_customer, amount):
            AccountRepository.save(account)
            print(f"Sikeres személyi hiteligénylés: {Helpers.format_amount(account.personal_loan_amount)} Ft")

        else:
            print("Az ügyfél már rendelkezik személyi hitellel!")

    def repay_personal_loan(self):
        current_customer_id = self.bank.current_customer.id
        account = AccountRepository.find_by_customer_id(current_customer_id)

        if account.personal_loan_amount == 0:
            print("Az ügyfélnek nincs személyi hitele.")
            return

        try:
            amount = int(input(f"Törlesztendő összeg (max {account.personal_loan_amount} Ft): "))
            account.repay_personal_loan(amount)

            AccountRepository.save(account)
            print(f"Sikeres törlesztés! Hátralévő személyi hitel: {account.personal_loan_amount} Ft")

        except ValueError as ve:
            print(f"Hiba: {ve}")

    def back_to_customer_actions_menu(self):
        from ui.customer_actions_menu import CustomerActionsMenu
        CustomerActionsMenu(self.bank).show()
