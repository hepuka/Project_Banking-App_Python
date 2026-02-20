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
        current_customer = self.bank.current_customer

        accounts = AccountRepository.find_by_customer_id(current_customer.id)

        if not accounts:
            print("Ehhez az ügyfélhez nem tartozik számla!")
            return

        hun_accounts = [acc for acc in accounts if acc.account_type == "HUN"]

        if not hun_accounts:
            print("Személyi kölcsön csak HUN számlán igényelhető!")
            return

        print("\nHUN számlák:\n")

        for i, acc in enumerate(hun_accounts, start=1):
            print(f"{i}. {acc.account_number} | "
                  f"Egyenleg: {Helpers.format_amount(acc.balance)} Ft | "
                  f"Személyi hitel: {Helpers.format_amount(acc.personal_loan_amount)} Ft")

        try:
            choice = int(input("\nMelyik számlára igényled? (sorszám): "))

            if choice < 1 or choice > len(hun_accounts):
                raise ValueError("Érvénytelen választás!")

            account = hun_accounts[choice - 1]

            if account.personal_loan_amount != 0:
                print("Ezen a számlán már van személyi hitel!")
                return

            amount = int(input("Kölcsön összege: "))

            account.request_personal_loan(current_customer.id, amount)

            AccountRepository.save(account)

            print(f"\nSikeres hiteligénylés!")
            print(f"Új személyi hitel: {Helpers.format_amount(account.personal_loan_amount)} Ft")

        except ValueError as ve:
            print(f"Hiba: {ve}")

    def repay_personal_loan(self):
        current_customer = self.bank.current_customer

        accounts = AccountRepository.find_by_customer_id(current_customer.id)

        if not accounts:
            print("Ehhez az ügyfélhez nem tartozik számla!")
            return

        loan_accounts = [
            acc for acc in accounts
            if acc.account_type == "HUN" and acc.personal_loan_amount > 0
        ]

        if not loan_accounts:
            print("Nincs törleszthető személyi hitel.")
            return

        print("\nHitelek:\n")

        for i, acc in enumerate(loan_accounts, start=1):
            print(f"{i}. {acc.account_number} | "
                  f"Hátralévő hitel: {Helpers.format_amount(acc.personal_loan_amount)} Ft")

        try:
            choice = int(input("\nMelyik számlán szeretnél törleszteni? (sorszám): "))

            if choice < 1 or choice > len(loan_accounts):
                raise ValueError("Érvénytelen választás!")

            account = loan_accounts[choice - 1]

            amount = int(input(f"Törlesztendő összeg (max {account.personal_loan_amount} Ft): "))

            account.repay_personal_loan(amount)

            AccountRepository.save(account)

            print(f"\nSikeres törlesztés!")
            print(f"Hátralévő hitel: {Helpers.format_amount(account.personal_loan_amount)} Ft")

        except ValueError as ve:
            print(f"Hiba: {ve}")

    def back_to_customer_actions_menu(self):
        from ui.customer_actions_menu import CustomerActionsMenu
        CustomerActionsMenu(self.bank).show()
