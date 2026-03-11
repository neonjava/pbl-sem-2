import mysql.connector
from mysql.connector import Error
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

class Database:
    def __init__(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            # First connect without database to create it if it doesn't exist
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            conn.close()

            # Now connect to the database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False

    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor(dictionary=True, buffered=True)
            cursor.execute(query, params or ())
            
            # If it's a SELECT query, return the cursor to be fetched
            if query.strip().upper().startswith("SELECT"):
                return cursor
            
            # Otherwise, commit and return lastrowid then close cursor
            self.connection.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"Query Error: {e}")
            if 'cursor' in locals() and cursor:
                cursor.close()
            return None

    def fetch_all(self, query, params=None):
        res = self.execute_query(query, params)
        if isinstance(res, mysql.connector.cursor_cext.CMySQLCursorBufferedDict):
            data = res.fetchall()
            res.close()
            return data
        return []

    def fetch_one(self, query, params=None):
        res = self.execute_query(query, params)
        if isinstance(res, mysql.connector.cursor_cext.CMySQLCursorBufferedDict):
            data = res.fetchone()
            res.close()
            return data
        return None

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

# Initialize database schema
def init_db():
    db = Database()
    if db.connect():
        with open("schema.sql", "r") as f:
            sql_commands = f.read().split(';')
            for command in sql_commands:
                cmd = command.strip()
                if cmd:
                    res = db.execute_query(cmd)
                    # If it returned a cursor (though schema commands shouldn't for SELECT), close it
                    if hasattr(res, 'close'):
                        res.close()
        print("Database initialized successfully.")
        db.close()
    else:
        print("Failed to initialize database.")

if __name__ == "__main__":
    init_db()
