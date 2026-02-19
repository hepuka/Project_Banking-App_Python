from config.database import accounts_collection
from models.account import Account

class AccountRepository:

    @staticmethod
    def save(account: Account):
        customer_doc = accounts_collection.find_one(
            {"customer_id": account.customer_id}
        )

        account_data = account.to_dict()

        if not customer_doc:
            accounts_collection.insert_one({
                "customer_id": account.customer_id,
                "accounts": [account_data]
            })
            return

        accounts_collection.update_one(
            {"customer_id": account.customer_id},
            {"$push": {"accounts": account_data}}
        )

    @staticmethod
    def find_by_customer_id(customer_id):
        doc = accounts_collection.find_one(
            {"customer_id": customer_id}
        )

        if not doc:
            return []

        accounts = []

        for acc in doc.get("accounts", []):
            acc["customer_id"] = customer_id
            accounts.append(Account(acc))

        return accounts

    @staticmethod
    def find_by_account_number(account_number):
        doc = accounts_collection.find_one(
            {"accounts.account_number": account_number}
        )

        if not doc:
            return None

        customer_id = doc["customer_id"]

        for acc in doc["accounts"]:
            if acc["account_number"] == account_number:
                acc["customer_id"] = customer_id
                return Account(acc)

        return None
