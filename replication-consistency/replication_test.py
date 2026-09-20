from pymongo import MongoClient, WriteConcern
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure, OperationFailure
from datetime import datetime, timezone
import time
import statistics


def test_write_concern(client, w, num_records=500, timeout_ms=5000):
    db = client["my_database"]
    collection = db.get_collection("user_profile", write_concern=WriteConcern(w=w, wtimeout=timeout_ms, j=True))
    times = []
    inserted_ids = []

    print(f"\nTesting write concern w={w}, inserting {num_records} records...")
    for i in range(num_records):
        try:
            start_time = time.perf_counter()
            result = collection.insert_one(
                {
                    "user_id": int(time.time()) + i,
                    "username": f"test_w_{w}_{i}",
                    "email": f"test_w_{w}_{i}@example.com",
                    "last_login_time": datetime.now(timezone.utc),
                    "dummy_data": "x" * 1000  # 1KB data
                }
            )
            elapsed_time_ms = (time.perf_counter() - start_time) * 1000  # convert to milliseconds
            times.append(elapsed_time_ms)
            inserted_ids.append(result.inserted_id)
        except OperationFailure as e:
            print(f"Write failed (w={w}, record {i + 1}): {e}. Possible reason: insufficient available nodes (requires {w} nodes)")
            break

    if times:
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)
        std_time = statistics.stdev(times) if len(times) > 1 else 0
        print(f"Write successful (w={w}): {len(inserted_ids)} records")
        print(f"Time statistics (ms):")
        print(f"  Average: {avg_time:.3f}")
        print(f"  Max: {max_time:.3f}")
        print(f"  Min: {min_time:.3f}")
        print(f"  Std dev: {std_time:.3f}")
        return inserted_ids
    else:
        print(f"Write failed (w={w}): no records inserted")
        return []


def simulate_primary_failure(client):
    try:
        status = client.admin.command('replSetGetStatus')
        primary = next((m for m in status['members'] if m['stateStr'] == 'PRIMARY'), None)
        original_primary = primary['name'] if primary else 'No primary'
        primary_container = original_primary.split(':')[0]
        print(f"Please run 'docker stop {primary_container}' in another terminal to simulate primary node failure")
        print("Detecting primary re-election...")
        print(f"Current primary: {original_primary}")
    except Exception as e:
        print(f"Failed to get initial primary: {e}")
        return None

    start_time = time.perf_counter()
    max_wait_time = 60
    poll_interval = 0.5

    while time.perf_counter() - start_time < max_wait_time:
        try:
            status = client.admin.command('replSetGetStatus')
            new_primary = next((m for m in status['members'] if m['stateStr'] == 'PRIMARY'), None)
            if new_primary and new_primary['name'] != original_primary:
                elapsed_time_ms = (time.perf_counter() - start_time) * 1000  # convert to milliseconds
                print(f"New primary detected: {new_primary['name']}, re-election time: {elapsed_time_ms:.3f} ms")
                return elapsed_time_ms
            time.sleep(poll_interval)
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print(f"Error while polling status (possibly due to primary failure): {e}")
            time.sleep(poll_interval)
        except Exception as e:
            print(f"Other error: {e}")
            time.sleep(poll_interval)

    print("No new primary detected within 60 seconds; re-election may have failed")
    return None


try:
    client = MongoClient(
        "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0",
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        socketTimeoutMS=10000
    )

    client.admin.command('ping')
    print("Successfully connected to MongoDB replica set!")

    status = client.admin.command('replSetGetStatus')
    primary = next((m for m in status['members'] if m['stateStr'] == 'PRIMARY'), None)
    print(f"Current primary: {primary['name'] if primary else 'No primary'}")

    print("\nTesting write concern w=1...")
    inserted_ids_w1 = test_write_concern(client, w=1, num_records=500)

    print("\nTesting write concern w=majority...")
    inserted_ids_majority = test_write_concern(client, w='majority', num_records=500)

    print("\nTesting write concern w=3...")
    inserted_ids_w3 = test_write_concern(client, w=3, num_records=500)

    print("\nSimulating primary node failure...")
    election_time = simulate_primary_failure(client)

    status = client.admin.command('replSetGetStatus')
    new_primary = next((m for m in status['members'] if m['stateStr'] == 'PRIMARY'), None)
    print(f"New primary: {new_primary['name'] if new_primary else 'No primary'}")

    print("\nTesting post-failure write (w=majority)...")
    inserted_ids_post_failure = test_write_concern(client, w='majority', num_records=500)

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
