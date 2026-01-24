# Redis Data Structures Demo

## Overview

A comprehensive demonstration of Redis data types and commands. This guide covers all major Redis data structures with practical examples and use cases.

**What You'll Learn:**
- All 9 Redis data types and when to use each
- Essential commands for each data structure
- Time complexity and performance characteristics
- Real-world use cases and patterns

---

## Environment Setup

```bash
# Option 1: Docker Compose (Recommended)
docker-compose up -d

# Connect to Redis CLI
docker exec -it redis-demo redis-cli

# Option 2: Docker standalone
docker run -d --name redis-demo -p 6379:6379 redis:latest
docker exec -it redis-demo redis-cli

# Option 3: Local installation (Ubuntu/Debian)
sudo apt-get install redis-server
redis-cli
```

---

## Part 1: Strings

**Description**: The most basic Redis data type. Can store text, numbers, serialized JSON, or binary data (max 512 MB).

**Use Cases**: Sessions, caching, counters, locks

```redis
# Basic operations
SET greeting "Hello, Redis!"
GET greeting

# Set with expiration (seconds)
SET session:token "abc123xyz" EX 60
TTL session:token

# Conditional set (NX = only if not exists, XX = only if exists)
SET lock:resource "process-1" NX
SET lock:resource "process-updated" XX

# Numeric operations
SET counter 100
INCR counter
INCRBY counter 10
DECR counter
INCRBYFLOAT price 0.50

# String manipulation
APPEND message " World!"
STRLEN message
GETRANGE message 0 4

# Multiple keys
MSET user:1:name "Alice" user:1:email "alice@example.com"
MGET user:1:name user:1:email

# JSON storage
SET user:profile '{"id":1,"name":"John","roles":["admin","user"]}'
```

**Key Commands**: `GET`, `SET`, `MGET`, `MSET`, `INCR`, `INCRBY`, `APPEND`, `EXPIRE`

**Time Complexity**: O(1) for most operations

---

## Part 2: Lists

**Description**: Ordered collections implemented as linked lists. Can contain duplicates.

**Use Cases**: Recent items, activity feeds, message queues, logs

```redis
# Push operations
LPUSH tasks "task-1" "task-2" "task-3"    # Add to head
RPUSH tasks "task-4" "task-5"              # Add to tail
LRANGE tasks 0 -1                          # Get all

# Pop operations
LPOP tasks              # Remove from head
RPOP tasks              # Remove from tail
LPOP tasks 2            # Pop multiple

# Access by index
LINDEX fruits 0         # First element
LINDEX fruits -1        # Last element
LRANGE fruits 0 2       # Range of elements

# Modify list
LSET fruits 1 "blueberry"                  # Set by index
LINSERT fruits BEFORE "cherry" "banana"    # Insert
LREM fruits 1 "apple"                      # Remove by value

# Bounded list pattern
LPUSH logs "new-log"
LTRIM logs 0 99         # Keep only last 100

# List info
LLEN fruits
LPOS fruits "cherry"
```

**Key Commands**: `LPUSH`, `RPUSH`, `LPOP`, `RPOP`, `LRANGE`, `LTRIM`, `LINDEX`, `LLEN`

**Time Complexity**: O(1) for push/pop, O(N) for range operations

---

## Part 3: Sets

**Description**: Unordered collections of unique elements. No duplicates allowed.

**Use Cases**: Tags, categories, unique visitors, relationships

```redis
# Basic operations
SADD colors "red" "green" "blue"
SMEMBERS colors
SISMEMBER colors "red"      # Check membership
SREM colors "green"         # Remove element

# Set info
SCARD colors                # Count elements
SRANDMEMBER colors 2        # Random elements
SPOP colors                 # Pop random element

# Set operations (powerful!)
SADD set:A 1 2 3 4 5
SADD set:B 4 5 6 7 8

SUNION set:A set:B          # All elements from both
SINTER set:A set:B          # Only common elements
SDIFF set:A set:B           # Elements in A but not B

# Store results
SUNIONSTORE set:all set:A set:B
SINTERSTORE set:common set:A set:B
```

**Key Commands**: `SADD`, `SMEMBERS`, `SISMEMBER`, `SREM`, `SINTER`, `SUNION`, `SDIFF`, `SCARD`

**Time Complexity**: O(1) for add/remove/check, O(N) for members

---

## Part 4: Hashes

**Description**: Maps of field-value pairs, like objects or dictionaries.

**Use Cases**: User profiles, shopping carts, configuration, any object-like data

```redis
# Basic operations
HSET user:100 name "Alice" email "alice@example.com" age 28
HGET user:100 name
HGETALL user:100

# Get keys/values
HKEYS user:100
HVALS user:100
HMGET user:100 name age

# Modify fields
HSETNX user:100 country "USA"      # Set if not exists
HINCRBY user:100 age 1             # Increment
HINCRBYFLOAT user:100 balance 25.75
HDEL user:100 city                 # Delete field

# Hash info
HLEN user:100
HEXISTS user:100 name
HSTRLEN user:100 email

# Use Case: Shopping Cart
HSET cart:user:1001 "product:201" 2 "product:202" 1
HINCRBY cart:user:1001 "product:201" 1
HGETALL cart:user:1001
```

