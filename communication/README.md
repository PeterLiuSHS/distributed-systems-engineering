# Synchronous Communication Patterns

## Table of Contents

- [Project Overview](#project-overview)
- [Directory Structure](#directory-structure)
- [System Design & Implementation](#system-design--implementation)
  - [Phase 1: Socket Implementation](#phase-1-socket-implementation)
  - [Phase 2: REST API Implementation](#phase-2-rest-api-implementation)
  - [Phase 3: gRPC Implementation](#phase-3-grpc-implementation)
  - [Phase 4: REST vs gRPC Benchmark Comparison](#phase-4-rest-vs-grpc-benchmark-comparison)
- [Conclusion](#conclusion)
- [References](#references)

---

## Project Overview

This project demonstrates **synchronous request–response communication** using three technologies:

- **Raw TCP Sockets** — low-level synchronous data exchange with Python's built-in socket library.  
- **REST API (Flask)** — HTTP-based synchronous CRUD communication.  
- **gRPC** — modern, high-performance RPC using Protocol Buffers.  

A **benchmark module** compares REST and gRPC performance under identical conditions.
All services are containerized using **Docker** and orchestrated via **docker-compose** for reproducible testing.

---

## Directory Structure

Below is the complete project layout as implemented locally in  
`Distributed-systems-lab1`:

lab1/  
├── python-grpc-lab/  
│ ├── generated/  
│ │ ├── **init**.py  
│ │ ├── user_service_pb2.py  
│ │ └── user_service_pb2_grpc.py  
│ ├── proto/  
│ │ └── user_service.proto  
│ ├── client.py  
│ ├── server.py  
│ ├── requirements.txt  
│ └── .idea/  
│  
├── python-rest-lab/  
│ ├── app.py  
│ ├── models.py  
│ ├── Dockerfile  
│ ├── requirements.txt  
│ └── .idea/  
│  
├── python-socket-lab/  
│ ├── client.py  
│ ├── server.py  
│ ├── Dockerfile  
│ ├── requirements.txt  
│ └── .idea/  
│  
├── benchmark.py  
├── docker-compose.yml  
└── README.md

---

## System Design & Implementation

### Phase 1: Socket Implementation

**Tech Stack:** Python socket library + TCP protocol  
This phase demonstrates fundamental synchronous client–server communication via blocking sockets.  
The server listens for connections, processes messages sequentially, and responds before moving to the next client.

#### Example Code

**Server (`server.py`):**

```python
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 8080))
server_socket.listen(3)
print("Server is listening on port 8080")

while True:
    client_socket, addr = server_socket.accept()
    print("Connected from", addr)
    data = client_socket.recv(1024)
    response = data.decode().upper()
    client_socket.send(response.encode())
    client_socket.close()ose()
```

**Client (`client.py`):**

```
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 8080))
client_socket.send(b"hello server")
response = client_socket.recv(1024)
print("Server response:", response.decode())
client_socket.close()
```

#### Test Results

1️⃣ **Normal Communication**

```
Connected to localhost:8080
Sending: hello server
Server response: HELLO SERVER
```

2️⃣ **Wrong Port Simulation**

```powershell
$env:PORT=9999
python client.py
```

```
ConnectionRefusedError: [WinError 10061] No connection could be made because the target machine actively refused it.
```

3️⃣ **Invalid Hostname Simulation**

```$env:APP="no_such_host"
$env:APP="quotno_such_host"
python client.py
```

```
socket.gaierror: [Errno 11001] getaddrinfo failed
```

#### Code Rationale

The **socket implementation** demonstrates the most fundamental synchronous request–response model.

- The **server**:
  
  - Uses `socket.accept()` (blocking call) to wait for a connection.
  - Uses `recv()` (blocking call) to wait for incoming data.
  - Processes the message and returns a response with `send()` before moving to the next client.

- The **client**:
  
  - Uses `connect()` to establish a connection.
  - Sends a message synchronously and waits for a response before continuing.
  - Includes error handling for `ConnectionRefusedError`, `socket.gaierror`, and timeouts.

This phase verifies:

- **Connection establishment**
- **Message transmission**
- **Error handling for invalid endpoints**

The client and server exchange data **synchronously**: each operation blocks until completion, ensuring a one-to-one response cycle.

✅ **Conclusion:**  
This confirms that the socket implementation correctly supports blocking synchronous request–response and proper exception handling.

---

### Phase 2: REST API Implementation

**Tech Stack:** Flask + HTTP/1.1 + JSON

The REST service implements synchronous CRUD endpoints under `/api/users`.  
Each request blocks until the Flask server completes and returns a JSON response.

#### Example Endpoints

| Method | Path              | Description       |
| ------ | ----------------- | ----------------- |
| GET    | `/api/users`      | Get all users     |
| GET    | `/api/users/<id>` | Get user by ID    |
| POST   | `/api/users`      | Create a new user |
| PUT    | `/api/users/<id>` | Update a user     |
| DELETE | `/api/users/<id>` | Delete a user     |

#### Test Cases

**1️⃣ Create User**

```bash
curl.exe -X POST http://127.0.0.1:5000/api/users -H "Content-Type: application/json" -d "{\`"name\`":\`"TestUser\`",\`"email\`":\`"test@example.com\`"}"Response:
```

```json
{"email":"test@example.com","id":"159aeeae","name":"TestUser"}
```

**2️⃣ Get User**

```bash
curl.exe http://127.0.0.1:5000/api/users/1
```

Response:

```json
{"email":"test@example.com","id":"159aeeae","name":"TestUser"}
```

**3️⃣ Update User**

```bash
curl.exe -X PUT http://127.0.0.1:5000/api/users/1 -H "Content-Type: application/json" -d "{\`"name\`":\`"UpdatedUser\`",\`"email\`":\`"updated@example.com\`"}"Response:
```

```json
{"message":"User successfully updated"}
```

**4️⃣ Delete User**

```bash
curl.exe -X DELETE http://127.0.0.1:5000/api/users/1
```

Response: 

```
204 No Content
```

**5️⃣ Invalid Request Example**

```bash
curl.exe http://127.0.0.1:5000/api/users/9999
```

Response:

```json
{"error":"Resource not found"}
```

#### Code Rationale

This **Flask-based REST API** provides synchronous CRUD endpoints for `/api/users`.

- Each route handler executes in a blocking manner:
  
  - The client sends an HTTP request.
  
  - The Flask app processes it and sends a JSON response.
  
  - The client waits for the response before proceeding.

Key features:

- Validates JSON headers (`Content-Type: application/json`)

- Handles missing data and nonexistent resources

- Uses `models.py` to manage in-memory data

This implementation illustrates **synchronous HTTP communication** — the client must wait for the server’s full response before continuing execution.

✅ **Conclusion:**  
The REST service clearly demonstrates synchronous, blocking request–response behavior through standard HTTP methods and JSON data exchange.

---

### Phase 3: gRPC Implementation

**Tech Stack:** Python gRPC + Protocol Buffers

The gRPC phase provides high-performance, strongly typed synchronous RPC communication.  
All messages and services are defined in `user_service.proto`, compiled into generated Python modules.

#### Server (`server.py`)

```python
class UserService(user_service_pb2_grpc.UserServiceServicer):
 def CreateUser(self, request, context):
 new_user = user_service_pb2.User(id="1", name=request.name, email=request.email)
 return new_user
```

**Server Run Output:**

```textile
gRPC server starting on port 50051...
Server is ready and listening for requests
```

#### Client (`client.py`)

```python
with grpc.insecure_channel("localhost:50051") as channel:
 stub = user_service_pb2_grpc.UserServiceStub(channel)
 user = stub.CreateUser(user_service_pb2.CreateUserRequest(name="TestUser", email="test@example.com"))
 print(user)
```

**Output:**

```textile
Created: id: "1" name: "TestUser" email: "test@example.com"
Got: id: "1" name: "TestUser" email: "test@example.com"
Updated: id: "1" name: "UpdatedUser" email: "updated@example.com"
Deleted user ID: 1
```

#### Code Rationale

The **gRPC service** defines synchronous RPC calls via `user_service.proto` and auto-generated stubs.

- The **server** (`server.py`):
  
  - Implements `UserServiceServicer` for Create, Get, Update, Delete operations.
  
  - Uses blocking RPC calls — each method must return before another call can begin for that client.
  
  - Structured error handling using `context.set_code()` (e.g., `NOT_FOUND`, `INVALID_ARGUMENT`).

- The **client** (`client.py`):
  
  - Invokes RPC methods synchronously using `UserServiceStub`.
  
  - Waits for responses before making subsequent calls.
  
  - Validates success and failure scenarios.

gRPC provides **type safety**, **binary serialization (Protocol Buffers)**, and **low latency** while still demonstrating synchronous request–response logic.

✅ **Conclusion:**  
Each RPC is blocking until the server response arrives, ensuring strict synchronous behavior while leveraging binary serialization via Protocol Buffers.

---

### Phase 4: REST vs gRPC Benchmark Comparison

#### Benchmark Command

```bash
python benchmark.py
```

#### Output

```textile
Performance Benchmark - 100 CRUD cycles
==============================================
REST service: available
gRPC service: available
Running 100 complete CRUD operations...
REST Results:
 Total time: 0.631 seconds
 Average per operation: 6.31 ms
gRPC Results:
 Total time: 0.090 seconds
 Average per operation: 0.90 ms
Performance Comparison:
 gRPC is 7.03x faster than REST
 Conclusion: gRPC demonstrates better performance
```

✅ **Performance Summary**

| Method | Avg Time (ms) | Speedup          | Remarks                              |
| ------ | ------------- | ---------------- | ------------------------------------ |
| REST   | 6.31          | –                | Human-readable JSON, slower HTTP/1.1 |
| gRPC   | 0.90          | **7.03× faster** | Binary, compact, efficient           |

#### Performance Analysis

- Both REST and gRPC follow **synchronous request–response** communication.

- REST uses **HTTP/1.1 + JSON**, which introduces overhead due to text parsing and larger payloads.

- gRPC uses **HTTP/2 + Protocol Buffers**, offering:
  
  - Binary serialization (smaller message size)
  
  - Persistent connections
  
  - Multiplexed streams for lower latency

**Result:**

- gRPC completed 100 CRUD operations **7× faster** than REST.

- The performance gain arises from **reduced serialization time** and **more efficient transport**.

Thus, gRPC demonstrates clear advantages in speed and efficiency for synchronous RPC communication.

---

## Conclusion

- **Socket** — demonstrated low-level synchronous blocking communication.

- **REST** — provided structured synchronous CRUD over HTTP.

- **gRPC** — achieved best performance via binary serialization and HTTP/2.

- **Benchmark** — confirmed gRPC is ~7× faster than REST.

- **Docker** — ensured isolated, reproducible testing environments.

This project collectively illustrates the fundamental mechanics and trade-offs of synchronous communication patterns in distributed systems.

---

## References

- [Python socket](https://docs.python.org/3/library/socket.html)

- [Flask Documentation](https://flask.palletsprojects.com/)

- [gRPC Python Docs](https://grpc.io/docs/languages/python/quickstart/)

- [Docker Compose Guide](https://docs.docker.com/compose/)
