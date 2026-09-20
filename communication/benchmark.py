import os
import sys
import time
import grpc
import requests

# Configure paths for imports
project_root = os.path.join(os.path.dirname(__file__), "python-grpc-lab")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from generated import user_service_pb2
from generated import user_service_pb2_grpc

# Service configurations
REST_API_URL = "http://127.0.0.1:5000/api/users"
GRPC_SERVER_ADDRESS = "127.0.0.1:50052"
TEST_ITERATIONS = 100


def test_rest_performance(iterations=TEST_ITERATIONS):
    """Measure REST API performance for complete CRUD cycle"""
    start_time = time.perf_counter()

    for i in range(iterations):
        # Create new user
        response = requests.post(
            REST_API_URL,
            json={"name": f"TestUser_{i}", "email": f"user_{i}@test.com"}
        )
        response.raise_for_status()
        user_id = response.json()["id"]

        # Retrieve user
        response = requests.get(f"{REST_API_URL}/{user_id}")
        response.raise_for_status()

        # Update user information
        response = requests.put(
            f"{REST_API_URL}/{user_id}",
            json={"name": f"UpdatedUser_{i}", "email": f"updated_{i}@test.com"}
        )
        response.raise_for_status()

        # Remove user
        response = requests.delete(f"{REST_API_URL}/{user_id}")
        if response.status_code not in (200, 204):
            response.raise_for_status()

    total_time = time.perf_counter() - start_time
    avg_time_per_operation = (total_time / iterations) * 1000

    return total_time, avg_time_per_operation


def test_grpc_performance(iterations=TEST_ITERATIONS):
    """Measure gRPC performance for complete CRUD cycle"""
    with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
        client = user_service_pb2_grpc.UserServiceStub(channel)

        start_time = time.perf_counter()

        for i in range(iterations):
            # Create user via gRPC
            new_user = client.CreateUser(
                user_service_pb2.CreateUserRequest(
                    name=f"TestUser_{i}",
                    email=f"user_{i}@test.com"
                )
            )

            # Get user details
            client.GetUser(
                user_service_pb2.UserRequest(id=new_user.id)
            )

            # Update user data
            client.UpdateUser(
                user_service_pb2.UpdateUserRequest(
                    id=new_user.id,
                    name=f"UpdatedUser_{i}",
                    email=f"updated_{i}@test.com"
                )
            )

            # Delete user
            client.DeleteUser(
                user_service_pb2.UserRequest(id=new_user.id)
            )

        total_time = time.perf_counter() - start_time
        avg_time_per_operation = (total_time / iterations) * 1000

        return total_time, avg_time_per_operation


def check_service_availability():
    """Verify both services are running before benchmarking"""
    services_ready = True

    # Check REST service
    try:
        response = requests.get(REST_API_URL, timeout=2)
        print("REST service: available")
    except:
        print("REST service: not reachable")
        services_ready = False

    # Check gRPC service
    try:
        with grpc.insecure_channel(GRPC_SERVER_ADDRESS) as channel:
            grpc.channel_ready_future(channel).result(timeout=2)
        print("gRPC service: available")
    except:
        print("gRPC service: not reachable")
        services_ready = False

    return services_ready


def main():
    """Execute performance comparison"""
    print(f"Performance Benchmark - {TEST_ITERATIONS} CRUD cycles")
    print("=" * 50)

    if not check_service_availability():
        print("Please start both services before running benchmarks")
        return

    print(f"Running {TEST_ITERATIONS} complete CRUD operations...")

    # Test REST performance
    try:
        rest_total, rest_avg = test_rest_performance()
        print("\nREST Results:")
        print(f"  Total time: {rest_total:.3f} seconds")
        print(f"  Average per operation: {rest_avg:.2f} ms")
    except Exception as e:
        print(f"REST test failed: {e}")
        rest_total = rest_avg = 0

    # Test gRPC performance
    try:
        grpc_total, grpc_avg = test_grpc_performance()
        print("\ngRPC Results:")
        print(f"  Total time: {grpc_total:.3f} seconds")
        print(f"  Average per operation: {grpc_avg:.2f} ms")
    except Exception as e:
        print(f"gRPC test failed: {e}")
        grpc_total = grpc_avg = 0

    # Performance comparison
    if rest_total > 0 and grpc_total > 0:
        print("\nPerformance Comparison:")
        speedup = rest_total / grpc_total if grpc_total > 0 else 0
        print(f"  gRPC is {speedup:.2f}x faster than REST")

        if speedup > 1:
            print("  Conclusion: gRPC demonstrates better performance")
        else:
            print("  Conclusion: REST performance is comparable or better")


if __name__ == "__main__":
    main()