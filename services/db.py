from pymongo import MongoClient, errors
import certifi

MONGO_URI = (
    "mongodb+srv://kavezo:rkPLxRSJSpcSjeap@cluster0.q7veg.mongodb.net/"
    "bank_app?retryWrites=true&w=majority&appName=bank_app"
)

try:
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000
    )
    client.server_info()
except errors.ServerSelectionTimeoutError as e:
    raise RuntimeError(
        "Nem sikerült csatlakozni a MongoDB Atlas-hoz. "
        "Ellenőrizd az IP whitelistet és a tanúsítványokat."
    ) from e

db = client["bank_app"]

customers_collection = db["customers"]
users_collection = db["users"]
