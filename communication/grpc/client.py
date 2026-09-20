import grpc
from generated import user_service_pb2
from generated import user_service_pb2_grpc


def main():
    with grpc.insecure_channel("127.0.0.1:50052") as channel:
        stub = user_service_pb2_grpc.UserServiceStub(channel)

        created = stub.CreateUser(user_service_pb2.CreateUserRequest(
            name="TestUser",
            email="test@example.com"
        ))
        print("Created:>>>", "id:", created.id, "name:", created.name, "email:", created.email)
        print("-------------------------------------------------")

        got = stub.GetUser(user_service_pb2.UserRequest(id=created.id))
        print("Got:>>>", "id:",got.id, "name:",got.name, "email:",got.email)
        print("-------------------------------------------------")

        updated = stub.UpdateUser(user_service_pb2.UpdateUserRequest(
            id=created.id,
            name="UpdatedUser",
            email="updated@example.com"
        ))
        print("Updated:>>>", "id:",updated.id, "name",updated.name, "email:",updated.email)
        print("-------------------------------------------------")

        stub.DeleteUser(user_service_pb2.UserRequest(id=created.id))
        print("Deleted user ID:>>>", created.id)
        print("-------------------------------------------------")


if __name__ == "__main__":
    main()