**Key Commands**: `HSET`, `HGET`, `HGETALL`, `HMGET`, `HINCRBY`, `HDEL`, `HEXISTS`, `HLEN`

**Time Complexity**: O(1) for single field operations

---

## Part 5: Sorted Sets (ZSets)

**Description**: Like Sets but each element has a score. Automatically ordered by score (low to high).

**Use Cases**: Leaderboards, rankings, priority queues, rate limiters, time-series

```redis
# Add with scores
ZADD scores 85 "Alice" 92 "Bob" 78 "Charlie" 95 "Diana"

# Get elements
ZRANGE scores 0 -1 WITHSCORES        # Low to high
ZREVRANGE scores 0 -1 WITHSCORES     # High to low
ZREVRANGE scores 0 2 WITHSCORES      # Top 3

# Score operations
ZSCORE scores "Bob"
ZINCRBY scores 5 "Charlie"

# Rank operations
ZRANK scores "Diana"          # Rank (low to high)
ZREVRANK scores "Diana"       # Rank (high to low)

# Range queries
ZRANGEBYSCORE scores 80 90 WITHSCORES
ZCOUNT scores 80 90

# Remove operations
ZREM scores "Eve"
ZREMRANGEBYRANK leaderboard 0 1      # By rank
ZREMRANGEBYSCORE leaderboard 0 50    # By score

# Info
ZCARD scores
```

**Key Commands**: `ZADD`, `ZRANGE`, `ZREVRANGE`, `ZSCORE`, `ZRANK`, `ZINCRBY`, `ZRANGEBYSCORE`

**Time Complexity**: O(log N) for most operations

---

## Part 6: HyperLogLog

**Description**: Probabilistic data structure for cardinality estimation. Uses only 12KB regardless of elements counted. ~0.81% standard error.

**Use Cases**: Unique visitors, unique events, cardinality estimation

```redis
# Add elements
PFADD visitors "user:1" "user:2" "user:3"
PFCOUNT visitors

# Duplicates don't increase count
PFADD visitors "user:1" "user:2" "user:4" "user:5"
PFCOUNT visitors

# Merge multiple HyperLogLogs
PFADD day1:visitors "user:1" "user:2" "user:3"
PFADD day2:visitors "user:2" "user:3" "user:4"
PFMERGE week:visitors day1:visitors day2:visitors
PFCOUNT week:visitors
```

**Key Commands**: `PFADD`, `PFCOUNT`, `PFMERGE`

**Time Complexity**: O(1)

---

## Part 7: Bitmaps

**Description**: Not a separate type - uses Strings for bit-level operations. Very memory efficient for binary states.

**Use Cases**: Feature flags, user activity tracking, bloom filters, daily active users

```redis
# Set individual bits
SETBIT user:1:features 0 1
SETBIT user:1:features 2 1
SETBIT user:1:features 7 1

# Get individual bits
GETBIT user:1:features 0
GETBIT user:1:features 1

# Count set bits
BITCOUNT user:1:features

# Daily Active Users example
SETBIT daily:active:2024-01-15 1001 1
SETBIT daily:active:2024-01-15 1002 1
SETBIT daily:active:2024-01-16 1001 1
SETBIT daily:active:2024-01-16 1003 1

# Bitwise operations
BITOP AND active:both daily:active:2024-01-15 daily:active:2024-01-16
BITOP OR active:any daily:active:2024-01-15 daily:active:2024-01-16
BITCOUNT active:both
BITCOUNT active:any
```

**Key Commands**: `SETBIT`, `GETBIT`, `BITCOUNT`, `BITOP`

**Time Complexity**: O(1) for single bit, O(N) for BITCOUNT/BITOP

---

## Part 8: Streams

**Description**: Append-only log data structure. Each entry has an auto-generated ID (timestamp-sequence).

**Use Cases**: Event sourcing, message queues, activity logs, audit trails

```redis
# Add entries
XADD events * action "login" user "alice" ip "192.168.1.1"
XADD events * action "purchase" user "bob" product "item-123"
XADD events * action "logout" user "alice"

# Read stream
XRANGE events - +              # All entries
XRANGE events - + COUNT 2      # With limit
XREVRANGE events + -           # Reverse order

# Stream info
XLEN events
XINFO STREAM events

# Consumer groups (for distributed processing)
XGROUP CREATE events mygroup $ MKSTREAM
# XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS events >
# XACK events mygroup <message-id>
```

**Key Commands**: `XADD`, `XREAD`, `XRANGE`, `XLEN`, `XGROUP`, `XREADGROUP`, `XACK`

**Time Complexity**: O(1) for XADD, O(N) for range queries

---

## Part 9: Geospatial

