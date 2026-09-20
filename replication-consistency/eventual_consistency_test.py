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

    db = client.get_database("my_database", read_concern=ReadConcern("local"))
    collection = db.get_collection("user_profile", write_concern=WriteConcern(w=1, j=True))

    insert_result = collection.insert_one(
        {
            "user_id": int(time.time()),
            "username": "eventual_consistency_user",
            "email": "eventual_user@example.com",
            "last_login_time": datetime.now(timezone.utc)
        }
    )
    print(f"Eventual consistency write successful: {insert_result.inserted_id}")

    # Loop to read from secondary node
    secondary_collection = db.get_collection("user_profile", read_preference=ReadPreference.SECONDARY, read_concern=ReadConcern("local"))
    max_attempts = 10
    interval = 0.5  # seconds
    for i in range(max_attempts):
        doc = secondary_collection.find_one({"_id": insert_result.inserted_id})
        print(f"Eventual consistency read result (from secondary, attempt {i+1}): {doc if doc else 'No data found'}")
        if doc and doc["_id"] == insert_result.inserted_id:
            print(f"Data synchronized after: {i * interval * 1000:.3f} ms")
            break
        time.sleep(interval)
    else:
        print("Data not synchronized within expected time")

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
