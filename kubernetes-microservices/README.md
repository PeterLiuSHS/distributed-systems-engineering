# Kubernetes Microservices

A containerized **online bookstore system** built with FastAPI and deployed on Kubernetes.

The application is decomposed into two independently deployed services — **Book Service** and **Order Service** — that communicate synchronously over HTTP. The experiment explores service boundaries, inter-service communication, service discovery, replication, and load balancing in a Kubernetes environment.

## Overview

The system consists of two microservices:

- **Book Service** — manages book information and inventory.
- **Order Service** — manages orders and coordinates inventory validation and deduction with the Book Service.

When an order is created, the Order Service calls the Book Service to verify inventory and deduct stock before completing the order.

Both services are:

- Implemented with FastAPI
- Packaged as Docker images
- Deployed independently to Kubernetes
- Exposed through Kubernetes Services
- Configured with multiple Pod replicas

## Architecture

```text
                         Client
                            │
                            ▼
                         Ingress
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
          Order Service           Book Service
           ClusterIP               ClusterIP
                 │                     │
                 │                     │
          ┌──────┴──────┐       ┌──────┴──────┐
          │             │       │             │
          ▼             ▼       ▼             ▼
      Order Pod     Order Pod  Book Pod     Book Pod
          │                           ▲
          │                           │
          └────── HTTP / REST ────────┘
```

The Order Service communicates with the Book Service inside the cluster using Kubernetes service discovery:

```text
http://book-service:8001
```

This allows the Order Service to address the Book Service by service name rather than depending on individual Pod IP addresses.

## Repository Structure

```text
kubernetes-microservices/
├── book-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── models.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── order-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── models.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── kubernetes/
│   ├── book-service.yaml
│   ├── order-service.yaml
│   └── ingress.yaml
│
└── README.md
```

## Book Service

The Book Service owns book information and inventory state.

Its responsibilities include:

- Retrieving all books
- Retrieving an individual book
- Managing inventory
- Validating stock availability
- Deducting inventory during order processing

The service runs on:

```text
Port 8001
```

Inventory operations remain inside the Book Service boundary rather than being implemented directly by the Order Service.

## Order Service

The Order Service owns order-processing logic.

Its responsibilities include:

- Creating orders
- Retrieving existing orders
- Coordinating with the Book Service during order creation
- Returning errors when an order cannot be completed

The service runs on:

```text
Port 8000
```

When an order is submitted, the Order Service coordinates the following workflow:

```text
Client
   │
   │ Create Order
   ▼
Order Service
   │
   │ Check inventory
   ▼
Book Service
   │
   │ Stock available
   ▼
Deduct Inventory
   │
   ▼
Order Service
   │
   │ Complete order
   ▼
Client
```

This demonstrates synchronous service-to-service communication across independently deployed application components.

## Order & Inventory Workflow

A successful order was tested by submitting quantities for multiple books.

Before the order:

```text
Book 1 stock: 10
Book 2 stock: 5
```

The order requested:

```text
Book 1: quantity 2
Book 2: quantity 1
```

After processing:

```text
Book 1 stock: 8
Book 2 stock: 4
```

The resulting inventory change verified that the Order Service successfully communicated with the Book Service and that inventory was deducted as part of the order workflow.

## Error Handling

The system also handles orders requesting more inventory than is available.

For example:

```text
Requested quantity: 100
Available quantity: 8
```

The Book Service rejects the inventory operation and the order request returns:

```text
HTTP 409 Conflict
```

This prevents an order from being completed when sufficient inventory is unavailable.

## Docker Containerization

Each microservice has its own Dockerfile and dependency configuration.

```text
Book Service
    │
    └── Docker image
          │
          └── FastAPI :8001


Order Service
    │
    └── Docker image
          │
          └── FastAPI :8000
```

The images are built independently and loaded into a local **Kind (Kubernetes in Docker)** cluster for deployment.

This keeps each service independently deployable while providing a consistent runtime environment.

## Kubernetes Deployment

Each microservice is deployed using Kubernetes **Deployment** and **Service** resources.

