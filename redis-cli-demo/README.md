# Redis Demo: Real-Time E-Commerce Session & Cart Management

## Demo Overview

**Scenario**: Build a simplified e-commerce backend demonstrating Redis as a key-value store for session management, shopping cart, product caching, and real-time analytics.

**Why This Scenario?**
- Showcases multiple Redis data structures (Strings, Hashes, Lists, Sets, Sorted Sets)
- Demonstrates real-world use cases where Redis excels
- Highlights key-value database strengths: speed, simplicity, flexibility

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

# Option 3: Local installation
# Ubuntu/Debian
sudo apt-get install redis-server
redis-cli
```

---

## Demo Part 1: User Session Management (Strings + TTL)

**Use Case**: Store user sessions with automatic expiration

```redis
# Create a user session after login
SET session:user:1001 '{"userId":1001,"username":"john_doe","role":"customer","loginTime":"2024-01-15T10:30:00Z"}' EX 3600

# Check session exists
GET session:user:1001

# Check remaining TTL (Time To Live)
TTL session:user:1001

# Extend session on user activity
EXPIRE session:user:1001 3600

# Simulate logout - delete session
DEL session:user:1001

# Verify deletion
EXISTS session:user:1001
```

**Key Points**:
- O(1) time complexity for GET/SET
- Built-in expiration prevents memory leaks
- No need for cleanup jobs

---

## Demo Part 2: Shopping Cart (Hashes)

**Use Case**: Store shopping cart as hash with product quantities

```redis
# Add items to cart for user 1001
HSET cart:user:1001 product:101 2
HSET cart:user:1001 product:102 1
HSET cart:user:1001 product:103 3

# Get all cart items
HGETALL cart:user:1001

# Get specific product quantity
HGET cart:user:1001 product:101

# Update quantity (increment by 1)
HINCRBY cart:user:1001 product:101 1

# Remove item from cart
HDEL cart:user:1001 product:103

# Get cart item count
HLEN cart:user:1001

# Check if product exists in cart
HEXISTS cart:user:1001 product:102

# Set cart expiration (24 hours)
EXPIRE cart:user:1001 86400
```

**Key Points**:
- Hash is perfect for object-like data
- Atomic increment operations
- Memory efficient for small hashes

---

## Demo Part 3: Product Caching (Strings + JSON)

**Use Case**: Cache frequently accessed product data

```redis
# Cache product details
SET product:101 '{"id":101,"name":"Wireless Mouse","price":29.99,"stock":150,"category":"electronics"}' EX 300

SET product:102 '{"id":102,"name":"USB-C Cable","price":12.99,"stock":500,"category":"accessories"}' EX 300

SET product:103 '{"id":103,"name":"Mechanical Keyboard","price":89.99,"stock":75,"category":"electronics"}' EX 300

# Retrieve product
GET product:101

# Check multiple products at once (batch operation)
MGET product:101 product:102 product:103

# Simulate cache miss and refresh
DEL product:101
GET product:101
# Returns (nil) - indicates cache miss, fetch from database
```

**Key Points**:
- MGET reduces network round trips
- Short TTL ensures data freshness
- Cache-aside pattern demonstration

---

## Demo Part 4: Recently Viewed Products (Lists)

**Use Case**: Track user's browsing history with limited size

```redis
# User views products (most recent first)
LPUSH recent:user:1001 product:103
LPUSH recent:user:1001 product:101
LPUSH recent:user:1001 product:102
LPUSH recent:user:1001 product:105
LPUSH recent:user:1001 product:101

# Keep only last 5 items (remove duplicates logic would be in app)
LTRIM recent:user:1001 0 4

# Get recently viewed products
LRANGE recent:user:1001 0 -1

# Get only last 3 viewed
LRANGE recent:user:1001 0 2

# Check list length
LLEN recent:user:1001
```

**Key Points**:
- LPUSH + LTRIM pattern for bounded lists
- O(1) for push operations
- Efficient for activity feeds, logs

---

## Demo Part 5: Product Categories & Tags (Sets)

**Use Case**: Find products by category, implement tag-based filtering

```redis
# Add products to category sets
SADD category:electronics product:101 product:103 product:107
SADD category:accessories product:102 product:104 product:106
SADD category:gaming product:103 product:105 product:107

# Add tags to products
SADD tag:wireless product:101 product:105
SADD tag:usb product:102 product:104
SADD tag:rgb product:103 product:105 product:107

# Get all electronics products
SMEMBERS category:electronics

# Find products that are both electronics AND gaming
SINTER category:electronics category:gaming

# Find products that are electronics OR accessories
SUNION category:electronics category:accessories

# Find electronics that are NOT gaming
SDIFF category:electronics category:gaming

# Check if product is in category
SISMEMBER category:electronics product:101

