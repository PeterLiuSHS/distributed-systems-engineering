# Replication & Consistency

A hands-on exploration of **replication, consistency, and failure recovery** using a three-node MongoDB replica set.

The experiments evaluate how different write concerns affect latency and durability, observe primary election during node failure, and explore consistency behavior through different read and write configurations.

## Overview

This module focuses on distributed data management using **MongoDB Replica Sets** and **PyMongo**.

The experiments cover:

- Leader-follower replication
- Replica set initialization and primary election
- Write concerns (`w=1`, `w=majority`, `w=3`)
- Replication latency and durability trade-offs
- Primary failure and automatic re-election
- Strong consistency
- Eventual consistency
- Causal consistency
- Read preference behavior

The MongoDB cluster is containerized with Docker Compose to provide a reproducible three-node distributed database environment.

## Architecture

```text
                    MongoDB Replica Set
                         RF = 3

                       ┌─────────┐
                  ┌───►│Secondary│
                  │    │ mongo2  │
                  │    └─────────┘
                  │
┌────────┐    ┌───┴─────┐
│ Python │───►│ Primary │
│ Client │    │ mongo1  │
└────────┘    └───┬─────┘
                  │
                  │    ┌─────────┐
                  └───►│Secondary│
                       │ mongo3  │
                       └─────────┘
```

The exact node acting as primary may change after an election.

All writes are initially directed to the current primary and replicated to the secondary nodes.

## Repository Structure

```text
replication-consistency/
├── docker-compose.yml
├── setup_replica_set.py
├── replication_test.py
├── leader_follower_test.py
├── strong_consistency_test.py
├── eventual_consistency_test.py
├── causal_consistency_test.py
├── read_preference_test.py
└── README.md
```

## Replica Set Setup

The experiment uses a MongoDB replica set containing:

- **1 primary node**
- **2 secondary nodes**
- **Replication factor: 3**

Docker Compose is used to start the MongoDB nodes, after which the replica set is initialized and MongoDB automatically elects a primary.

A Python setup script inserts an initial dataset and verifies that records written to the primary are replicated to secondary nodes.

This provides the baseline environment for the remaining consistency and failure experiments.

## Write Concern Experiment

MongoDB write concern controls how many replica-set members must acknowledge a write before it is considered successful.

Three configurations were tested:

| Write Concern | Required Acknowledgment |
|---|---|
| `w=1` | Primary only |
| `w=majority` | Majority of replica-set members |
| `w=3` | All three nodes |

Each configuration was tested with **500 write operations**, and the write latency was measured.

### Results

| Write Concern | Avg Latency | Max Latency | Min Latency | Std. Dev. |
|---|---:|---:|---:|---:|
| `w=1` | 1.210 ms | 13.695 ms | 0.915 ms | 0.626 ms |
| `w=majority` | 1.579 ms | 13.718 ms | 1.256 ms | 0.814 ms |
| `w=3` | 2.042 ms | 4.106 ms | 1.802 ms | 0.181 ms |

The observed average latency followed:

```text
w=1 < w=majority < w=3
```

This reflects the additional acknowledgment required as the write concern becomes stricter.

```text
w=1
Client ──► Primary ✓
           │
           └──── replication continues


w=majority
Client ──► Primary ✓
           │
           └──── Secondary ✓


w=3
Client ──► Primary ✓
           ├──── Secondary ✓
           └──── Secondary ✓
```

The experiment demonstrates the trade-off between **write latency and acknowledgment requirements**: waiting for more replica members increases the work required before a write is acknowledged.

## Primary Failure & Leader Election

The next experiment evaluates the behavior of the replica set when the current primary becomes unavailable.

The active primary container was manually stopped to simulate node failure.

```bash
docker stop <primary-container>
```

MongoDB detected the failure and initiated a new election among the remaining replica-set members.

### Observed Result

```text
Primary failure
      │
      ▼
Primary unavailable
      │
      ▼
Replica-set election
      │
      │ ~4.5 seconds
      ▼
New primary elected
      │
      ▼
Writes resume
```

The measured election duration was approximately:

```text
4531.728 ms
≈ 4.5 seconds
```

Write operations were temporarily unavailable while the election was in progress.

After the new primary was elected, writes using `w=majority` succeeded again.

A subsequent record-count verification showed consistent data across the newly elected primary and a secondary node after the test.

This experiment demonstrates automatic leader election and recovery in a replicated database while also showing the temporary availability impact of primary failure.

## Consistency Experiments

Several experiments were implemented to explore how read and write configuration affects the visibility of replicated data.

### Strong Consistency

The strong-consistency experiment uses stricter read/write settings so that reads observe acknowledged data from the replica set.

The experiment demonstrates the additional coordination required when applications prioritize consistent reads over immediate availability.

### Eventual Consistency

The eventual-consistency experiment reads from replicated nodes where updates may not become visible immediately.

This demonstrates an important property of asynchronous replication:

```text
Write to Primary
      │
      ▼
Primary updated
      │
      ├────────► Secondary
      │              │
      │              ▼
      │        replication delay
      │
      └────────► Secondary
```

A secondary can temporarily expose an older state until replication catches up.

The replicas eventually converge once the update has propagated.

### Causal Consistency

The causal-consistency experiment explores maintaining ordering between logically related operations.

A client session is used so that operations belonging to the same causal sequence can observe the required ordering relationship.

Conceptually:

```text
Operation A
    │
    ▼
Operation B depends on A
    │
    ▼
B should observe the effects of A
```

This provides stronger ordering guarantees for related operations without requiring every operation in the system to behave as a globally serialized transaction.

## Read Preference

MongoDB read preference determines which replica-set members are eligible to serve reads.

The experiments explore different read-routing behavior between the primary and secondary nodes.

This demonstrates another distributed-system trade-off:

```text
Primary reads
    │
    └── prioritize the latest primary state

Secondary reads
    │
    └── distribute read traffic but may observe replication lag
```

Read preference therefore affects both system scalability and the consistency characteristics visible to an application.

## Running the Experiments

Start the MongoDB cluster:

```bash
docker compose up -d
```

Initialize the replica set and baseline data:

```bash
python setup_replica_set.py
```

Run the replication and write-concern experiment:

```bash
python replication_test.py
```

Run individual consistency experiments:

```bash
python strong_consistency_test.py
python eventual_consistency_test.py
python causal_consistency_test.py
python read_preference_test.py
```

Run the leader-follower failure experiment:

```bash
python leader_follower_test.py
```

> The exact execution environment and container networking configuration are defined in `docker-compose.yml`.

## Key Takeaways

This module demonstrates several fundamental trade-offs in distributed data systems.

**Replication improves fault tolerance**, but introduces coordination and synchronization between replicas.

**Write concern affects latency and acknowledgment guarantees.** In this experiment, average write latency increased from **1.210 ms with `w=1`** to **2.042 ms with `w=3`** as additional replica acknowledgments were required.

**Leader election enables automatic recovery**, but failover is not instantaneous. The experiment observed approximately **4.5 seconds** of temporary write unavailability before a new primary was elected.

**Consistency is configurable rather than absolute.** Read preference, write concern, and session behavior allow applications to make different trade-offs between consistency, latency, and availability.

Together, these experiments demonstrate why distributed database configuration should be driven by application requirements rather than relying on a single consistency strategy.

## Tech Stack

- Python
- MongoDB
- PyMongo
- MongoDB Replica Sets
- Docker
- Docker Compose