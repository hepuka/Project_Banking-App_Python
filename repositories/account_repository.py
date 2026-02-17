from config.database import accounts_collection
from models.account import Account

class AccountRepository:

    @staticmethod
    def save(account: Account):
        data = account.to_dict()

        accounts_collection.update_one(
            {"account_number": account.account_number},
            {"$set": data},
            upsert=True
        )

    @staticmethod
    def find_by_customer_id(customer_id):
        data = accounts_collection.find_one(
            {"customer_id": customer_id}
        )
        return Account(data) if data else None

    @staticmethod
    def find_by_account_number(account_number):
        data = accounts_collection.find_one(
            {"account_number": account_number}
        )
        return Account(data) if data else None

    @staticmethod
    def delete_account(customer_id: str):
        accounts_collection.delete_one({"customer_id": customer_id})