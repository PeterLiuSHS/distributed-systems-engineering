from pymongo import MongoClient, ReadPreference
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from datetime import datetime, timezone
import time

try:
    client = MongoClient(
        "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0",
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )
    client.admin.command('ping')
    print("Successfully connected to MongoDB replica set!")

    db = client.get_database("my_database", read_concern=ReadConcern("majority"))
    collection = db.get_collection("user_profile", write_concern=WriteConcern(w="majority", wtimeout=5000, j=True))

    insert_result = collection.insert_one(
        {
            "user_id": int(time.time()),
            "username": "strong_consistency_user",
            "email": "strong_user@example.com",
            "last_login_time": datetime.now(timezone.utc)
        }
    )
    print(f"Strong consistency write successful: {insert_result.inserted_id}")

    # Read from secondary node
    secondary_collection = db.get_collection("user_profile", read_preference=ReadPreference.SECONDARY, read_concern=ReadConcern("majority"))
    doc = secondary_collection.find_one({"_id": insert_result.inserted_id})
    print(f"Strong consistency read result (from secondary): {doc if doc else 'No data found'}")

except ServerSelectionTimeoutError as e:
    print(f"Server selection timeout error: {e}")
except ConnectionFailure as e:
    print(f"Connection failure: {e}")
except OperationFailure as e:
    print(f"Operation failure: {e}")
except Exception as e:
    print(f"Other error: {e}")
finally:
    client.close()
