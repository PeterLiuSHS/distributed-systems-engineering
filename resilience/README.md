# Resilience & Fault Tolerance

A hands-on experiment exploring **failure handling, retry strategies, circuit breaking, and recovery** in a distributed system deployed on Kubernetes.

The experiment begins with a deliberately unreliable backend and a baseline client with no resilience mechanisms. It then introduces **exponential backoff, jitter, and a Circuit Breaker** to observe how these patterns change system behavior under transient and persistent failures.

## Overview

This module explores common resilience patterns used in distributed systems:

- Failure and latency injection
- Client-side timeouts
- Retry
- Exponential backoff
- Jitter
- Circuit Breaker
- Graceful degradation
- Kubernetes service discovery
- Containerized deployment
- Failure and recovery testing

The goal is to compare a baseline client with a resilience-aware client under the same backend failure conditions.

## Architecture

```text
                   Kubernetes Cluster

        ┌───────────────────────────────┐
        │                               │
        │   ┌─────────────────────┐     │
        │   │    Client Service   │     │
        │   │                     │     │
        │   │  Baseline Client    │     │
        │   │       or            │     │
        │   │  Resilient Client   │     │
        │   └──────────┬──────────┘     │
        │              │                │
        │              │ HTTP           │
        │              ▼                │
        │   ┌─────────────────────┐     │
        │   │   backend-service   │     │
        │   │    ClusterIP        │     │
        │   └──────────┬──────────┘     │
        │              │                │
        │              ▼                │
        │   ┌─────────────────────┐     │
        │   │   Backend Service   │     │
        │   │                     │     │
        │   │ Delay / 500 / OK    │     │
        │   └─────────────────────┘     │
        │                               │
        └───────────────────────────────┘
```

## Repository Structure

```text
resilience/
├── backend-service/
│   ├── backend_service.py
│   └── requirements.txt
│
├── client-service/
│   ├── client_baseline.py
│   ├── client_resilient.py
│   ├── requirements-baseline.txt
│   └── requirements-resilient.txt
│
├── Dockerfiles/
│   ├── Dockerfile.backend
│   ├── Dockerfile.client-baseline
│   └── Dockerfile.client-resilient
│
├── kubernetes/
│   ├── backend-deployment.yaml
│   ├── client-baseline.yaml
│   └── client-resilient.yaml
│
└── README.md
```

## Failure Injection

The backend intentionally simulates unreliable service behavior through its `/data` endpoint.

Each request produces one of three outcomes:

| Backend Behavior | Configured Probability |
|---|---:|
| 5-second delay | 40% |
| HTTP 500 error | 40% |
| Successful response | 20% |

The delayed response simulates a slow or overloaded downstream service, while HTTP 500 responses simulate application-level failures.

The backend also exposes a `/health` endpoint for health checks.

This controlled fault model makes it possible to compare baseline and resilient client behavior under the same failure conditions.

## Baseline Client

The baseline client communicates with the backend using normal HTTP requests with a:

```text
2-second timeout
```

It contains no:

- Retry mechanism
- Circuit Breaker
- Backoff strategy
- Failure recovery logic

Conceptually:

```text
Client
   │
   ├── Request ──► Success ──► Continue
   │
   ├── Request ──► HTTP 500 ──► Fail
   │
   └── Request ──► Slow Backend
                         │
                         │ wait 2 seconds
                         ▼
                      Timeout
```

### Baseline Results

A baseline run of **50 consecutive requests** produced:

| Result | Count | Percentage |
|---|---:|---:|
| Successful | 11 | 22% |
| HTTP 500 | 11 | 22% |
| Timeout | 28 | 56% |
| **Total** | **50** | **100%** |

Successful requests completed quickly under normal backend conditions, while delayed requests occupied the client until the configured timeout expired.

The baseline demonstrates the effect of directly exposing a client to downstream failures: transient backend problems immediately become client-visible failures.

## Resilient Client

The resilient client introduces two complementary mechanisms:

```text
              Request
                 │
                 ▼
         ┌───────────────┐
         │ Circuit       │
         │ Breaker       │
         └───────┬───────┘
                 │ CLOSED
                 ▼
         ┌───────────────┐
         │ HTTP Request  │
         └───────┬───────┘
                 │ failure
                 ▼
         ┌───────────────┐
         │ Retry         │
         │ + Backoff     │
         │ + Jitter      │
         └───────────────┘
```

The two mechanisms address different failure patterns:

- **Retries** attempt to recover from transient failures.
- **Circuit Breaker** limits repeated calls when failures persist.

## Retry with Exponential Backoff & Jitter

Retries were implemented using **Tenacity**.

The experiment configured:

| Setting | Value |
|---|---|
| Maximum attempts | 3 |
| Initial backoff | ~1 second |
| Maximum backoff | 4 seconds |
| Jitter | Randomized |

Instead of retrying immediately after a failure, the client waits before another attempt.

Conceptually:

```text
Request
   │
   ▼
Failure
   │
   ▼
Wait ~1s + jitter
   │
   ▼
Retry
   │
   ▼
Failure
   │
   ▼
Wait ~2s + jitter
   │
   ▼
Retry
```

