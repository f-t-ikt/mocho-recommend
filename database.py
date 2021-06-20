import os
import psycopg2
from song import Song

def read_data():
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    cur.execute("SELECT * FROM data ORDER BY id");
    data = []
    for record in cur:
        song = Song(*record)
        data.append(song)
    
    return data