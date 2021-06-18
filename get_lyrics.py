import os
import time
from bs4 import BeautifulSoup
import psycopg2
import requests
from parser import parse

SITE_URL = "https://www.uta-net.com"
ARTIST_URL = "/artist/21078/"

def get_tables(url, page):
    response = requests.get(f"{url}0/{page}/")
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    return tables

def get_song_list(url):
    data = []
    page_no = 0
    
    while True:
        page_no += 1
        tables = get_tables(url, page_no)
        
        if len(tables) == 0:
            break
        
        for table in tables:
            title_list = table.find_all('td', {'class': 'td1'})
            for title in title_list:
                song_title = title.get_text()
                song_lyrics_url = title.a.get('href')
                data.append((song_title, song_lyrics_url))
        time.sleep(1)
    
    return data

def get_lyrics(lyrics_url):
    url = SITE_URL + lyrics_url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    song_lyrics = soup.find('div', id='kashi_area')
    for br in soup.select('br'):
        br.replace_with(' ')
    lyrics = song_lyrics.text
    time.sleep(1)
    return lyrics

if __name__ == "__main__":
    artist_url = SITE_URL + ARTIST_URL
    song_list = get_song_list(artist_url)
    
    parsed_data = []
    for title, lyrics_url in song_list:
        lyrics = get_lyrics(lyrics_url)
        lyrics_parsed = parse(lyrics)
        parsed_data.append((title, lyrics_parsed))
    
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    for title, lyrics_parsed in parsed_data:
        cur.execute(f"INSERT INTO data (title, lyrics) VALUES ('{title}', '{lyrics_parsed}')")
        conn.commit()
    