# Session Management with Redis

A simple demo showing how multiple Flask application instances can share session data using Redis as a centralized session store.

## Overview

This project demonstrates:
- **Shared sessions across multiple app instances** - Login on one server, stay logged in on another
- **Redis as session backend** - Fast, persistent session storage
- **Docker Compose orchestration** - Easy multi-container setup

## Architecture

```
┌─────────────┐     ┌─────────────┐
│   App-1     │     │   App-2     │
│  (port 5001)│     │  (port 5002)│
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 │
          ┌──────▼──────┐
          │    Redis    │
          │ (port 6379) │
          └─────────────┘
```

## Quick Start

```bash
# Start all services
docker-compose up --build

# Or run in background
docker-compose up --build -d
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Check login status |
| `/login` | POST | Login with username |
| `/logout` | POST | Clear session |
| `/visit` | GET | Increment visit counter |
| `/profile` | GET | Get session data |
| `/health` | GET | Health check |

## Testing the Demo

1. **Login via App-1:**
   ```bash
   curl -X POST http://localhost:5001/login \
     -H "Content-Type: application/json" \
     -d '{"username": "john"}' \
     -c cookies.txt
   ```

2. **Check session on App-2 (same session works!):**
   ```bash
   curl http://localhost:5002/profile -b cookies.txt
   ```

3. **Increment visit counter:**
   ```bash
   curl http://localhost:5001/visit -b cookies.txt
   curl http://localhost:5002/visit -b cookies.txt
   ```

4. **Logout:**
   ```bash
   curl -X POST http://localhost:5001/logout -b cookies.txt
   ```

## Project Structure

```
session-management/
├── app.py              # Flask application
├── docker-compose.yml  # Multi-container setup
├── Dockerfile          # App container image
└── requirements.txt    # Python dependencies
```

## Requirements

- Docker & Docker Compose

## Local Development (without Docker)

```bash
# Start Redis locally
redis-server

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```