import psycopg2
from config import DB

def connect():
    try:
        conn = psycopg2.connect(
            database=DB["database"],
            user=DB["user"],
            password=DB["password"],
            host=DB["host"],
            port=DB["port"]
        )
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)