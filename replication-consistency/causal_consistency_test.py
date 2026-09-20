from pymongo import MongoClient
from datetime import datetime, timezone
import time

client = MongoClient("mongodb://mongo1:27017,mongo2:27018,mongo3:27019/?replicaSet=rs0")
with client.start_session(causal_consistency=True) as session:
    db = client["my_database"]
    collection = db["causal_demo"]
    result = collection.insert_one({
        "user_id": int(time.time()),
        "username": "causal_test",
        "email": "test@example.com",
        "last_login_time": datetime.now(timezone.utc)
    }, session=session)
    print(f"Causal write: {result.inserted_id}")
    doc = collection.find_one({"_id": result.inserted_id}, session=session)
    print(f"Causal read: {doc}")
client.close()