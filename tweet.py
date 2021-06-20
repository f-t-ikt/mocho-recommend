import tweepy
from tweepy import TweepError

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
