# Redis Caching Demo with PostgreSQL

Demonstrates the **cache-aside pattern** using Redis as a cache layer in front of PostgreSQL.

## Architecture

```
┌──────────┐     ┌───────────┐     ┌────────────┐
│  Client  │────▶│  Flask    │────▶│   Redis    │
│          │     │   App     │     │  (Cache)   │
└──────────┘     └─────┬─────┘     └────────────┘
                       │ cache miss
                       ▼
                ┌────────────┐
                │ PostgreSQL │
                │    (DB)    │
                └────────────┘
```

## Quick Start

```bash
docker-compose up --build
```

The app will be available at `http://localhost:5000`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | API documentation |
| `GET /products` | List all products |
| `GET /product/<id>` | Get product **with** caching |
| `GET /product/<id>/no-cache` | Get product **without** caching |
| `GET /cache/clear` | Clear all cache |
| `GET /cache/stats` | View cache statistics |

## Demo: Cache vs No-Cache Performance

### 1. First request (cache miss) - ~2 seconds
```bash
curl http://localhost:5000/product/1
```
```json
{
  "data": {"id": 1, "name": "Wireless Mouse", "price": 29.99, ...},
  "source": "database",
  "response_time_ms": 2005.3,
  "cached_for": "60 seconds"
}
```

### 2. Second request (cache hit) - ~1ms
```bash
curl http://localhost:5000/product/1
```
```json
{
  "data": {"id": 1, "name": "Wireless Mouse", "price": 29.99, ...},
  "source": "cache",
  "response_time_ms": 1.2
}
```

### 3. Without caching (always slow)
```bash
curl http://localhost:5000/product/1/no-cache
```
```json
{
  "data": {"id": 1, "name": "Wireless Mouse", "price": 29.99, ...},
  "source": "database",
  "response_time_ms": 2003.1
}
```

**Performance improvement: ~2000x faster with cache!**

## How It Works (Cache-Aside Pattern)

1. **Check Cache**: App first checks Redis for the requested data
2. **Cache Hit**: If found, return immediately (~1ms)
3. **Cache Miss**: If not found, query PostgreSQL (~2s with simulated delay)
4. **Store in Cache**: Save result to Redis with 60s TTL
5. **Auto-Expiration**: Redis removes stale data after TTL

```
Request → Check Redis → [HIT] → Return cached data
                     → [MISS] → Query PostgreSQL
                              → Store in Redis
                              → Return data
```

## Sample Data

| ID | Name | Price | Stock | Category |
|----|------|-------|-------|----------|
| 1 | Wireless Mouse | $29.99 | 150 | electronics |
| 2 | USB-C Cable | $12.99 | 500 | accessories |
| 3 | Mechanical Keyboard | $89.99 | 75 | electronics |
| 4 | Monitor Stand | $45.00 | 200 | accessories |
| 5 | Webcam HD | $59.99 | 100 | electronics |

## Project Structure

```
caching/
├── app.py              # Flask app with caching logic
├── docker-compose.yml  # PostgreSQL + Redis + App
├── Dockerfile          # App container
├── init.sql            # Database schema & seed data
├── requirements.txt    # Python dependencies
└── README.md
```

## Stopping

```bash
docker-compose down        # Stop containers
docker-compose down -v     # Stop and remove volumes
```