from logging import getLogger
import os
from flask import Flask, session, redirect, render_template, request
from flask_bootstrap import Bootstrap
import tweepy
from database import read_data
from similarity import get_most_similar_title

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = os.environ['FLASK_SECRET_KEY']

logger = getLogger(__name__)

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
CALLBACK_URL = os.environ['CALLBACK_URL']

titles_list, lyrics_list = read_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter_auth', methods=['GET'])
def twitter_auth():
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
    except tweepy.TweepError as e:
        logger.exception(e)
        return redirect('/')

    return redirect(redirect_url)

@app.route('/success', methods=['GET'])
def success_login():
    verifier = request.args.get('oauth_verifier')
    session['verifier'] = verifier
    return redirect('/result')

@app.route('/result', methods=['GET'])
def result():
    data = analyze()
    if not data:
        return redirect('/')
    return render_template('result.html', title=data)

def analyze():
    token = session.pop('request_token', None)
    verifier = session.pop('verifier', None)
    if token is None or verifier is None:
        return False
    
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    auth.request_token = token
    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError as e:
        logger.exception(e)
        return False
    
    api = tweepy.API(auth)
    return get_most_similar_title(api, titles_list, lyrics_list)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])