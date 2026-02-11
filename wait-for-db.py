import os
import time
import psycopg2

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

print("Waiting for database...")

while True:
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        conn.close()
        print("Database is ready!")
        break
    except psycopg2.OperationalError:
        print("Database unavailable, sleeping 3 seconds...")
        time.sleep(3)