# Distributed Systems Engineering

Hands-on experiments exploring core distributed systems concepts through service communication, replication, consistency, resilience, and container orchestration.

The repository brings together four implementations covering **TCP, REST, gRPC, MongoDB replication, consistency models, fault tolerance, Docker, and Kubernetes**.

---

## Overview

This project explores how distributed applications communicate, remain consistent, recover from failures, and run across containerized environments.

The experiments progress through four areas:

| Module | Focus | Technologies |
|---|---|---|
| 01 | Service Communication & Benchmarking | TCP, REST, gRPC, Protobuf, Docker |
| 02 | Replication & Consistency | MongoDB Replica Set, Write Concern, Read Preference |
| 03 | Service Resilience | Retry, Exponential Backoff, Jitter, Circuit Breaker |
| 04 | Containerized Microservices | FastAPI, Docker, Kubernetes, Ingress |

---

## 01 — Service Communication

Implemented equivalent client-server communication using three different approaches:

- Raw TCP sockets
- REST over HTTP
- gRPC with Protocol Buffers

The services were containerized and benchmarked to compare communication overhead and latency.

### What I explored

- Socket-based client/server communication
- HTTP request/response communication
- RPC using strongly typed Protobuf contracts
- Docker networking between services
- Latency and throughput benchmarking

### Technologies

`Python` `TCP` `REST` `gRPC` `Protocol Buffers` `Docker`

---

## 02 — Replication & Consistency

Built a **three-node MongoDB replica set** to explore replication, consistency, durability, and failure recovery.

Experiments included different write concerns:

```text
w = 1
w = majority
w = all
```

and different read/consistency behaviors.

### What I explored

- Primary/secondary replication
- Replica synchronization
- Write concern and durability trade-offs
- Strong and eventual consistency
- Causal consistency
- Read preferences
- Primary failure and automatic election

A primary failure was simulated to observe election behavior and verify that writes could continue after a new primary was elected.

### Technologies

`MongoDB` `Python` `Docker` `Replica Sets`

---

## 03 — Service Resilience

Implemented resilience mechanisms for communication between distributed services.

The client handles temporary backend failures using:

```text
Request
   │
   ▼
Backend Failure
   │
   ▼
Retry
   │
   ▼
Exponential Backoff + Jitter
   │
   ▼
Circuit Breaker
```

### What I explored

- Retry policies
- Exponential backoff
- Randomized jitter
- Circuit breaker states
- Failure simulation
- Recovery after temporary service outages

The services were containerized and deployed in a Kubernetes environment to test behavior under service failures.

### Technologies

`Python` `FastAPI` `Docker` `Kubernetes`

---

## 04 — Kubernetes Microservices

Built a small distributed application consisting of independent **Book** and **Order** services.

```text
                Client
                   │
                   ▼
                Ingress
                   │
             ┌─────┴─────┐
             │           │
             ▼           ▼
       Order Service   Book Service
             │           ▲
             │           │
             └── HTTP ───┘
```

The Order service communicates with the Book service to validate books and update inventory while processing orders.

### What I explored

- Service-to-service HTTP communication
- Independent FastAPI services
- Docker containerization
- Kubernetes Deployments
- Kubernetes Services
- Internal service discovery
- Ingress routing

### Technologies

`FastAPI` `Python` `Docker` `Kubernetes`

---

## Repository Structure

```text
distributed-systems-engineering/
│
├── communication/
│   ├── tcp/
│   ├── rest/
│   ├── grpc/
│   └── ...
│
├── replication-consistency/
│   └── ...
│
├── resilience/
│   └── ...
│
├── kubernetes-microservices/
│   ├── book-service/
│   ├── order-service/
│   └── kubernetes/
│
└── README.md
```

---

## Key Takeaways

These experiments helped me understand distributed systems beyond individual APIs and services, particularly the engineering trade-offs between:

- REST, raw TCP, and gRPC communication
- Performance and protocol complexity
- Consistency and availability
- Write durability and latency
- Failure recovery and service resilience
- Local containers and orchestrated deployments

Rather than treating these concepts independently, the project explores how communication, data replication, failure handling, and deployment interact in distributed applications.

---

## Tech Stack

**Languages**

`Python`

**Communication**

`TCP` `HTTP/REST` `gRPC` `Protocol Buffers`

**Data**

`MongoDB` `Replica Sets`

**Resilience**

`Retry` `Exponential Backoff` `Jitter` `Circuit Breaker`

**Infrastructure**

`Docker` `Docker Compose` `Kubernetes`

---

## Background

This repository consolidates distributed systems experiments completed as part of **COMP41720**, reorganized by engineering topic for easier exploration and comparison.
