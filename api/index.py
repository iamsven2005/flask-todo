from flask import Flask, request, render_template, jsonify, session
import psycopg2
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CORS(app)

# Use environment variable for secret key
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret')

# Use environment variable for database connection string
conn_str = os.environ.get('DATABASE_URL')

def get_db():
    return psycopg2.connect(conn_str)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    session['username'] = username
    return jsonify({'status': 'ok'})

@app.route('/add', methods=['POST'])
def add():
    if 'username' not in session:
        return jsonify({'error': 'unauthorized'}), 401
    task = request.json['task']
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO todos (task, owner) VALUES (%s, %s);", (task, session['username']))
    return jsonify({'status': 'ok'})

@app.route('/list')
def list_tasks():
    if 'username' not in session:
        return jsonify([])
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, task FROM todos WHERE owner = %s ORDER BY id;", (session['username'],))
            todos = cur.fetchall()
    return jsonify(todos)

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'status': 'logged out'})

if __name__ == '__main__':
    app.run(debug=True)
