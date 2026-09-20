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

    # Insert test data
    insert_result = collection.insert_one(
        {
            "user_id": int(time.time()),
            "username": "read_preference_test",
            "email": "test@example.com",
            "last_login_time": datetime.now(timezone.utc)
        }
    )
    print(f"Write successful: {insert_result.inserted_id}")

    # Test different read preferences
    read_preferences = [
        ("Primary", ReadPreference.PRIMARY),
        ("Secondary", ReadPreference.SECONDARY),
        ("Primary Preferred", ReadPreference.PRIMARY_PREFERRED),
        ("Secondary Preferred", ReadPreference.SECONDARY_PREFERRED),
        ("Nearest", ReadPreference.NEAREST)
    ]

    for name, pref in read_preferences:
        start_time = time.time()
        coll = db.get_collection("user_profile", read_preference=pref, read_concern=ReadConcern("majority"))
        doc = coll.find_one({"_id": insert_result.inserted_id})
        elapsed_time = (time.time() - start_time) * 1000  # milliseconds
        print(f"{name} read result: {doc if doc else 'No data found'}, time: {elapsed_time:.3f} ms")

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
