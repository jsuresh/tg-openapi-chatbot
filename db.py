# Simple abstraction over the DB as a blob store
import psycopg2
from psycopg2 import sql
import json

def connect_db(dsn):
    return psycopg2.connect(dsn)

def get(conn, table, id):
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM {} WHERE id = %s".format(table), (str(id),))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return json.loads(result[0])  # Convert JSON string to Python dict
    else:
        return None

def update_or_create(conn, table, id, data):
    try:
        cursor = conn.cursor()
        json_data = json.dumps(data)  # Convert Python dict to JSON string
        cursor.execute("INSERT INTO {} (id, data) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET data = %s".format(table), (str(id), json_data, json_data))
        conn.commit()
        cursor.close()
    except Exception as e:
        print(f"Error: {str(e)}")

class Model:
    def __init__(self, conn, table):
        self.conn = conn
        self.table = table

    def get(self, id):
        return get(self.conn, self.table, id)

    def update_or_create(self, id, data):
        return update_or_create(self.conn, self.table, id, data)

class Bot(Model):
    def __init__(self, conn):
        super().__init__(conn, 'bot')

class Chat(Model):
    def __init__(self, conn):
        super().__init__(conn, 'chat')