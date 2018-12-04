from flask import Flask, render_template, request, redirect, session
import sys
from classifier import Classifier
from flask_sqlalchemy import SQLAlchemy
import os
import random
import threading

app = Flask(__name__)
app.debug = True
app.secret_key = 'SI7UH8JFHSU9B85UN1f4FHL'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)

from models import *
from data_collector import RedditAgent, reddit_db_updater

# db.drop_all()
db.create_all()
db.init_app(app)

clf = Classifier()

reddit = RedditAgent()
stop_reddit_updater = threading.Event()
reddit_thread = threading.Thread(target=reddit_db_updater, args=(reddit, db, models.RedditHeadline, clf, stop_reddit_updater,))
reddit_thread.start()

@app.route('/', methods=['GET'])
def index():
    # Poynter
    c = session.get('class')
    if c is None:
        c = ''
        cc = 'white'
    elif c == 'left':
        c = 'LEFT'
        cc = 'rgb(74, 74, 255)'
    elif c == 'right':
        c = 'RIGHT'
        cc = 'rgb(255, 74, 74)'
    return render_template('home.html', Class=c, ClassColor=cc)

@app.route('/classify', methods=['POST'])
def classify():
    headline = request.form['headline']
    regression = clf.classify_sentence(headline, discrete=False)
    session['class'] = clf.prediction_to_str(regression)
    user_headline = UserHeadline(headline, regression, session['class'])
    db.session.add(user_headline)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        stop_reddit_updater.set()