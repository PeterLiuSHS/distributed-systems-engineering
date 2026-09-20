# Service Communication & Benchmarking

A hands-on comparison of synchronous communication patterns in distributed systems using **TCP sockets**, **REST**, and **gRPC**.

The experiment implements the same request-response concept at different abstraction levels and benchmarks REST and gRPC under the same local containerized environment.

## Overview

This module explores three approaches to synchronous service communication:

- **TCP Sockets** — low-level client-server communication using Python's socket library.
- **REST** — HTTP-based CRUD APIs using Flask and JSON.
- **gRPC** — strongly typed RPC communication using Protocol Buffers.

All services are containerized with Docker, and a benchmark compares REST and gRPC across repeated CRUD operations.

## Architecture

```text
communication/
├── tcp/
│   ├── client.py
│   ├── server.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── rest/
│   ├── app.py
│   ├── models.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── grpc/
│   ├── proto/
│   │   └── user_service.proto
│   ├── generated/
│   │   ├── user_service_pb2.py
│   │   └── user_service_pb2_grpc.py
│   ├── client.py
│   ├── server.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── benchmark.py
├── docker-compose.yml
└── README.md
```

## TCP Sockets

The TCP implementation demonstrates synchronous communication at the transport layer.

The server:

- Listens for incoming TCP connections.
- Accepts one client connection at a time.
- Receives a message using a blocking `recv()` call.
- Processes the message and returns a response.
- Handles connection and endpoint errors.

The client establishes a connection, sends a message, and blocks until the server responds.

```text
Client
  │
  │ TCP connection
  ▼
TCP Server
  │
  │ Process request
  ▼
Response
```

Failure scenarios were also tested, including:

- Connection to an unavailable port.
- Invalid hostname resolution.
- Connection timeout handling.

This implementation provides a baseline for understanding the lower-level networking behavior abstracted by REST and gRPC.

## REST API

The REST implementation uses **Flask**, **HTTP**, and **JSON** to expose CRUD operations for user resources.

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/users` | Retrieve all users |
| `GET` | `/api/users/<id>` | Retrieve a user |
| `POST` | `/api/users` | Create a user |
| `PUT` | `/api/users/<id>` | Update a user |
| `DELETE` | `/api/users/<id>` | Delete a user |

The API also handles invalid requests and missing resources.

```text
Client
  │
  │ HTTP + JSON
  ▼
Flask REST API
  │
  │ CRUD operation
  ▼
JSON Response
```

Compared with raw sockets, REST provides a standardized application-level interface through HTTP methods, resource-oriented endpoints, status codes, and JSON serialization.

## gRPC

The gRPC implementation exposes equivalent CRUD operations through a strongly typed service contract defined in Protocol Buffers.

```text
Client
  │
  │ gRPC
  │ Protocol Buffers
  ▼
UserService
  │
  │ RPC
  ▼
Response
```

The service definition is stored in:

```text
grpc/proto/user_service.proto
```

Generated Python stubs are used by both the client and server.

The implementation demonstrates:

- Protocol Buffer message definitions.
- Generated client and server interfaces.
- Synchronous RPC calls.
- Structured gRPC error handling.
- Binary serialization.

## REST vs gRPC Benchmark

A benchmark was implemented to compare REST and gRPC under the same environment.

The benchmark executes **100 complete CRUD cycles** against each service.

Run the benchmark with:

```bash
python benchmark.py
```

### Results

| Protocol | Total Time | Average per Operation |
|---|---:|---:|
| REST | 0.631 s | 6.31 ms |
| gRPC | 0.090 s | 0.90 ms |

In this experiment, gRPC completed the workload approximately **7.03× faster** than REST.

```text
REST   6.31 ms/op  ███████████████████████████████
gRPC   0.90 ms/op  ████
```

These measurements are specific to this experiment and local test environment rather than a general performance guarantee.

The observed difference is consistent with several architectural differences between the two implementations:

- REST exchanges JSON payloads over HTTP.
- gRPC uses Protocol Buffers for binary serialization.
- gRPC provides a compact, strongly typed service contract.

## Running the Experiment

### Start the services

From the `communication` directory:

```bash
docker compose up --build
```

This starts the containerized communication services defined in `docker-compose.yml`.

### Run the benchmark

Once the REST and gRPC services are available:

```bash
python benchmark.py
```

The script performs repeated CRUD operations against both implementations and reports total and average execution times.

## Key Takeaways

This experiment demonstrates how the same synchronous request-response model can be implemented at different abstraction levels.

**TCP sockets** provide direct control over network communication but require manual handling of connections, message formats, and failures.

**REST** provides a simple and widely understood HTTP interface with human-readable JSON payloads, at the cost of additional protocol and serialization overhead.

**gRPC** provides strongly typed service contracts and compact binary serialization. In this experiment, it also produced substantially lower request latency than the REST implementation.

The comparison highlights an important distributed-systems design principle: communication mechanisms should be selected based on system requirements rather than abstraction level or raw performance alone.

## Tech Stack

- Python
- TCP Sockets
- Flask
- REST / HTTP
- gRPC
- Protocol Buffers
- Docker
- Docker Compose