# Count products in category
SCARD category:electronics
```

**Key Points**:
- Set operations (UNION, INTER, DIFF) are powerful
- Perfect for tagging, categorization, relationships
- O(1) membership check

---

## Demo Part 6: Product Leaderboard (Sorted Sets)

**Use Case**: Real-time product rankings by sales/views

```redis
# Add products with their sales count as score
ZADD leaderboard:sales 150 product:101
ZADD leaderboard:sales 89 product:102
ZADD leaderboard:sales 245 product:103
ZADD leaderboard:sales 178 product:104
ZADD leaderboard:sales 312 product:105

# Get top 3 best-selling products (highest scores)
ZREVRANGE leaderboard:sales 0 2 WITHSCORES

# Get rank of a specific product (0-indexed, reversed)
ZREVRANK leaderboard:sales product:103

# Increment sales count (atomic operation)
ZINCRBY leaderboard:sales 25 product:101

# Get products with sales between 100 and 200
ZRANGEBYSCORE leaderboard:sales 100 200 WITHSCORES

# Get total number of products in leaderboard
ZCARD leaderboard:sales

# Remove product from leaderboard
ZREM leaderboard:sales product:102
```

**Key Points**:
- Sorted sets maintain order automatically
- O(log N) for most operations
- Perfect for rankings, rate limiters, priority queues

---

## Demo Part 7: Real-Time Analytics (HyperLogLog + Pub/Sub)

**Use Case**: Count unique visitors and broadcast events

```redis
# Count unique daily visitors (probabilistic)
PFADD visitors:2024-01-15 user:1001
PFADD visitors:2024-01-15 user:1002
PFADD visitors:2024-01-15 user:1001  # Duplicate - won't increase count
PFADD visitors:2024-01-15 user:1003
PFADD visitors:2024-01-15 user:1004

# Get approximate unique count
PFCOUNT visitors:2024-01-15

# Merge multiple days for weekly count
PFADD visitors:2024-01-14 user:1001 user:1005 user:1006
PFMERGE visitors:week visitors:2024-01-14 visitors:2024-01-15
PFCOUNT visitors:week
```

### Pub/Sub Demo (requires two terminals)

```redis
# Terminal 1: Subscribe to order events
SUBSCRIBE orders:new

# Terminal 2: Publish order event
PUBLISH orders:new '{"orderId":5001,"userId":1001,"total":129.99}'
```

**Key Points**:
- HyperLogLog uses only 12KB regardless of count
- 0.81% standard error - acceptable for analytics
- Pub/Sub enables real-time event broadcasting

---

## Demo Part 8: Atomic Transactions

**Use Case**: Transfer inventory between warehouses atomically

```redis
# Set initial inventory
SET inventory:warehouse:A:product:101 100
SET inventory:warehouse:B:product:101 50

# Atomic transfer of 20 units from A to B
MULTI
DECRBY inventory:warehouse:A:product:101 20
INCRBY inventory:warehouse:B:product:101 20
EXEC

# Verify results
GET inventory:warehouse:A:product:101
GET inventory:warehouse:B:product:101

# Demonstrate WATCH for optimistic locking
WATCH inventory:warehouse:A:product:101
# If another client modifies this key before EXEC, transaction aborts
MULTI
DECRBY inventory:warehouse:A:product:101 10
EXEC
```

**Key Points**:
- MULTI/EXEC provides atomic execution
- WATCH enables optimistic concurrency control
- All or nothing execution

---

## Demo Part 9: Performance Benchmark

**Use Case**: Show Redis speed advantage

```bash
# Built-in benchmark tool
redis-benchmark -t set,get -n 100000 -q

# Expected output shows operations per second:
# SET: ~100,000+ ops/sec
# GET: ~100,000+ ops/sec

# Test with pipelining (batch operations)
redis-benchmark -t set,get -n 100000 -q -P 16
# Shows significant improvement with pipelining
```

---

## Summary Table

| Data Structure | Use Case | Key Commands | Time Complexity |
|----------------|----------|--------------|-----------------|
| **String** | Sessions, Cache | GET, SET, MGET, EXPIRE | O(1) |
| **Hash** | Shopping Cart, User Profile | HSET, HGET, HGETALL, HINCRBY | O(1) |
| **List** | Recent Items, Activity Feed | LPUSH, LRANGE, LTRIM | O(1) push, O(N) range |
| **Set** | Tags, Categories | SADD, SMEMBERS, SINTER, SUNION | O(1) add, O(N) members |
| **Sorted Set** | Leaderboards, Rankings | ZADD, ZRANGE, ZREVRANK | O(log N) |
| **HyperLogLog** | Unique Counts | PFADD, PFCOUNT | O(1) |

---

## Q&A

1. **Why Redis over a relational database for sessions?**
   - Speed (in-memory), automatic expiration, no schema overhead

2. **What happens if Redis crashes?**
   - Data persistence options: RDB snapshots, AOF logging, or hybrid

3. **How does Redis handle concurrent writes?**
   - Single-threaded command processing (no locks needed), MULTI/EXEC for transactions

4. **When should you NOT use Redis?**
   - Complex queries, large datasets exceeding RAM, strong consistency requirements

5. **How does Redis scale?**
   - Redis Cluster for horizontal scaling, read replicas for read scaling