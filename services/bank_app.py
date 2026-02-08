import json
import uuid
import sys
from typing import List, Optional, Dict
from models.customer import Customer
from services.db import customers_collection, users_collection

class BankApp:
    def __init__(self):
        self.customers: List[Customer] = []
        self.users: List[Dict] = []
        self.current_customer: Optional[Customer] = None
        self.current_user: Optional[dict] = None
        self.load_data()

    # ---------- DATABASE ----------

    def load_data(self):
        self.customers = [
            Customer(c) for c in customers_collection.find({}, {"_id": 0})
        ]
        self.users = list(users_collection.find({}))

    def save_data(self):
        customers_collection.delete_many({})
        users_collection.delete_many({})

        customers_collection.insert_many(
            [c.to_dict() for c in self.customers]
        )
        users_collection.insert_many(self.users)

    # ---------- MENU'S ----------
    def main_menu(self):
        menu = {
            "1": ("Ügyfélkereső", self.customer_menu),
            "2": ("Új ügyfél", self.add_customer),
            "3": ("Kilépés", self.exit_app)
        }
        self.run_menu(menu)

    def customer_actions_menu(self):
        menu = {
            "1": ("Ügyféladatok", self.customer_details),
            "2": ("Tranzakciók listája", self.get_transactions),
            "3": ("Befizetés", self.deposit),
            "4": ("Kifizetés", self.withdraw),
            "5": ("Utalás bankszámlára", self.transfer),
            "6": ("Számlahitel", self.account_loan_menu),
            "7": ("Személyi kölcsön", self.personal_loan_menu),
            "8": ("Vissza a főmenübe", self.back_to_main_menu),
            "9": ("Kilépés", self.exit_app)
        }
        self.run_menu(menu)

    def customer_menu(self):
        if not self.find_customer():
            return
        self.customer_actions_menu()

    def account_loan_menu(self):
        if self.current_customer.request_account_loan():
            self.save_data()
            print(f"Sikeres számlahitel: {self.current_customer.loan_amount} Ft")
        else:
            print("Már van számlahitel!")

    def personal_loan_menu(self):
        menu = {
            "1": ("Kölcsön igénylés", self.request_personal_loan),
            "2": ("Törlesztés", self.repay_personal_loan),
            "3": ("Vissza az ügyfél menübe", self.back_to_customer_menu),
        }
        self.run_menu(menu)

    def back_to_main_menu(self):
        self.current_customer = None
        self.main_menu()

    def back_to_customer_menu(self):
        if not self.current_customer:
            print("Nincs aktív ügyfél!")
            return
        self.customer_actions_menu()
    
    def run_menu(self, menu: dict):
        while True:
            print("\n---------- MENÜ ----------")
            for key, (desc, _) in menu.items():
                print(f"({key}) {desc}")
            choice = input("Válassz: ")
            action = menu.get(choice)
            if action:
                action[1]()
            else:
                print("Érvénytelen választás!")

    # ---------- CUSTOMER ----------
    def find_customer_by_account_number(self, account_number: str):
        for c in self.customers:
            if c.account_number == account_number:
                return c
        return None

    def add_customer(self):
        name = input("Név: ")
        email = input("Email: ")
        new_customer = Customer({
            "id": uuid.uuid4().hex[:4],
            "name": name,
            "email": email,
            "balance": 0,
            "loan_amount": 0,
            "personal_loan_amount": 0
        })
        self.customers.append(new_customer)
        self.save_data()
        print(f"Új ügyfél létrehozva! Azonosító: {new_customer.id}")

    def find_customer(self):
        customer_id = input("Add meg az ügyfél azonosítóját: ")
        for c in self.customers:
            if c.id == customer_id:
                self.current_customer = c
                print(f"Ügyfél: {c.name}")
                return True
        print("Nem található ügyfél!")
        return False

    def customer_details(self):
        c = self.current_customer
        print("\nÜgyféladatok:")
        print(f"Név: {c.name}")
        print(f"E-mail: {c.email}")
        print(f"Számlaszám: {c.account_number}")
        print(f"Egyenleg: {c.balance} Ft")
        print(f"Hitelkeret: {c.loan_amount} Ft")
        print(f"Személyi kölcsön: {c.personal_loan_amount} Ft")

    def get_transactions(self):
        print("\nTranzakciók:")
        if len(self.current_customer.transactions) == 0:
            print("Nincs tranzakció!")
        for t in self.current_customer.transactions:
            print(f"{t.timestamp} - {t.type} - {t.amount} Ft")

    def deposit(self):
        try:
            c = self.current_customer
            print(f"\nNév: {c.name}")
            print(f"Egyenleg: {c.balance} Ft")

            tmp = input("Befizetendő összeg: ").strip()

            if not tmp.isdigit():
                raise ValueError("Kérlek, csak pozitív számot ad meg!")

            amount = int(tmp)
            self.current_customer.deposit(amount)
            self.save_data()
            print("Sikeres befizetés!")
        except ValueError as e:
            print(e)

    def withdraw(self):
        try:
            amount = int(input("Kifizetendő összeg: "))
            self.current_customer.withdraw(amount)
            self.save_data()
            print("Sikeres!")
        except ValueError as e:
            print(e)
    
    def request_personal_loan(self):
        amount = int(input("Kölcsön összege: "))
        if self.current_customer.request_personal_loan(amount):
            self.save_data()
            print(f"Sikeres személyi hiteligénylés: {self.current_customer.personal_loan_amount} Ft")
        else:
            print("Az ügyfél már rendelkezik személyi hitellel!")
    
    def repay_personal_loan(self):
        print(f"\nFennáló hitelösszeg: {self.current_customer.personal_loan_amount} Ft")
        amount = int(input("Törlesztés összege: "))
        if self.current_customer.repay_personal_loan(amount):
            self.save_data()
            print(f"Sikeres törlesztés.\nFennálló hitelösszeg: {self.current_customer.personal_loan_amount} Ft")
        else:
            print("Törlesztés hiba!")
    
    # ---------- TRANSACTIONS ----------
    def transfer(self):
        try:
            print(f"\nForrás számla: {self.current_customer.account_number}")
            print(f"Egyenleg: {self.current_customer.balance} Ft\n")

            target_account = input("Cél számlaszám: ").strip()
            target_customer = self.find_customer_by_account_number(target_account)

            print("\nCél számlaadatok:")
            print(f"Név: {target_customer.name}")
            print(f"Számlaszám: {target_customer.account_number}\n")

            if not target_customer:
                print("Cél számla nem található!")
                return

            amount = int(input("Utalás összege: "))

            self.current_customer.transfer_to(self.current_customer, target_customer, amount)
            self.save_data()

            print("\nSikeres utalás!")
        except ValueError as e:
            print(e)

    # ---------- EXIT ----------
    def exit_app(self):
        print("Kilépés...")
        sys.exit(0)