# Redis Caching Demo Application

A simple Flask application demonstrating Redis caching use cases with clear performance comparisons.

## Overview

This application simulates a slow database query (3 seconds) and demonstrates how Redis caching can dramatically improve response times for subsequent requests.

## Features

- Flask REST API with multiple endpoints
- Redis caching with 60-second TTL (Time To Live)
- Performance comparison between cached and non-cached requests
- Cache statistics and management endpoints

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Start the application:
```bash
docker-compose up --build
```

2. The application will be available at `http://localhost:5000`

## API Endpoints

- `GET /` - Home page with endpoint documentation
- `GET /user/<user_id>` - Get user with caching
- `GET /user/<user_id>/no-cache` - Get user without caching
- `GET /cache/clear` - Clear all cache
- `GET /cache/stats` - View cache statistics

## Demo: Comparing Cache Performance

### Test 1: Without Cache (Baseline)

Request user data without caching:
```bash
curl http://localhost:5000/user/1/no-cache
```

Expected response time: ~3 seconds
```json
{
  "data": {
    "user_id": 1,
    "name": "User 1",
    "email": "user1@example.com",
    "created_at": "2026-01-19T..."
  },
  "source": "database",
  "response_time_seconds": 3.002,
  "message": "Data retrieved from database (no caching)"
}
```

### Test 2: First Request with Cache (Cache Miss)

Request user data with caching enabled (first time):
```bash
curl http://localhost:5000/user/1
```

Expected response time: ~3 seconds (cache miss, data fetched from database)
```json
{
  "data": {
    "user_id": 1,
    "name": "User 1",
    "email": "user1@example.com",
    "created_at": "2026-01-19T..."
  },
  "source": "database",
  "response_time_seconds": 3.001,
  "message": "Data retrieved from database and cached for 60 seconds"
}
```

### Test 3: Subsequent Request with Cache (Cache Hit)

Request the same user data again within 60 seconds:
```bash
curl http://localhost:5000/user/1
```

Expected response time: < 0.01 seconds (cache hit, data from Redis)
```json
{
  "data": {
    "user_id": 1,
    "name": "User 1",
    "email": "user1@example.com",
    "created_at": "2026-01-19T..."
  },
  "source": "cache",
  "response_time_seconds": 0.003,
  "message": "Data retrieved from Redis cache!"
}
```

**Performance Improvement: ~1000x faster!**

### Test 4: View Cache Statistics

```bash
curl http://localhost:5000/cache/stats
```

Response:
```json
{
  "total_keys": 1,
  "keys": ["user:1"],
  "keyspace_hits": 5,
  "keyspace_misses": 1
}
```

### Test 5: Clear Cache

```bash
curl http://localhost:5000/cache/clear
```

## Key Observations

1. **First Request (Cache Miss)**: Takes ~3 seconds as data is fetched from the simulated database
2. **Cached Requests (Cache Hit)**: Takes < 0.01 seconds, retrieved instantly from Redis
3. **Performance Gain**: Approximately 300-1000x faster with caching
4. **TTL**: Cache expires after 60 seconds, then the cycle repeats

## Use Cases Demonstrated

1. **Database Query Caching**: Reduce load on databases for frequently accessed data
2. **API Response Caching**: Speed up API responses for repeated requests
3. **Session Management**: Redis can store session data (demonstrated through user data)
4. **Rate Limiting**: Track request counts (visible in cache stats)

## Stopping the Application

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Project Structure

```
.
├── app.py              # Flask application with Redis caching
├── Dockerfile          # Docker configuration for the app
├── docker-compose.yml  # Orchestration for app + Redis
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## How It Works

1. **Slow Database Query**: `simulate_slow_database_query()` simulates a 3-second database operation
2. **Cache Check**: Before querying the database, the app checks Redis for cached data
3. **Cache Hit**: If data exists in cache, return immediately (milliseconds)
4. **Cache Miss**: If data not in cache, query database, then store result in Redis with 60s expiration
5. **Automatic Expiration**: Redis automatically removes expired keys after TTL

## Conclusion

This demo clearly shows how Redis caching can:
- Dramatically reduce response times (from seconds to milliseconds)
- Reduce load on backend databases
- Improve user experience
- Scale applications efficiently