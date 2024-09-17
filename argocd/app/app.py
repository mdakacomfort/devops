from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

def get_db_connection():
    connection = psycopg2.connect(
        dbname='demodb1',
        user='postgres',
        password='password',
        host='postgres-service',
        port=5432
    )
    return connection

@app.route('/')
def index():
    return "Welcome to the Flask App with PostgreSQL!"

@app.route('/data')
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT version();')
    db_version = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"PostgreSQL Version": db_version})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)