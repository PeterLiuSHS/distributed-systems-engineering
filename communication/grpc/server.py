import grpc
from concurrent import futures
import uuid
from generated import user_service_pb2
from generated import user_service_pb2_grpc

# Simple in-memory storage for demo purposes
USERS = {
    "1": {"id": "1", "name": "TestUser_Alice", "email": "alice@testusr.com"},
    "2": {"id": "2", "name": "TestUser_Bob", "email": "bob@testusr.com"}
}


class UserService(user_service_pb2_grpc.UserServiceServicer):

    def GetUser(self, request, context):
        """Retrieve a user by ID"""
        user_id = request.id
        if user_id in USERS:
            user_data = USERS[user_id]
            return user_service_pb2.User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email']
            )
        else:
            # Return 404 if user not found
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with id {user_id} not found")
            return user_service_pb2.User()

    def CreateUser(self, request, context):
        """Add a new user to the system"""
        # Generate short UUID for demo
        new_id = str(uuid.uuid4())[:8]
        new_user = {
            'id': new_id,
            'name': request.name,
            'email': request.email
        }
        USERS[new_id] = new_user

        return user_service_pb2.User(
            id=new_user['id'],
            name=new_user['name'],
            email=new_user['email']
        )

    def UpdateUser(self, request, context):
        """Modify existing user details"""
        user_id = request.id
        if user_id in USERS:
            # Update user fields
            USERS[user_id]['name'] = request.name
            USERS[user_id]['email'] = request.email

            updated_user = USERS[user_id]
            return user_service_pb2.User(
                id=updated_user['id'],
                name=updated_user['name'],
                email=updated_user['email']
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with id {user_id} not found")
            return user_service_pb2.User()

    def DeleteUser(self, request, context):
        """Remove a user from the system"""
        user_id = request.id
        if user_id in USERS:
            del USERS[user_id]
            return user_service_pb2.Empty()
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"User with id {user_id} not found")
            return user_service_pb2.Empty()

def serve():
    """Main function to start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_service_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50052')

    print("gRPC server starting on port 50052...")
    server.start()
    print("Server is ready and listening for requests")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server shutdown requested")
        server.stop(0)


if __name__ == '__main__':
    serve()