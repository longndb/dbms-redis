from flask import Flask, jsonify
import redis
import time
import json
from datetime import datetime

app = Flask(__name__)

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def simulate_slow_database_query(user_id):
    """Simulate a slow database query that takes 3 seconds"""
    time.sleep(3)
    return {
        'user_id': user_id,
        'name': f'User {user_id}',
        'email': f'user{user_id}@example.com',
        'created_at': datetime.now().isoformat()
    }

@app.route('/')
def home():
    return jsonify({
        'message': 'Redis Caching Demo',
        'endpoints': {
            '/user/<user_id>': 'Get user with caching (cached for 60 seconds)',
            '/user/<user_id>/no-cache': 'Get user without caching',
            '/cache/clear': 'Clear all cache',
            '/cache/stats': 'View cache statistics'
        }
    })

@app.route('/user/<int:user_id>')
def get_user_cached(user_id):
    """Get user data with Redis caching"""
    cache_key = f'user:{user_id}'

    start_time = time.time()

    # Try to get from cache
    cached_data = redis_client.get(cache_key)

    if cached_data:
        data = json.loads(cached_data)
        elapsed_time = time.time() - start_time
        return jsonify({
            'data': data,
            'source': 'cache',
            'response_time_seconds': round(elapsed_time, 3),
            'message': 'Data retrieved from Redis cache!'
        })

    # Cache miss - get from "database"
    data = simulate_slow_database_query(user_id)

    # Store in cache with 60 seconds expiration
    redis_client.setex(cache_key, 60, json.dumps(data))

    elapsed_time = time.time() - start_time
    return jsonify({
        'data': data,
        'source': 'database',
        'response_time_seconds': round(elapsed_time, 3),
        'message': 'Data retrieved from database and cached for 60 seconds'
    })

@app.route('/user/<int:user_id>/no-cache')
def get_user_no_cache(user_id):
    """Get user data without caching"""
    start_time = time.time()

    data = simulate_slow_database_query(user_id)

    elapsed_time = time.time() - start_time
    return jsonify({
        'data': data,
        'source': 'database',
        'response_time_seconds': round(elapsed_time, 3),
        'message': 'Data retrieved from database (no caching)'
    })

@app.route('/cache/clear')
def clear_cache():
    """Clear all cache"""
    redis_client.flushall()
    return jsonify({
        'message': 'All cache cleared successfully!'
    })

@app.route('/cache/stats')
def cache_stats():
    """Get cache statistics"""
    info = redis_client.info('stats')
    keys = redis_client.keys('*')

    return jsonify({
        'total_keys': len(keys),
        'keys': keys,
        'keyspace_hits': info.get('keyspace_hits', 0),
        'keyspace_misses': info.get('keyspace_misses', 0)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)