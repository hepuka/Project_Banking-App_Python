from datetime import datetime
from typing import Optional

class Transaction:
    def __init__(self, type_: str, amount: float, timestamp: Optional[str] = None):
        self.type = type_
        self.amount = amount
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            type_=data["type"],
            amount=data["amount"],
            timestamp=data.get("timestamp")
        )

    def to_dict(self):
        return {"type": self.type, "amount": self.amount, "timestamp": self.timestamp}
