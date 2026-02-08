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
            raise ValueError("Hibás összeg!")
        self.balance += amount
        self.transactions.append(Transaction("Befizetés", amount))

    def withdraw(self, amount: int):
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        if self.balance - amount < -self.loan_amount:
            raise ValueError("Nincs elegendő fedezet a számlán!")
        self.balance -= amount
        self.transactions.append(Transaction("Kifizetés", amount))
    
    def transfer_to(self,current_customer, target_customer, amount: int):
        if amount <= 0:
            raise ValueError("Hibás összeg!")

        if self.balance - amount < -self.loan_amount:
            raise ValueError("Nincs elegendő fedezet az utaláshoz!")

        # levonás
        self.balance -= amount
        self.transactions.append(
            Transaction(
                f"Átutalás bankszámlára: {target_customer.name} - {target_customer.account_number}",
                amount
            )
        )

        # jóváírás
        target_customer.balance += amount
        target_customer.transactions.append(
            Transaction(
                f"Jóváírás: {current_customer.name} - {current_customer.account_number}",
                amount
            )
        )

    # ---------- LOAN -------------
    def request_account_loan(self):
        if self.loan_amount != 0:
            return False
        self.loan_amount = self.balance * 1.5
        self.transactions.append(Transaction("Számlahitel igénylés", self.loan_amount))
        return True

    def request_personal_loan(self, amount: int):
        if self.personal_loan_amount != 0:
            return False
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        self.personal_loan_amount += amount
        self.balance += amount
        self.transactions.append(Transaction("Személyi hitel igénylés", amount))
        return True

    def repay_personal_loan(self, amount: int):
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        
        if amount > self.personal_loan_amount:
            amount = self.personal_loan_amount
        
        self.personal_loan_amount -= amount
        self.balance -= amount
        self.transactions.append(Transaction("Személyi hiteltörlesztés", amount))
        return True

    # ------ ACCOUNT NUMBER -------------
    @staticmethod
    def generate_account_number():
        first_block = "1177" + str(random.randint(1000, 9999))
        second_block = str(random.randint(10_000_000, 99_999_999))
        third_block = str(random.randint(10_000_000, 99_999_999))
        return f"{first_block}-{second_block}-{third_block}"