Observed retry intervals included patterns such as:

```text
1.3s → 2.7s
1.4s → 2.8s
1.6s → 2.6s
```

The increasing delay demonstrates exponential backoff, while variation between attempts demonstrates jitter.

Jitter is useful because multiple clients retrying at exactly the same intervals can create synchronized retry bursts against a recovering service.

## Circuit Breaker

The Circuit Breaker was implemented using **PyBreaker**.

The experiment used:

| Setting | Value |
|---|---:|
| Failure threshold | 3 consecutive failures |
| Reset timeout | 15 seconds |

The breaker transitions between three states:

```text
             failures reach threshold
       ┌───────────────────────────────┐
       │                               ▼
    CLOSED                           OPEN
       ▲                               │
       │                               │ 15 seconds
       │                               ▼
       └──────── success ───────── HALF-OPEN
```

### Observed State Transition

During testing:

```text
Requests #5–#7
    │
    └── consecutive failures
              │
              ▼
        Circuit OPEN

Requests #8–#14
    │
    └── fail fast without calling backend

~15 seconds
    │
    ▼
Circuit HALF-OPEN

Request #15
    │
    └── test request succeeds
              │
              ▼
        Circuit CLOSED
```

When the breaker was open, requests failed immediately instead of repeatedly waiting for an unhealthy backend.

This prevents unnecessary calls to a persistently failing downstream service and avoids repeatedly consuming client resources on requests unlikely to succeed.

## Combining Retry and Circuit Breaker

Retry and Circuit Breaker solve related but different problems.

```text
                 Backend Failure
                       │
             ┌─────────┴─────────┐
             │                   │
       Transient Failure   Persistent Failure
             │                   │
             ▼                   ▼
           Retry          Circuit Breaker
             │                   │
       Backoff + Jitter       Fail Fast
             │                   │
             └─────────┬─────────┘
                       ▼
                Resilient Client
```

Retries provide another opportunity for requests affected by temporary failures.

If failures continue, they contribute to the Circuit Breaker's failure count. Once the configured threshold is reached, the breaker opens and temporarily stops calls to the backend.

This creates layered failure handling:

```text
Transient fault
      ↓
Retry
      ↓
Backoff + jitter
      ↓
Persistent failures
      ↓
Circuit opens
      ↓
Fail fast
      ↓
Half-open probe
      ↓
Recovery
```

## Kubernetes Deployment

All components are containerized with Docker and deployed to Kubernetes.

Kubernetes provides internal service discovery through the `backend-service` Service resource.

```text
Client Pod
    │
    │ HTTP
    ▼
backend-service
  (ClusterIP)
    │
    ▼
Backend Pod
```

Separate Kubernetes manifests are provided for:

- Backend deployment and service
- Baseline client
- Resilient client

This allows both client implementations to be tested against the same backend environment.

## Failure & Recovery Testing

The experiment also tests infrastructure-level failure by intentionally terminating backend Pods.

This complements application-level fault injection:

```text
Application-level failures
    ├── HTTP 500
    └── Slow response / timeout

Infrastructure-level failure
    └── Backend Pod termination
```

Kubernetes detects the failed workload and recreates the required Pod according to the Deployment configuration.

This demonstrates the distinction between two layers of resilience:

```text
Application Layer
├── Retry
├── Exponential Backoff
├── Jitter
└── Circuit Breaker

Infrastructure Layer
└── Kubernetes workload recovery
```

Application-level resilience handles failures during service communication, while Kubernetes handles failed workload instances.

## Running the Experiment

Build the required Docker images using the Dockerfiles in:

```text
Dockerfiles/
```

Deploy the backend:

```bash
kubectl apply -f kubernetes/backend-deployment.yaml
```

Run the baseline client:

```bash
kubectl apply -f kubernetes/client-baseline.yaml
```

Observe its behavior:

```bash
kubectl logs -f deployment/client-baseline
```

Then deploy the resilient client:

```bash
kubectl apply -f kubernetes/client-resilient.yaml
```

Observe Circuit Breaker and retry behavior:

```bash
kubectl logs -f deployment/client-resilient
```

Kubernetes resources can be inspected with:

```bash
kubectl get pods
kubectl get services
```

## Key Takeaways

This experiment demonstrates that resilience in distributed systems requires protection at multiple layers.

**Timeouts bound how long a client waits**, but timeout handling alone does not recover failed requests.

**Retries can recover transient failures**, but uncontrolled retries can increase pressure on an already unhealthy service.

**Exponential backoff and jitter make retries safer** by spacing repeated attempts and reducing synchronized retry behavior.

**Circuit Breakers protect against persistent failures** by temporarily stopping calls to an unhealthy downstream dependency and failing fast.

**Kubernetes provides infrastructure-level recovery**, while application-level resilience patterns determine how services behave while failures are occurring.

The experiment highlights that fault tolerance is not a single mechanism but a combination of strategies addressing different failure modes.

## Tech Stack

- Python
- Flask
- HTTP / REST
- PyBreaker
- Tenacity
- Docker
- Kubernetes