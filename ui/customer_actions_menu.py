from services.account_service import AccountService
from ui.base_menu import BaseMenu
from services.helper_service import Helpers
from config.database import costs_collection, interest_collection
from repositories.customer_repository import CustomerRepository
from models.transaction import Transaction
from repositories.account_repository import AccountRepository
from ui.personal_loan_menu import PersonalLoanMenu
from services.pdf_service import export_account_statement
from datetime import datetime

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
            "10": ("Számlakivonat készítése", self.export_pdf),
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
        accounts = AccountRepository.find_by_customer_id(self.customer.id)

        if not accounts:
            print("Ehhez az ügyfélhez nem tartozik számla!")
            return

        print("\n--- Számlaadatok ---")

        for acc in accounts:
            currency = "Ft" if acc.account_type == "HUN" else "EUR"

            print(f"Számlaszám: {acc.account_number}")
            print(f"Típus: {acc.account_type}")
            print(f"Egyenleg: {Helpers.format_amount(acc.balance)} {currency}")

            if acc.account_type == "HUN":
                print(f"Számlahitel: {Helpers.format_amount(acc.loan_amount)} {currency}")
                print(f"Személyi kölcsön: {Helpers.format_amount(acc.personal_loan_amount)} {currency}")

            print("------------------------")

    def get_transactions(self):
        accounts = AccountRepository.find_by_customer_id(self.customer.id)

        if not accounts:
            print("\nNincs tranzakció!")
            return

        for i, acc in enumerate(accounts, start=1):
            print(f"{i}. {acc.account_number} | {acc.account_type.upper()}")

        choice = int(input("Melyik számla tranzakcióit szeretnéd látni? "))

        if choice < 1 or choice > len(accounts):
            print("Érvénytelen választás!")
            return

        account = accounts[choice - 1]

        if not account.transactions:
            print("Nincs rögzített tranzakció!")
            return

        currency = "Ft" if account.account_type == "HUN" else "EUR"

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
                f"{t.formatted_amount()} {currency}"
            )

    def deposit(self):
        try:
            c = self.customer

            if not c:
                print("Nincs kiválasztott ügyfél!")
                return

            accounts = AccountRepository.find_by_customer_id(c.id)

            if not accounts:
                print("Ehhez az ügyfélhez nem tartozik számla!")
                return

            print("\nAz ügyfél számlái:\n")

            for i, acc in enumerate(accounts, start=1):
                print(f"{i}. {acc.account_number} | "
                      f"{acc.account_type.upper()} | "
                      f"Egyenleg: {Helpers.format_amount(acc.balance)}")

            choice_tmp = input("\nMelyik számlára szeretnél befizetni? (szám): ").strip()

            if not choice_tmp.isdigit():
                raise ValueError("Érvénytelen választás!")

            choice = int(choice_tmp)

            if choice < 1 or choice > len(accounts):
                raise ValueError("Nincs ilyen sorszámú számla!")

            account = accounts[choice - 1]

            tmp = input("\nBefizetendő összeg: ").strip()

            if not tmp.isdigit():
                raise ValueError("Kérlek, csak pozitív számot adj meg!")

            amount = int(tmp)

            rows = [
                ("Név", c.name),
                ("Számlaszám", account.account_number),
                ("Jelenlegi egyenleg", f"{Helpers.format_amount(account.balance)}"),
                ("Befizetendő összeg", f"{Helpers.format_amount(amount)}"),
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
        try:
            c = self.customer

            if not c:
                print("Nincs kiválasztott ügyfél!")
                return

            accounts = AccountRepository.find_by_customer_id(c.id)

            if not accounts:
                print("Ehhez az ügyfélhez nem tartozik számla!")
                return

            print("\nAz ügyfél számlái:\n")

            for i, acc in enumerate(accounts, start=1):
                print(f"{i}. {acc.account_number} | "
                      f"{acc.account_type} | "
                      f"Egyenleg: {Helpers.format_amount(acc.balance)}")

            choice = int(input("\nMelyik számláról szeretnél kifizetni? (szám): "))

            if choice < 1 or choice > len(accounts):
                raise ValueError("Érvénytelen választás!")

            account = accounts[choice - 1]
            cost = self.get_cost("withdraw")

            tmp = input("Kifizetendő összeg: ").strip()

            if not tmp.isdigit():
                raise ValueError("Kérlek, pozitív egész számot adj meg!")

            amount = int(tmp)

            total = amount + amount * cost

            if account.balance - total < -account.loan_amount:
                raise ValueError("Nincs elegendő fedezet!")

            rows = [
                ("Név", c.name),
                ("Számlaszám", account.account_number),
                ("Kifizetendő összeg", f"{Helpers.format_amount(amount)} Ft"),
            ]

            Helpers.print_table("KIFIZETÉS MEGERŐSÍTÉS", rows)

            confirm = input("\nBiztosan végrehajtod? (i/n): ").lower()

            if confirm != "i":
                print("Művelet megszakítva.")
                return

            AccountService.withdraw(c, account, amount, cost)

            print("\nSikeres!")

        except ValueError as e:
            print(f"Hiba: {e}")

    def transfer(self):
        try:
            source_customer = self.customer

            if not source_customer:
                print("Nincs kiválasztott ügyfél!")
                return

            # Forrás számlák lekérdezése
            accounts = AccountRepository.find_by_customer_id(source_customer.id)

            if not accounts:
                print("Ehhez az ügyfélhez nem tartozik számla!")
                return

            print("\nForrás számlák:\n")

            for i, acc in enumerate(accounts, start=1):
                print(f"{i}. {acc.account_number} | "
                      f"{acc.account_type} | "
                      f"Egyenleg: {Helpers.format_amount(acc.balance)}")

            choice = int(input("\nMelyik számláról utalsz? (sorszám): "))

            if choice < 1 or choice > len(accounts):
                raise ValueError("Érvénytelen választás!")

            source_account = accounts[choice - 1]

            target_account_number = input("Célszámlaszám: ").strip()
            target_account = AccountRepository.find_by_account_number(target_account_number)

            if not target_account:
                raise ValueError("Nem található ilyen számla!")

            target_customer = CustomerRepository.find_by_id(target_account.customer_id)
            print(f"Célszámlatulajdonos: {target_customer.name}")

            tmp = input("Utalandó összeg: ").strip()
            if not tmp.isdigit():
                raise ValueError("Kérlek, pozitív számot adj meg!")

            amount = int(tmp)
            cost = 0.09  # mindig 0,09 a költség
            currency_source = source_account.account_type
            currency_target = target_account.account_type

            # Különböző pénznemek esetén váltás
            if currency_source == "HUN" and currency_target == "EUR":
                transferred_amount = round(amount / 380, 2)
            elif currency_source == "EUR" and currency_target == "HUN":
                transferred_amount = round(amount * 380)
            else:
                transferred_amount = amount

            # Teljes levonás a forrás számláról (összeg + költség)
            total_deduction = amount + cost

            if source_account.balance - total_deduction < -source_account.loan_amount:
                raise ValueError("Nincs elegendő fedezet!")

            # Megerősítés táblázat
            rows = [
                ("Küldő fél", source_customer.name),
                ("Forrás számla", source_account.account_number),
                ("Fogadó fél", target_customer.name),
                ("Utalandó összeg", f"{Helpers.format_amount(transferred_amount)} {currency_target}"),
                ("Költség", f"{Helpers.format_amount(cost)} {currency_source}")
            ]

            Helpers.print_table("UTALÁS MEGERŐSÍTÉS", rows)

            confirm = input("\nBiztosan végrehajtod? (i/n): ").lower()
            if confirm != "i":
                print("Művelet megszakítva.")
                return

            source_account.withdraw(source_customer, amount, cost)
            target_account.balance += transferred_amount
            target_account.transactions.append(
                Transaction(source_customer.id, target_account.account_number, "Átutalás jóváírás", transferred_amount)
            )

            AccountRepository.save(source_account)
            AccountRepository.save(target_account)

            print("\nSikeres utalás!")

        except ValueError as e:
            print(f"Hiba: {e}")

    def get_account_loan(self):
        try:
            c = self.customer

            if not c:
                print("Nincs kiválasztott ügyfél!")
                return

            accounts = AccountRepository.find_by_customer_id(c.id)

            if not accounts:
                print("Ehhez az ügyfélhez nem tartozik számla!")
                return

            hun_accounts = [acc for acc in accounts if acc.account_type == "HUN"]

            if not hun_accounts:
                print("Számlahitel csak HUN típusú számlán igényelhető!")
                return

            print("\nHUN típusú számlák:\n")

            for i, acc in enumerate(hun_accounts, start=1):
                print(f"{i}. {acc.account_number} | "
                      f"Egyenleg: {Helpers.format_amount(acc.balance)} Ft | "
                      f"Számlahitel: {Helpers.format_amount(acc.loan_amount)} Ft")

            choice_tmp = input("\nMelyik számlára szeretnél számlahitelt igényelni? (szám): ").strip()

            if not choice_tmp.isdigit():
                raise ValueError("Érvénytelen választás!")

            choice = int(choice_tmp)

            if choice < 1 or choice > len(hun_accounts):
                raise ValueError("Nincs ilyen sorszám!")

            account = hun_accounts[choice - 1]

            if account.loan_amount != 0:
                print("Már van aktív számlahitel ezen a számlán!")
                return

            proposed_loan = int(account.balance * 1.5)

            rows = [
                ("Név", c.name),
                ("Számlaszám", account.account_number),
                ("Jelenlegi egyenleg", f"{Helpers.format_amount(account.balance)} Ft"),
                ("Igényelhető hitel", f"{Helpers.format_amount(proposed_loan)} Ft"),
            ]

            Helpers.print_table("SZÁMLAHITEL IGÉNYLÉS", rows)

            confirm = input("\nBiztosan igényled? (i/n): ").lower()

            if confirm != "i":
                print("Művelet megszakítva.")
                return

            account.loan_amount = proposed_loan

            account.transactions.append(
                Transaction(
                    c.id,
                    account.account_number,
                    "Számlahitel igénylés",
                    proposed_loan
                )
            )

            AccountRepository.save(account)

            print(f"\nSikeres számlahitel igénylés!")
            print(f"Új hitelkeret: {Helpers.format_amount(account.loan_amount)} Ft")

        except ValueError as e:
            print(f"Hiba: {e}")

    def personal_loan_menu(self):

        PersonalLoanMenu(self.bank).show()

    def export_pdf(self):
        account = AccountRepository.find_by_customer_id(self.customer.id)

        if not account:
            print("Ehhez az ügyfélhez nem tartozik számla!")
            return

        print("\n--- Időszak megadása ---")
        from_str = input("Kezdő dátum (YYYY-MM-DD) vagy Enter: ")
        to_str = input("Záró dátum (YYYY-MM-DD) vagy Enter: ")

        date_from = None
        date_to = None

        if from_str and to_str:
            date_from = datetime.strptime(from_str, "%Y-%m-%d")
            date_to = datetime.strptime(to_str, "%Y-%m-%d")

        path = export_account_statement(
            account,
            self.customer,
            date_from,
            date_to
        )

        print("\nPDF sikeresen elkészült!")
        print(f"Mentési hely: {path}")

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