"""
Simple Flask application demonstrating Redis session management.
Shows how multiple app instances can share sessions via Redis.
"""
from flask import Flask, session, request, jsonify
from flask_session import Session
import redis
import os

app = Flask(__name__)

# App instance identifier
APP_NAME = os.environ.get('APP_NAME', 'App-Unknown')

# Session configuration using Redis
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_REDIS'] = redis.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379')
)

# Initialize Flask-Session
Session(app)


@app.route('/')
def index():
    """Home page showing session status."""
    if 'username' in session:
        return jsonify({
            'server': APP_NAME,
            'message': f"Welcome back, {session['username']}!",
            'logged_in': True,
            'visit_count': session.get('visit_count', 0)
        })
    return jsonify({
        'server': APP_NAME,
        'message': 'Welcome! Please login.',
        'logged_in': False
    })


@app.route('/login', methods=['POST'])
def login():
    """Login endpoint - stores user in Redis session."""
    data = request.get_json() or {}
    username = data.get('username', 'guest')

    session['username'] = username
    session['visit_count'] = 1

    return jsonify({
        'server': APP_NAME,
        'message': f'Logged in as {username}',
    })


@app.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint - clears Redis session."""
    username = session.get('username', 'Unknown')
    session.clear()

    return jsonify({
        'server': APP_NAME,
        'message': f'Goodbye, {username}!'
    })


@app.route('/visit')
def visit():
    """Increment visit counter stored in session."""
    if 'username' not in session:
        return jsonify({'server': APP_NAME, 'error': 'Please login first'}), 401

    session['visit_count'] = session.get('visit_count', 0) + 1

    return jsonify({
        'server': APP_NAME,
        'username': session['username'],
        'visit_count': session['visit_count']
    })


@app.route('/profile')
def profile():
    """Get current session data."""
    if 'username' not in session:
        return jsonify({'server': APP_NAME, 'error': 'Please login first'}), 401

    return jsonify({
        'server': APP_NAME,
        'username': session['username'],
        'visit_count': session.get('visit_count', 0)
    })


@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        redis_client = app.config['SESSION_REDIS']
        redis_client.ping()
        return jsonify({'server': APP_NAME, 'status': 'healthy', 'redis': 'connected'})
    except Exception as e:
        return jsonify({'server': APP_NAME, 'status': 'unhealthy', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
