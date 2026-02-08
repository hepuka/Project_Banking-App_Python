from datetime import datetime
from typing import Optional

class Transaction:
    def __init__(self, name: str, account_number: str, type_: str, amount: float, timestamp: Optional[str] = None):
        self.name = name
        self.account_number = account_number
        self.type = type_
        self.amount = amount
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            account_number=data["account_number"],
            type_=data["type"],
            amount=data["amount"],
            timestamp=data.get("timestamp")
        )

    def to_dict(self):
        return {"name": self.name, "account_number": self.account_number, "type": self.type, "amount": self.amount, "timestamp": self.timestamp}

    def formatted_amount(self):
        return f"{self.amount:,}".replace(",", ".")
