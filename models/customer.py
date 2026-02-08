import random
from datetime import datetime
from typing import List
from .transaction import Transaction

class Customer:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.email = data["email"]
        self.account_number = data.get("account_number", self.generate_account_number())
        self.balance = int(data.get("balance", 0))
        self.loan_amount = int(data.get("loan_amount", 0))
        self.personal_loan_amount = int(data.get("personal_loan_amount", 0))
        self.transactions: List[Transaction] = [
            Transaction.from_dict(t) for t in data.get("transactions", [])
        ]
        self.createdAt = data.get("createdAt", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "account_number": self.account_number,
            "balance": self.balance,
            "loan_amount": self.loan_amount,
            "personal_loan_amount": self.personal_loan_amount,
            "transactions": [t.to_dict() for t in self.transactions],
            "createdAt": self.createdAt
        }

    # ------- TRANSACTIONS ------------
    def deposit(self, amount: int):
        if amount <= 0:
            raise ValueError("A befizetés összege csak pozitív lehet!")

        self.balance += amount
        self.transactions.append(Transaction(self.name, self.account_number, "Befizetés", amount))

    def withdraw(self, amount: int, cost: float):
        if amount <= 0:
            raise ValueError("Hibás összeg!")

        total = amount + amount * cost

        if self.balance - total < -self.loan_amount:
            raise ValueError("Nincs elegendő fedezet a számlán!")

        self.balance -= total
        self.transactions.append(Transaction(self.name, self.account_number, "Kifizetés", amount))
        self.transactions.append(
            Transaction(self.name, self.account_number, "Kifizetés költsége", round(amount * cost, 2))
        )
    
    def transfer_to(self,current_customer, target_customer, amount: int, cost: float):
        if amount <= 0:
            raise ValueError("Hibás összeg!")

        if self.balance - amount < -self.loan_amount:
            raise ValueError("Nincs elegendő fedezet az utaláshoz!")

        # levonás
        total = amount + amount * cost
        self.balance -= total
        self.transactions.append(
            Transaction(target_customer.name, target_customer.account_number, "Átutalás bankszámlára", amount)
        )

        self.transactions.append(
            Transaction(current_customer.name, current_customer.account_number, "Átutalás költsége", round(amount * cost, 2))
        )

        # jóváírás
        target_customer.balance += amount
        self.transactions.append(
            Transaction(current_customer.name, current_customer.account_number, "Jóváírás", amount)
        )

    # ---------- LOAN -------------
    def request_account_loan(self):
        if self.loan_amount != 0:
            return False
        self.loan_amount = self.balance * 1.5
        self.transactions.append(Transaction(self.name, self.account_number, "Számlahitel igénylés", self.loan_amount))
        return True

    def request_personal_loan(self, amount: int):
        if self.personal_loan_amount != 0:
            return False
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        self.personal_loan_amount += amount
        self.balance += amount
        self.transactions.append(Transaction(self.name, self.account_number, "Személyi hitel igénylés", amount))
        return True

    def repay_personal_loan(self, amount: int):
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        
        if amount > self.personal_loan_amount:
            amount = self.personal_loan_amount
        
        self.personal_loan_amount -= amount
        self.balance -= amount
        self.transactions.append(Transaction(self.name, self.account_number, "Személyi hiteltörlesztés", amount))
        return True

    # ------ HELPERS -------------
    @staticmethod
    def generate_account_number():
        first_block = "1177" + str(random.randint(1000, 9999))
        second_block = str(random.randint(10_000_000, 99_999_999))
        third_block = str(random.randint(10_000_000, 99_999_999))
        return f"{first_block}-{second_block}-{third_block}"
    
    @staticmethod
    def format_amount(amount: int) -> str:
        return f"{amount:,}".replace(",", ".")

    @staticmethod
    def print_table(title: str, rows: list[tuple[str, str]]):
        col_width = max(len(label) for label, _ in rows) + 2

        print(f"\n{title}")

        for label, value in rows:
            print(f"{label.ljust(col_width)} | {value}")




