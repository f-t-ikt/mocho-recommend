import tweepy
from tweepy import TweepError
from parser import parse

def calc_simpson_coefficient(x, y):
    x_size, y_size = len(x), len(y)
    intersection = x & y
    intersection_size = len(intersection)
    denominator = min(x_size, y_size)
    if denominator == 0:
        return 0
    return intersection_size / denominator

def calc_similarity(tweets_set, lyrics_list):
    similarity = [0] * len(lyrics_list)
    if len(tweets_set) == 0:
        return similarity
    for i, lyrics in enumerate(lyrics_list):
        terms_in_lyrics = set(lyrics.split())
        similarity[i] = calc_simpson_coefficient(terms_in_lyrics, tweets_set)
    return similarity

def get_tweets(api):
    tweets = []
    try:
        tweets = api.user_timeline(count=100, include_rts=False)
    except TweepError:
        raise
    if len(tweets) > 30:
        tweets = tweets[:30]
    return tweets

def concat_tweets(tweets):
    text = " "
    for tweet in tweets:
        text += tweet.text + " "
    return text

def get_terms_in_tweets(api):
    try:
        tweets = get_tweets(api)
    except :
        raise
    tweets_text = concat_tweets(tweets)
    tweets_parsed = parse(tweets_text)
    tweets_set = set(tweets_parsed.split())
    return tweets_set

def get_most_similar_title(api, tweets_set, songs_data):
    lyrics_list = [song.lyrics for song in songs_data]
    similarity = calc_similarity(tweets_set, lyrics_list)
    max_index = similarity.index(max(similarity))
    return max_index