Both deployments use:

```yaml
replicas: 2
```

resulting in:

```text
Book Service
├── Book Pod 1
└── Book Pod 2

Order Service
├── Order Pod 1
└── Order Pod 2
```

This creates multiple running instances of each service.

## Service Discovery

Kubernetes Services provide stable network identities for the underlying Pods.

For example, the Book Service is exposed internally through a ClusterIP Service:

```text
Order Service
      │
      │ http://book-service:8001
      ▼
book-service
   ClusterIP
      │
   ┌──┴──┐
   ▼     ▼
 Pod 1  Pod 2
```

The Order Service therefore does not need to know which individual Book Service Pod handles a request.

## Load Balancing

The experiment verified that both services were running with two replicas.

For the Book Service, the Kubernetes Service exposed multiple Pod endpoints behind a single ClusterIP address.

Conceptually:

```text
                  book-service
                   ClusterIP
                       │
                 ┌─────┴─────┐
                 │           │
                 ▼           ▼
             Book Pod 1   Book Pod 2
```

This allows requests addressed to the Service to be routed across the available backend Pods.

The experiment therefore demonstrates the relationship between:

- Deployments
- Replicas
- Pods
- Services
- Service endpoints

## Ingress

A basic Kubernetes Ingress resource is also included:

```text
Client
   │
   ▼
Ingress
   │
   ├──► Order Service
   │
   └──► Book Service
```

The Ingress provides an external routing layer in front of the internal services and provides a foundation for centralized HTTP routing as the application grows.

## Running the Project

### 1. Create a Kind cluster

```bash
kind create cluster --name bookstore-cluster
```

### 2. Build the Docker images

From the project directory:

```bash
docker build -t book-service:latest ./book-service
docker build -t order-service:latest ./order-service
```

### 3. Load the images into Kind

```bash
kind load docker-image book-service:latest --name bookstore-cluster
kind load docker-image order-service:latest --name bookstore-cluster
```

### 4. Deploy to Kubernetes

```bash
kubectl apply -f kubernetes/
```

### 5. Verify the deployment

```bash
kubectl get pods
kubectl get services
kubectl get deployments
```

All Book Service and Order Service Pods should reach the `Running` state.

### 6. Access the services locally

Port-forward the Order Service:

```bash
kubectl port-forward service/order-service 8000:8000
```

Port-forward the Book Service:

```bash
kubectl port-forward service/book-service 8001:8001
```

The APIs can then be tested through their local ports.

## Design Trade-offs

### Synchronous Communication

The Order Service uses synchronous HTTP calls to the Book Service.

This keeps the order workflow straightforward:

```text
Create Order
    ↓
Validate Inventory
    ↓
Deduct Inventory
    ↓
Complete Order
```

However, synchronous communication also introduces runtime coupling.

If the Book Service becomes unavailable or slow, order processing can also become unavailable or slow.

### Service Boundaries

Inventory and order processing are separated into different services:

```text
Book Service
└── Book data + inventory

Order Service
└── Order lifecycle
```

This separates the two responsibilities and allows them to be deployed independently.

At the same time, order creation crosses a service boundary, which introduces distributed coordination that would not exist in a single-process application.

## Key Takeaways

This experiment demonstrates how a small application changes when it is decomposed into independently deployed services.

**Service boundaries create independent components**, but operations spanning those boundaries require explicit communication and coordination.

**Kubernetes Services provide stable service discovery** while Pods remain replaceable deployment instances.

**Multiple replicas improve deployment redundancy and allow traffic to be distributed across service instances.**

**Synchronous REST communication is straightforward**, but introduces runtime dependency between upstream and downstream services.

**Container orchestration solves infrastructure-level concerns**, such as deployment, service discovery, and replica management, but does not eliminate application-level distributed-system concerns such as cross-service consistency and failure handling.

## Tech Stack

- Python
- FastAPI
- REST / HTTP
- Docker
- Kubernetes
- Kind
- Kubernetes Deployments
- Kubernetes Services
- Kubernetes Ingress