**Description**: Store and query geographic coordinates. Uses sorted sets internally.

**Use Cases**: Finding nearby locations, distance calculations, location-based services

```redis
# Add locations (longitude, latitude, name)
GEOADD locations -122.4194 37.7749 "San Francisco"
GEOADD locations -118.2437 34.0522 "Los Angeles"
GEOADD locations -73.9857 40.7484 "New York"
GEOADD locations -87.6298 41.8781 "Chicago"

# Get coordinates
GEOPOS locations "San Francisco"

# Calculate distance
GEODIST locations "San Francisco" "Los Angeles" km
GEODIST locations "New York" "Chicago" mi

# Find nearby locations
GEOSEARCH locations FROMMEMBER "Los Angeles" BYRADIUS 500 km WITHDIST
GEOSEARCH locations FROMLONLAT -122.0 37.5 BYRADIUS 100 km WITHDIST

# Get geohash
GEOHASH locations "San Francisco" "New York"
```

**Key Commands**: `GEOADD`, `GEOPOS`, `GEODIST`, `GEOSEARCH`, `GEOHASH`

**Time Complexity**: O(log N) for most operations

---

## Part 10: Key Management & TTL

```redis
# TTL operations
SET temp:data "temporary value"
EXPIRE temp:data 60            # Set expiration
TTL temp:data                  # Check remaining time
PERSIST temp:data              # Remove expiration

# Key pattern matching
KEYS user:*                    # Find keys (avoid in production)
SCAN 0 MATCH user:* COUNT 10   # Non-blocking alternative

# Key info
TYPE user:100                  # Get data type
OBJECT ENCODING user:100       # Get encoding
MEMORY USAGE user:100          # Memory consumption

# Rename keys
RENAME old:key new:key
RENAMENX old:key new:key       # Only if new doesn't exist

# Delete
DEL key1 key2
EXISTS key1
```

---

## Part 11: Transactions

**Description**: MULTI/EXEC provides atomic execution of multiple commands.

```redis
# Basic transaction
SET account:A 1000
SET account:B 500

MULTI
DECRBY account:A 200
INCRBY account:B 200
EXEC

MGET account:A account:B

# Discard transaction
MULTI
SET test:key "value"
DISCARD

# Optimistic locking with WATCH
WATCH account:A
GET account:A
MULTI
DECRBY account:A 100
EXEC
UNWATCH
```

**Key Commands**: `MULTI`, `EXEC`, `DISCARD`, `WATCH`, `UNWATCH`

---

## Part 12: Pub/Sub

**Description**: Real-time messaging between clients. Messages are not persisted.

```redis
# Terminal 1: Subscribe
SUBSCRIBE news:sports news:tech

# Terminal 2: Publish
PUBLISH news:sports "Team A wins!"
PUBLISH news:tech "New release!"

# Pattern subscribe
PSUBSCRIBE news:*
```

**Key Commands**: `SUBSCRIBE`, `UNSUBSCRIBE`, `PUBLISH`, `PSUBSCRIBE`

---

## Summary Table

| Data Type | Description | Key Commands | Time Complexity |
|-----------|-------------|--------------|-----------------|
| **String** | Text, numbers, binary | GET, SET, INCR, MGET | O(1) |
| **List** | Ordered, allows duplicates | LPUSH, RPUSH, LRANGE, LTRIM | O(1) push, O(N) range |
| **Set** | Unique, unordered | SADD, SMEMBERS, SINTER, SUNION | O(1) add, O(N) members |
| **Hash** | Field-value pairs | HSET, HGET, HGETALL, HINCRBY | O(1) |
| **Sorted Set** | Unique with scores | ZADD, ZRANGE, ZRANK, ZINCRBY | O(log N) |
| **HyperLogLog** | Cardinality estimation | PFADD, PFCOUNT, PFMERGE | O(1) |
| **Bitmap** | Bit-level operations | SETBIT, GETBIT, BITCOUNT | O(1) per bit |
| **Stream** | Append-only log | XADD, XREAD, XRANGE | O(1) add, O(N) range |
| **Geospatial** | Geographic coordinates | GEOADD, GEODIST, GEOSEARCH | O(log N) |

---

## Performance Benchmark

```bash
# Built-in benchmark tool
redis-benchmark -t set,get -n 100000 -q

# With pipelining
redis-benchmark -t set,get -n 100000 -q -P 16
```

---

## Q&A

1. **Why Redis over a relational database for caching/sessions?**
   - Speed (in-memory), automatic expiration, no schema overhead

2. **What happens if Redis crashes?**
   - Data persistence options: RDB snapshots, AOF logging, or hybrid

3. **How does Redis handle concurrent writes?**
   - Single-threaded command processing (no locks needed), MULTI/EXEC for transactions

4. **When should you NOT use Redis?**
   - Complex queries, large datasets exceeding RAM, strong consistency requirements

5. **How does Redis scale?**
   - Redis Cluster for horizontal scaling, read replicas for read scaling