from datetime import timedelta
from logging import getLogger, StreamHandler, DEBUG
import os
from flask import Flask, session, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
import tweepy
from tweepy import TweepError
from database import read_data
from similarity import get_most_similar_song
from tweet import get_terms_in_tweets

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = os.environ['FLASK_SECRET_KEY']

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
CALLBACK_URL = os.environ['CALLBACK_URL']

songs_data = read_data()

@app.before_request
def delete_analyzed_data():
    if request.path == url_for('result') or request.path.startswith('/static/'):
        return
    session.pop('recommended_index', None)
    session.pop('included_terms', None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/twitter_auth', methods=['GET'])
def twitter_auth():
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
        redirect_url = auth.get_authorization_url()
        session['request_token'] = auth.request_token
    except TweepError as e:
        logger.exception('in twitter_auth')
        return redirect('/')

    return redirect(redirect_url)

@app.route('/success', methods=['GET'])
def success_login():
    verifier = request.args.get('oauth_verifier')
    session['verifier'] = verifier
    return redirect('/result')
    
@app.route('/result', methods=['GET'])
def result():
    if 'recommended_index' in session and 'included_terms' in session:
        index = session['recommended_index']
        recommended_song = songs_data[index]
        included_terms = session['included_terms']
        return render_template('result.html', url_root=request.url_root, song=recommended_song, included_terms=included_terms)
    
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    
    token = session.pop('request_token', None)
    verifier = session.pop('verifier', None)
    if token is None or verifier is None:
        return redirect('/')
    
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    auth.request_token = token
    try:
        auth.get_access_token(verifier)
    except TweepError as e:
        logger.exception('in result, authorizing')
        return redirect(url_for('error', msg='連携に失敗しました. 初めからやり直してください.'))
    
    api = tweepy.API(auth)
    
    try:
        terms_in_tweets = get_terms_in_tweets(api)
    except TweepError as e:
        logger.exception('in result, getting tweets')
        return redirect(url_for('error', msg='ツイートの取得に失敗しました. 初めからやり直してください.'))
    
    if len(terms_in_tweets) == 0:
        return redirect(url_for('error', msg='ツイートが不足しています.'))
    
    max_index = get_most_similar_song(api, terms_in_tweets, songs_data)
    session['recommended_index'] = max_index
    recommended_song = songs_data[max_index]
    lyrics_set = set(recommended_song.lyrics.split())
    intersection = terms_in_tweets & lyrics_set
    session['included_terms'] = list(intersection)
    
    return render_template('result.html', url_root=request.url_root, song=recommended_song, included_terms=intersection)

@app.route('/error?<string:msg>', methods=['GET'])
def error(msg):
    session.pop('title', None)
    return render_template('error.html', message=msg)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])