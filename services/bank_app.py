import uuid
import sys
from typing import List, Optional, Dict
from models.customer import Customer
from models.user import User
from services.db import customers_collection, users_collection, interest_collection, costs_collection

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
            Customer(c)
            for c in customers_collection.find({}, {"_id": 0})
        ]

        self.users = list(
            users_collection.find({}, {"_id": 0})
        )

    def save_data(self):
        if self.customers:
            customers_collection.delete_many({})
            customers_collection.insert_many(
                [c.to_dict() for c in self.customers]
            )

        if self.users:
            users_collection.delete_many({})
            users_collection.insert_many(self.users)

    # ---------- MENU'S ----------
    def main_menu(self):
        user_menu = {
            "1": ("Ügyfélkereső", self.customer_menu),
            "2": ("Új ügyfél", self.add_customer),
            "0": ("Kilépés", self.exit_app)
        }
        admin_menu = {
            "1": ("Új felhasználó hozzáadása", self.add_user),
            "2": ("Rögzített felhasználók", self.get_users),
            "0": ("Kilépés", self.exit_app)
        }

        user = self.current_user["role"]
        self.run_menu(admin_menu if user == "admin" else user_menu)

    def customer_actions_menu(self):
        menu = {
            "1": ("Ügyféladatok", self.customer_details),
            "2": ("Számlaadatok", self.account_details),
            "3": ("Tranzakciók listája", self.get_transactions),
            "4": ("Befizetés", self.deposit),
            "5": ("Kifizetés", self.withdraw),
            "6": ("Utalás bankszámlára", self.transfer),
            "7": ("Számlahitel", self.account_loan_menu),
            "8": ("Személyi kölcsön", self.personal_loan_menu),
            "9": ("Vissza a főmenübe", self.back_to_main_menu),
            "0": ("Kilépés", self.exit_app)
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
    
    @staticmethod
    def run_menu(menu: dict):
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



    # ---------- USER ----------
    def add_user(self):
        name = input("Név: ")
        email = input("Email: ")
        username = input("Felhasználónév: ")
        password = input("Jelszó: ")
        tmp = input("Szerepkör: (1)user (2)admin:")
        role = "user" if tmp == "1" else "admin"

        new_user = User({
            "name": name,
            "email": email,
            "username": username,
            "password": password,
            "role": role

        })
        self.users.append(new_user.user_to_dict())
        self.save_data()
        print(f"Új felhasználó létrehozva! Azonosító: {new_user.name}")

    def get_users(self):
        users = self.users

        if not users:
            print("\nNincs rögzített felhasználó!")
            return

        print("\nFELHASZNÁLÓK")
        print(
            f"{'Név'.ljust(20)} | "
            f"{'Email'.ljust(20)} | "
            f"{'Szerepkör'.ljust(10)} | "
            f"{'Felhasználónév'.ljust(20)} | "
            f"{'Jelszó'.ljust(20)} | "
            f"{'Létrehozva'.ljust(20)} | "

        )

        for u in users:
            print(
                f"{u.get('name', '').ljust(20)} | "
                f"{u.get('email', '').ljust(20)} | "
                f"{u.get('role', '').ljust(10)} | "
                f"{u.get('username', '').ljust(20)} | "
                f"{u.get('password', '').ljust(20)} | "
                f"{u.get('createdAt', '').ljust(20)}"
            )


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
        customer_id = input("\nAdd meg az ügyfél azonosítóját: ")
        for c in self.customers:
            if c.id == customer_id:
                self.current_customer = c
                self.customer_details()
                return True
        print("Nem található ügyfél!")
        return False

    def customer_details(self):
        c = self.current_customer

        rows = [
            ("Név", c.name),
            ("E-mail", c.email),
            ("Számlaszám", c.account_number),
            ("Számlanyitás", c.createdAt),
        ]

        Customer.print_table("ÜGYFÉLADATOK", rows)

    def account_details(self):
        c = self.current_customer

        rows = [
            ("Név", c.name),
            ("Számlaszám", c.account_number),
            ("Számlaegyenleg", f"{Customer.format_amount(c.balance)} Ft"),
            ("Számlahitel összege", f"{Customer.format_amount(c.loan_amount)} Ft"),
            ("Személyi kölcsön összege", f"{Customer.format_amount(c.personal_loan_amount)} Ft"),
        ]

        Customer.print_table("SZÁMLAADATOK", rows)

    def get_transactions(self):
        c = self.current_customer

        if not c.transactions:
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

        for t in c.transactions:
            print(
                f"{t.timestamp.ljust(20)} | "
                f"{t.type.ljust(20)} | "
                f"{t.name.ljust(20)} | "
                f"{t.account_number.ljust(30)} | "
                f"{t.formatted_amount()} Ft"
            )

    def deposit(self):
        try:
            c = self.current_customer
            rows = [
                ("Név", c.name),
                ("Számlaegyenleg", f"{Customer.format_amount(c.balance)} Ft"),
                ]
            
            Customer.print_table("ÜGYFÉLADATOK", rows)

            tmp = input("\nBefizetendő összeg: ").strip()

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
            cost = self.get_cost("withdraw")
            c = self.current_customer
            rows = [
                ("Név", c.name),
                ("Számlaegyenleg", f"{Customer.format_amount(c.balance)} Ft"),
                ]
            
            Customer.print_table("ÜGYFÉLADATOK", rows)

            tmp = input("\nKifizetendő összeg: ").strip()
            
            if not tmp.isdigit():
                raise ValueError("Kérlek, csak pozitív számot adj meg!")

            amount = int(tmp)
            self.current_customer.withdraw(amount, cost)
            self.save_data()
            print("Sikeres kifizetés!")

        except ValueError as e:
            print(e)
    
    def request_personal_loan(self):
        amount = int(input("Kölcsön összege: "))
        if self.current_customer.request_personal_loan(amount):
            self.save_data()
            print(f"Sikeres személyi hiteligénylés: {Customer.format_amount(self.current_customer.personal_loan_amount)} Ft")
        else:
            print("Az ügyfél már rendelkezik személyi hitellel!")
    
    def repay_personal_loan(self):
        try:
            c = self.current_customer
            rows = [
                ("Név", c.name),
                ("Fennáló hitelösszeg", f"{Customer.format_amount(c.personal_loan_amount)} Ft"),
                ]
            
            Customer.print_table("ÜGYFÉLADATOK", rows)

            tmp = input("\nTörlesztés összege: ").strip()

            if not tmp.isdigit():
                raise ValueError("Kérlek, csak pozitív számot ad meg!")

            amount = int(tmp)

            if self.current_customer.repay_personal_loan(amount):
                self.save_data()
                print(f"Sikeres törlesztés.\nFennálló hitelösszeg: {Customer.format_amount(c.personal_loan_amount)} Ft")
            else:
                print("Törlesztés hiba!")

        except ValueError as e:
            print(e)
    
    # ---------- TRANSACTIONS ----------
    def transfer(self):
        try:
            c = self.current_customer
            rows = [
                ("Forrás számla", c.account_number),
                ("Számlaegyenleg", f"{Customer.format_amount(c.balance)} Ft"),
                ]
            
            Customer.print_table("FORRÁS SZÁMLAADATOK", rows)

            target_account = input("Cél számlaszám: ").strip()
            target_customer = self.find_customer_by_account_number(target_account)

            rows2 = [
                ("Név", target_customer.name),
                ("Számlaszám", target_customer.account_number),
                ]
            
            Customer.print_table("CÉL SZÁMLAADATOK", rows2)

            if not target_customer:
                print("Cél számla nem található!")
                return

            cost = self.get_cost("transaction")
            tmp = input("Utalás összege: ").strip()
            
            if not tmp.isdigit():
                raise ValueError("Kérlek, csak pozitív számot adj meg!")

            amount = int(tmp)
            self.current_customer.transfer_to(self.current_customer, target_customer, amount, cost)
            self.save_data()

            print("\nSikeres utalás!")
        except ValueError as e:
            print(e)

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
    
    # ---------- EXIT ----------
    @staticmethod
    def exit_app():
        print("Kilépés...")
        sys.exit(0)
    
