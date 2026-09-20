from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, ConfigurationError
from datetime import datetime, timezone

try:
    # Connect to the replica set
    client = MongoClient(
        "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0",
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )

    # Test the connection
    client.admin.command('ping')
    print("Successfully connected to the MongoDB replica set!")

    # Check replica set status
    status = client.admin.command('replSetGetStatus')
    print("Replica set status:", status)

    db = client["my_database"]
    collection = db["user_profile"]

    # Insert data
    users = [
        {
            "user_id": i,
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "last_login_time": datetime.now(timezone.utc)
        }
        for i in range(1, 6)
    ]

    collection.insert_many(users)
    print("Data insertion completed!")

    # Verify data
    for doc in collection.find():
        print(doc)

except ServerSelectionTimeoutError as e:
    print(f"Server selection timeout error: {e}")
except ConnectionFailure as e:
    print(f"Connection failure: {e}")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
except Exception as e:
    print(f"Other error: {e}")
finally:
    client.close()
