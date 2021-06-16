import os
import psycopg2

def read_data():
    database_url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    cur.execute("SELECT * FROM data");
    titles_list, lyrics_list = [], []
    for title, lyrics_parsed in cur:
        titles_list.append(title)
        lyrics_list.append(lyrics_parsed)
    
    return titles_list, lyrics_list