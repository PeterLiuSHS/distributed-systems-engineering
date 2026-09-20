from pymongo import MongoClient, ReadPreference
from datetime import datetime, timezone
import time

client = MongoClient("mongodb://mongo1:27017,mongo2:27018,mongo3:27019/?replicaSet=rs0")
db = client["my_database"]
collection = db["user_profile"]

# Primary write
result = collection.insert_one({
    "user_id": int(time.time()),
    "username": "leader_follower_test",
    "email": "test@example.com",
    "last_login_time": datetime.now(timezone.utc)
})
print(f"Primary write: {result.inserted_id}")

# Secondary read
coll = db.get_collection("user_profile", read_preference=ReadPreference.SECONDARY)
doc = coll.find_one({"_id": result.inserted_id})
print(f"Secondary read: {doc}")

client.close()
