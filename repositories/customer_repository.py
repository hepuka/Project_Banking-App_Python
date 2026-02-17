from config.database import customers_collection
from models.customer import Customer

class CustomerRepository:
    
    @staticmethod
    def save(customer: Customer):
        customers_collection.update_one(
            {"id": customer.id},
            {"$set": customer.to_dict()},
            upsert=True
        )

    @staticmethod
    def create_customer(customer: Customer):
        result = customers_collection.insert_one(customer.to_dict())
        return result.inserted_id

    @staticmethod
    def save_all(customers):
        customers_collection.delete_many({})
        customers_collection.insert_many([c.to_dict() for c in customers])

    @staticmethod
    def find_by_id(customer_id: str):
        data = customers_collection.find_one({"id": customer_id}, {"_id": 0})
        return Customer(data) if data else None

    @staticmethod
    def update_customer(_id: str, updates: dict):
        customers_collection.update_one(
            {"id": _id},
            {"$set": updates}
        )

    @staticmethod
    def find_by_account_number(account_number: str):
        data = customers_collection.find_one(
            {"account_number": account_number},
            {"_id": 0}
        )
        return Customer(data) if data else None
