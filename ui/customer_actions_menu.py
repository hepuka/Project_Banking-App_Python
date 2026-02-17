from services.account_service import AccountService
from ui.base_menu import BaseMenu
from services.helper_service import Helpers
from config.database import costs_collection, interest_collection
from repositories.customer_repository import CustomerRepository
from models.transaction import Transaction
from repositories.account_repository import AccountRepository
from ui.personal_loan_menu import PersonalLoanMenu


class CustomerActionsMenu(BaseMenu):

    def __init__(self, bank):
        super().__init__(bank)

    @property
    def customer(self):
            return self.bank.current_customer

    def show(self):
        print(f"Ügyfél neve: {self.customer.name}")

        menu = {
            "1": ("Ügyféladatok", self.show_customer_details),
            "2": ("Számlaadatok", self.show_account_details),
            "3": ("Tranzakciók listája", self.get_transactions),
            "4": ("Befizetés", self.deposit),
            "5": ("Kifizetés", self.withdraw),
            "6": ("Utalás bankszámlára", self.transfer),
            "7": ("Számlahitel", self.get_account_loan),
            "8": ("Személyi kölcsön", self.personal_loan_menu),
            "9": ("Vissza a főmenübe", self.back_to_main_menu),
            "0": ("Kilépés", self.exit_app)
        }

        self.run(menu, "Ügyfélkezelés")

    def show_customer_details(self):

        if not self.customer:
            print("Nincs kiválasztott ügyfél!")
            return

        print("\n--- Ügyféladatok ---")
        print(f"Név: {self.customer.name}")
        print(f"Email: {self.customer.email}")
        print(f"Anyja neve: {self.customer.mothers_maiden_name}")
        print(f"Személyi igazolvány száma: {self.customer.personal_id_card_number}")
        print(f"Irányítószám: {self.customer.address['post_code']}")
        print(f"Település: {self.customer.address['city']}")
        print(f"Utca: {self.customer.address['street']}")
        print(f"Házszám: {self.customer.address['house_number']}")
        print(f"Emelet: {self.customer.address['floor']}")
        print(f"Ajtó: {self.customer.address['door_number']}")

    def show_account_details(self):

        if not self.customer:
            print("Nincs kiválasztott ügyfél!")
            return

        account = AccountRepository.find_by_customer_id(self.customer.id)

        if not account:
            print("Ehhez az ügyfélhez nem tartozik számla!")
            return

        print("\n--- Számlaadatok ---")
        print(f"Számlaszám: {account.account_number}")
        print(f"Számlaegyenleg: {Helpers.format_amount(account.balance)} Ft")
        print(f"Számlahitel: {Helpers.format_amount(account.loan_amount)} Ft")
        print(f"Személyi kölcsön: {Helpers.format_amount(account.personal_loan_amount)} Ft")

    def get_transactions(self):
        account = AccountRepository.find_by_customer_id(self.customer.id)

        if not account.transactions:
            print("\nNincs tranzakció!")
            return

        print("\nTRANZAKCIÓK")
        print(
            f"{'Dátum'.ljust(20)} | "
            f"{'Típus'.ljust(20)} | "
            f"{'Név'.ljust(20)} | "
            f"{'Számlaszám'.ljust(30)} | "
            f"{'Összeg'}"
        )

        for t in account.transactions:
            print(
                f"{t.timestamp.ljust(20)} | "
                f"{t.type.ljust(20)} | "
                f"{t.name.ljust(20)} | "
                f"{t.account_number.ljust(30)} | "
                f"{t.formatted_amount()} Ft"
            )

    def deposit(self):
        try:
            c = self.customer
            account = AccountRepository.find_by_customer_id(self.customer.id)

            if not c:
                print("Nincs kiválasztott ügyfél!")
                return

            rows = [
                ("Név", c.name),
                ("Számlaegyenleg", f"{Helpers.format_amount(account.balance)} Ft"),
            ]

            Helpers.print_table("BEFIZETÉS", rows)

            tmp = input("\nBefizetendő összeg: ").strip()

            if not tmp.isdigit():
                raise ValueError("Kérlek, csak pozitív számot adj meg!")

            amount = int(tmp)

            rows = [
                ("Név", c.name),
                ("Jelenlegi számlaegyenleg", f"{Helpers.format_amount(account.balance)} Ft"),
                ("Befizetendő összeg", f"{Helpers.format_amount(amount)} Ft"),
            ]

            Helpers.print_table("BEFIZETÉS MEGERŐSÍTÉS", rows)

            confirm = input("\nBiztosan végrehajtod? (i/n): ").lower()

            if confirm != "i":
                print("Művelet megszakítva.")
                return

            AccountService.deposit(c, account, amount)
            print("\nSikeres befizetés!")

        except ValueError as e:
            print(e)

    def withdraw(self):
        #UI → CustomerService → Customer (model) → Repository → DB
        try:
            c = self.customer
            cost = self.get_cost("withdraw")
            account = AccountRepository.find_by_customer_id(self.customer.id)


            if not c:
                print("Nincs kiválasztott ügyfél!")
                return

            rows = [
                ("Név", c.name),
                ("Számlaegyenleg", f"{Helpers.format_amount(account.balance)} Ft"),
                ("Számlahitel", f"{Helpers.format_amount(account.loan_amount)} Ft"),
            ]

            Helpers.print_table("KIFIZETÉS", rows)

            tmp = input("\nKifizetendő összeg: ").strip()

            if not tmp.isdigit():
                raise ValueError("Kérlek, pozitív egész számot adj meg!")

            amount = int(tmp)

            if amount > account.balance + account.loan_amount:
                raise ValueError("Nincs elegendő fedezet!")

            rows = [
                ("Név", c.name),
                ("Jelenlegi számlaegyenleg", f"{Helpers.format_amount(account.balance)} Ft"),
                ("Számlahitel", f"{Helpers.format_amount(account.loan_amount)} Ft"),
                ("Kifizetendő összeg", f"{Helpers.format_amount(amount)} Ft"),
            ]

            Helpers.print_table("KIFIZETÉS MEGERŐSÍTÉS", rows)

            confirm = input("\nBiztosan végrehajtod? (i/n): ").lower()
            if confirm != "i":
                print("Művelet megszakítva.")
                return

            # Service hívás
            AccountService.withdraw(c,account, amount, cost)

            print("\nSikeres kifizetés!")

        except ValueError as e:
            print(f"Hiba: {e}")

    def transfer(self):
        try:
            source = self.customer
            cost = self.get_cost("transaction")
            source_account = AccountRepository.find_by_customer_id(self.customer.id)

            if not source:
                print("Nincs kiválasztott ügyfél!")
                return

            target_account_tmp = input("Célszámlaszám: ").strip()
            target_account = AccountRepository.find_by_account_number(target_account_tmp)
            target_customer = CustomerRepository.find_by_id(target_account.customer_id)

            if not target_account:
                raise ValueError("Nem található ilyen számla!")

            print(f"Célszámlatulajdonos: {target_customer.name}")
            tmp = input("Utalandó összeg: ").strip()

            if not tmp.isdigit():
                raise ValueError("Kérlek, pozitív egész számot adj meg!")

            amount = int(tmp)

            if amount > source_account.balance:
                raise ValueError("Nincs elegendő fedezet!")

            rows = [
                ("Küldő fél", source.name),
                ("Fogadó fél", target_customer.name),
                ("Utalandó összeg", f"{Helpers.format_amount(amount)} Ft"),

            ]

            Helpers.print_table("UTALÁS MEGERŐSÍTÉS", rows)

            confirm = input("\nBiztosan végrehajtod? (i/n): ").lower()
            if confirm != "i":
                print("Művelet megszakítva.")
                return

            # Service hívás
            AccountService.transfer(
                self.customer,
                source_account,
                target_account,
                amount,
                cost
            )

            print("\nSikeres utalás!")

        except ValueError as e:
            print(f"Hiba: {e}")

    def get_account_loan(self):
        try:
            c = self.customer
            account = AccountRepository.find_by_customer_id(self.customer.id)

            if not c:
                print("Nincs kiválasztott ügyfél!")
                return

            rows = [
                ("Név", c.name),
                ("Számlaegyenleg", f"{Helpers.format_amount(account.balance)} Ft"),
            ]

            if account.loan_amount != 0:
                print("Már van aktív számlahitel, új hitel nem igényelhető!")
                return

            # A hitel összege a jelenlegi egyenleg 1.5-szöröse
            proposed_loan = int(account.balance * 1.5)

            Helpers.print_table("Számlahiteligénylés", rows)

            confirm = input(f"Szeretnéd igényelni a {Helpers.format_amount(proposed_loan)} Ft hitelt? (i/n): ").lower()
            if confirm != "i":
                print("Művelet megszakítva.")
                return

            # Hitel igénylés és tranzakció rögzítése
            account.loan_amount = proposed_loan
            account.transactions.append(
                    Transaction(c.name, account.account_number, "Számlahitel igénylés", proposed_loan)
                )

            # Mentés adatbázisba
            AccountRepository.save(account)

            print(f"Sikeres számlahitel igénylés! Új hitel: {Helpers.format_amount(account.loan_amount)} Ft")


        except ValueError as e:
            print(e)

    def personal_loan_menu(self):

        PersonalLoanMenu(self.bank).show()

    def back_to_main_menu(self):
        # aktuális ügyfél törlése
        self.bank.current_customer = None

        # visszalépés a CustomerMenu-be
        # lazy import – csak akkor importál, amikor lefut
        from ui.customer_menu import CustomerMenu
        CustomerMenu(self.bank).show()

    @staticmethod
    def get_cost(cost_type):
        cost_doc = costs_collection.find_one({"name": cost_type})
        cost = cost_doc["value"]
        return cost

    @staticmethod
    def get_interest(interest_type):
        interest_doc = interest_collection.find_one({"name": interest_type})
        interest = interest_doc["value"]
        return interest