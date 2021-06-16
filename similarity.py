import tweepy
from parser import parse

def calc_simpson_coefficient(x, y):
    x_size, y_size = len(x), len(y)
    intersection = x & y
    intersection_size = len(intersection)
    denominator = min(x_size, y_size)
    if denominator == 0:
        return 0
    return intersection_size / denominator

def calc_similarity(text, lyrics_list):
    text_parsed = set(parse(text).split())
    similarity = [0] * len(lyrics_list)
    if len(text_parsed) == 0:
        return similarity
    for i, lyrics in enumerate(lyrics_list):
        terms_in_lyrics = set(lyrics.split())
        similarity[i] = calc_simpson_coefficient(terms_in_lyrics, text_parsed)
    return similarity

def get_tweets(api):
    tweets = []
    try:
        tweets = api.user_timeline(count=100, include_rts=False)
    except tweepy.error.TweepError:
        pass
    if len(tweets) > 30:
        tweets = tweets[:30]
    return tweets

def concat_tweets(tweets):
    text = " "
    for tweet in tweets:
        text += tweet.text + " "
    return text

def get_most_similar_title(api, titles_list, lyrics_list):
    tweets = get_tweets(api)
    tweets_text = concat_tweets(tweets)
    similarity = calc_similarity(tweets_text, lyrics_list)
    max_index = similarity.index(max(similarity))
    max_title = titles_list[max_index]
    return max_title
