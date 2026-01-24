# Redis Cluster Demo

A 6-node Redis Cluster with 3 masters and 3 replicas for high availability and data sharding.

## Architecture

```
                         ┌─────────────────────────────────────┐
                         │          Redis Cluster              │
                         │        (16384 hash slots)           │
                         └─────────────────────────────────────┘
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        │                                 │                                 │
        ▼                                 ▼                                 ▼
┌───────────────┐                ┌───────────────┐                ┌───────────────┐
│   Master 1    │                │   Master 2    │                │   Master 3    │
│ 172.38.0.11   │                │ 172.38.0.12   │                │ 172.38.0.13   │
│  slots 0-5460 │                │ slots 5461-   │                │ slots 10923-  │
│               │                │     10922     │                │     16383     │
└───────┬───────┘                └───────┬───────┘                └───────┬───────┘
        │ replication                    │ replication                    │ replication
        ▼                                ▼                                ▼
┌───────────────┐                ┌───────────────┐                ┌───────────────┐
│   Replica 1   │                │   Replica 2   │                │   Replica 3   │
│ 172.38.0.14   │                │ 172.38.0.15   │                │ 172.38.0.16   │
│ (slave of M1) │                │ (slave of M2) │                │ (slave of M3) │
└───────────────┘                └───────────────┘                └───────────────┘
```

## Node Details

| Node | Role | IP Address | Host Port | Cluster Bus Port |
|------|------|------------|-----------|------------------|
| redis-1 | Master | 172.38.0.11 | 6371 | 16371 |
| redis-2 | Master | 172.38.0.12 | 6372 | 16372 |
| redis-3 | Master | 172.38.0.13 | 6373 | 16373 |
| redis-4 | Replica | 172.38.0.14 | 6374 | 16374 |
| redis-5 | Replica | 172.38.0.15 | 6375 | 16375 |
| redis-6 | Replica | 172.38.0.16 | 6376 | 16376 |

## Setup Instructions

### Step 1: Generate configuration files

```bash
sh config-generate.sh
```

This creates `redis/node-{1..6}/conf/redis.conf` with cluster settings.

### Step 2: Start all containers

```bash
docker-compose up -d
```

### Step 3: Verify containers are running

```bash
docker-compose ps
```

Expected output:
```
NAME                      IMAGE     COMMAND                  SERVICE   CREATED         STATUS         PORTS
redis-cluster-redis-1-1   redis     "docker-entrypoint.s…"   redis-1   6 seconds ago   Up 3 seconds   0.0.0.0:6371->6379/tcp, 0.0.0.0:16371->16379/tcp
redis-cluster-redis-2-1   redis     "docker-entrypoint.s…"   redis-2   6 seconds ago   Up 3 seconds   0.0.0.0:6372->6379/tcp, 0.0.0.0:16372->16379/tcp
redis-cluster-redis-3-1   redis     "docker-entrypoint.s…"   redis-3   6 seconds ago   Up 3 seconds   0.0.0.0:6373->6379/tcp, 0.0.0.0:16373->16379/tcp
redis-cluster-redis-4-1   redis     "docker-entrypoint.s…"   redis-4   6 seconds ago   Up 3 seconds   0.0.0.0:6374->6379/tcp, 0.0.0.0:16374->16379/tcp
redis-cluster-redis-5-1   redis     "docker-entrypoint.s…"   redis-5   6 seconds ago   Up 3 seconds   0.0.0.0:6375->6379/tcp, 0.0.0.0:16375->16379/tcp
redis-cluster-redis-6-1   redis     "docker-entrypoint.s…"   redis-6   6 seconds ago   Up 3 seconds   0.0.0.0:6376->6379/tcp, 0.0.0.0:16376->16379/tcp
```

### Step 4: Create the cluster

```bash
docker exec -it redis-cluster-redis-1-1 redis-cli --cluster create \
  172.38.0.11:6379 \
  172.38.0.12:6379 \
  172.38.0.13:6379 \
  172.38.0.14:6379 \
  172.38.0.15:6379 \
  172.38.0.16:6379 \
  --cluster-replicas 1
```

Type `yes` when prompted to accept the configuration.

### Step 5: Verify cluster status

```bash
# Connect to any node
docker exec -it redis-cluster-redis-1-1 redis-cli -c

# Check cluster info
CLUSTER INFO

# Check cluster nodes
CLUSTER NODES
```

Expected `CLUSTER NODES` output:
```
7c1daac52007f13d2fa57cc318c20f8990090def 172.38.0.12:6379@16379 master - 0 1769228262447 2 connected 5461-10922
6dc552316035032f52c864761680034757b32fd3 172.38.0.15:6379@16379 slave 250881a422b40a7308473d5886677ef5e84364bc 0 1769228263487 1 connected
c74d2ba06e7bd4d75eeeebf6c2f2d7be364c4e6f 172.38.0.14:6379@16379 slave 75c6e023f354cb4dc61efebee0a061cbbd131f76 0 1769228262000 3 connected
de43888ab239eb0df4163d7f1a3a1146b18992a7 172.38.0.16:6379@16379 slave 7c1daac52007f13d2fa57cc318c20f8990090def 0 1769228262000 2 connected
75c6e023f354cb4dc61efebee0a061cbbd131f76 172.38.0.13:6379@16379 master - 0 1769228263000 3 connected 10923-16383
250881a422b40a7308473d5886677ef5e84364bc 172.38.0.11:6379@16379 myself,master - 0 0 1 connected 0-5460
```

## Testing the Cluster

### Test data sharding

```bash
# Connect with cluster mode (-c flag)
docker exec -it redis-cluster-redis-1-1 redis-cli -c

# Set keys (will be redirected to correct node)
SET user:1 "Alice"
SET user:2 "Bob"
SET user:3 "Charlie"

# Get keys
GET user:1
GET user:2
GET user:3
```

Expected output:
```bash
127.0.0.1:6379> SET user:1 "Alice"
-> Redirected to slot [10778] located at 172.38.0.12:6379
OK
172.38.0.12:6379> SET user:2 "Bob"
OK
172.38.0.12:6379> SET user:3 "Charlie"
-> Redirected to slot [2648] located at 172.38.0.11:6379
OK
172.38.0.11:6379> GET user:1
-> Redirected to slot [10778] located at 172.38.0.12:6379
"Alice"
172.38.0.12:6379> GET user:2
"Bob"
172.38.0.12:6379> GET user:3
-> Redirected to slot [2648] located at 172.38.0.11:6379
"Charlie"
172.38.0.11:6379> 
```

### Check which slot a key belongs to

```bash
CLUSTER KEYSLOT user:1
CLUSTER KEYSLOT user:2
```

Expected output:
```bash
172.38.0.11:6379> CLUSTER KEYSLOT user:1
(integer) 10778
172.38.0.11:6379> CLUSTER KEYSLOT user:2
(integer) 6777
```

## Stop cluster

```bash
# Stop cluster
docker-compose down

# Stop and remove data
docker-compose down && rm -rf redis/
```
