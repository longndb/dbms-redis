"""
Redis Caching Demo with PostgreSQL
Demonstrates cache-aside pattern with a real database.
"""
from flask import Flask, jsonify
import redis
import psycopg2
import psycopg2.extras
import time
import json
import os

app = Flask(__name__)

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# PostgreSQL connection config
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'postgres'),
    'database': os.environ.get('DB_NAME', 'demo'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres')
}


def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)


def query_product_from_db(product_id):
    """Query product from PostgreSQL."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id, name, price, stock, category
        FROM products
        WHERE id = %s
    """, (product_id,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return {
            'id': row['id'],
            'name': row['name'],
            'price': float(row['price']),
            'stock': row['stock'],
            'category': row['category']
        }
    return None


@app.route('/')
def home():
    return jsonify({
        'message': 'Redis Caching Demo with PostgreSQL',
        'endpoints': {
            '/product/<id>': 'Get product WITH caching',
            '/product/<id>/no-cache': 'Get product WITHOUT caching',
            '/products': 'List all products',
            '/cache/clear': 'Clear all cache',
            '/cache/stats': 'View cache statistics'
        }
    })


@app.route('/product/<int:product_id>')
def get_product_cached(product_id):
    """Get product with Redis caching (cache-aside pattern)."""
    cache_key = f'product:{product_id}'
    start_time = time.time()

    # 1. Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        elapsed = time.time() - start_time
        return jsonify({
            'data': json.loads(cached),
            'source': 'cache',
            'response_time_ms': round(elapsed * 1000, 1)
        })

    # 2. Cache miss - query database
    product = query_product_from_db(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    # 3. Store in cache (TTL: 60 seconds)
    redis_client.setex(cache_key, 60, json.dumps(product))

    elapsed = time.time() - start_time
    return jsonify({
        'data': product,
        'source': 'database',
        'response_time_ms': round(elapsed * 1000, 1),
        'cached_for': '60 seconds'
    })


@app.route('/product/<int:product_id>/no-cache')
def get_product_no_cache(product_id):
    """Get product directly from database (no caching)."""
    start_time = time.time()

    product = query_product_from_db(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    elapsed = time.time() - start_time
    return jsonify({
        'data': product,
        'source': 'database',
        'response_time_ms': round(elapsed * 1000, 1)
    })


@app.route('/products')
def list_products():
    """List all products from database."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, name, price, stock, category FROM products")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    products = [{
        'id': r['id'],
        'name': r['name'],
        'price': float(r['price']),
        'stock': r['stock'],
        'category': r['category']
    } for r in rows]

    return jsonify({'products': products, 'count': len(products)})


@app.route('/cache/clear')
def clear_cache():
    """Clear all cached data."""
    keys = redis_client.keys('product:*')
    if keys:
        redis_client.delete(*keys)
    return jsonify({'message': 'Cache cleared', 'keys_removed': len(keys)})


@app.route('/cache/stats')
def cache_stats():
    """Get cache statistics."""
    info = redis_client.info('stats')
    keys = redis_client.keys('product:*')

    return jsonify({
        'cached_products': len(keys),
        'keys': keys,
        'hits': info.get('keyspace_hits', 0),
        'misses': info.get('keyspace_misses', 0)
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
