from pymongo import MongoClient, errors
import certifi

class Database:
    _client = None
    _db = None

    @classmethod
    def connect(cls):
        if cls._client:
            return cls._db

        MONGO_URI = (
            "mongodb+srv://kavezo:rkPLxRSJSpcSjeap@cluster0.q7veg.mongodb.net/"
            "bank_app?retryWrites=true&w=majority&appName=bank_app"
        )

        try:
            cls._client = MongoClient(
                MONGO_URI,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=5000
            )

            cls._client.server_info()
            cls._db = cls._client["bank_app"]

            return cls._db

        except errors.ServerSelectionTimeoutError as e:
            raise RuntimeError(
                "Nem sikerült csatlakozni a MongoDB Atlas-hoz. "
                "Ellenőrizd az IP whitelistet és a tanúsítványokat."
            ) from e


# Collection getterek
db = Database.connect()

customers_collection = db["customers"]
users_collection = db["users"]
interest_collection = db["interest"]
costs_collection = db["costs"]
accounts_collection = db["accounts"]
