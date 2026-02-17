from datetime import datetime
from typing import List
from .transaction import Transaction

class Account:

    def __init__(self, data: dict):
        self.id = data.get("_id")
        self.customer_id = data["customer_id"]
        self.account_number = data["account_number"]
        self.balance = int(data.get("balance", 0))
        self.loan_amount = int(data.get("loan_amount", 0))
        self.personal_loan_amount = int(data.get("personal_loan_amount", 0))
        self.transactions: List[Transaction] = [
            Transaction.from_dict(t)
            for t in data.get("transactions", [])
        ]
        self.createdAt = data.get(
            "createdAt",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "account_number": self.account_number,
            "balance": self.balance,
            "loan_amount": self.loan_amount,
            "personal_loan_amount": self.personal_loan_amount,
            "transactions": [t.to_dict() for t in self.transactions],
            "createdAt": self.createdAt
        }

    @staticmethod
    def _validate_positive_amount(amount: int):
        if amount <= 0:
            raise ValueError("Az összegnek pozitívnak kell lennie!")

    def _add_transaction(self, name: str, account: str, type_: str, amount: float):
        self.transactions.append(
            Transaction(name, account, type_, amount)
        )

    def deposit(self, c, amount: int):
        self._validate_positive_amount(amount)

        self.balance += amount
        self._add_transaction(
            c.name,
            self.account_number,
            "Befizetés",
            amount
        )

    def withdraw(self, c, amount: int, cost: float):
        self._validate_positive_amount(amount)

        total = amount + amount * cost

        if self.balance - total < -self.loan_amount:
            raise ValueError("Nincs elegendő fedezet a számlán!")

        self.balance -= total
        self.transactions.append(Transaction(c.name, self.account_number, "Kifizetés", amount))
        self.transactions.append(
            Transaction(c.name, self.account_number, "Kifizetés költsége", round(amount * cost, 2))
        )

    def transfer_to(self, target_account, amount: int, cost: float, source_customer_id):
        self._validate_positive_amount(amount)

        total = amount + amount * cost

        if self.balance - total < -self.loan_amount:
            raise ValueError("Nincs elegendő fedezet az utaláshoz!")

        # levonás
        self.balance -= total

        self.transactions.append(
            Transaction(target_account.customer_id,target_account.account_number, "Átutalás bankszámlára", amount)
        )

        self.transactions.append(
            Transaction(target_account.customer_id,target_account.account_number,"Átutalás költsége",round(amount * cost, 2)
            )
        )

        # jóváírás
        target_account.balance += amount

        target_account.transactions.append(
            Transaction(
                source_customer_id,
                self.account_number,
                "Jóváírás",
                amount
            )
        )

    def request_account_loan(self,c):
        if self.loan_amount != 0:
            return False

        self.loan_amount = self.balance * 1.5
        self.transactions.append(Transaction(c.name, self.account_number, "Számlahitel igénylés", self.loan_amount))
        return True
    
    def request_personal_loan(self,current_customer, amount: int):

        if self.personal_loan_amount != 0:
            return False
        
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        
        self.personal_loan_amount += amount
        self.balance += amount
        self.transactions.append(Transaction(current_customer, self.account_number, "Személyi hitel igénylés", amount))
        return True

    def repay_personal_loan(self, account, amount: int):
        if amount <= 0:
            raise ValueError("Hibás összeg!")
        
        if amount > account.personal_loan_amount:
            amount = account.personal_loan_amount
        
        account.personal_loan_amount -= amount
        account.balance -= amount
        self.transactions.append(Transaction(self.name, self.account_number, "Személyi hiteltörlesztés", amount))
        return True

    
    
    