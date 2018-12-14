from flask import Flask, render_template, request, redirect, session
import sys
from classifier import Classifier
from flask_sqlalchemy import SQLAlchemy
import os
import random
import threading
from datetime import datetime
from sqlalchemy import desc
import numpy as np
import time
from urllib.parse import urlparse

app = Flask(__name__)
app.debug = True
app.secret_key = 'SI7UH8JFHSU9B85UN1f4FHL'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class UserHeadline(db.Model):
    __tablename__ = 'user_headline'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime())
    headline = db.Column(db.String(1024))
    bias_regression = db.Column(db.ARRAY(db.Float))
    bias_class = db.Column(db.String(5))

    def __init__(self, headline, bias_regression, bias_class, timestamp=None):
        self.headline = headline
        self.bias_regression = bias_regression
        self.bias_class = bias_class
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp

    def __repr__(self):
        return '<Headline: {}, Bias: {}>'.fomat(self.headline, self.bias_class)

class RedditHeadline(db.Model):
    __tablename__ = 'reddit_headline'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime())
    headline = db.Column(db.String(1024))
    headline_src = db.Column(db.String(512))
    bias_regression = db.Column(db.ARRAY(db.Float))
    bias_class = db.Column(db.String(5))

    def __init__(self, headline, headline_src, bias_regression, bias_class, timestamp=None):
        self.headline = headline
        self.headline_src = headline_src
        self.bias_regression = bias_regression
        self.bias_class = bias_class
        if timestamp is None:
            self.timestamp = datetime.now()
        else:
            self.timestamp = timestamp

    def __repr__(self):
        return '<Headline: {}, Bias: {}>'.fomat(self.headline, self.bias_class)

from data_collector import RedditAgent, reddit_db_updater

try:    
    os.remove('info/last_update.txt')
except FileNotFoundError:
    pass
db.drop_all()
time.sleep(0.1)
db.create_all()
time.sleep(0.1)
db.init_app(app)

clf = Classifier()

reddit = RedditAgent()
stop_reddit_updater = threading.Event()
reddit_thread = threading.Thread(target=reddit_db_updater, args=(reddit, db, RedditHeadline, clf, stop_reddit_updater,))
reddit_thread.start()

@app.route('/', methods=['GET'])
def index():

    white = np.array([255, 255, 255])
    blue = np.array([85, 85, 255])
    red = np.array([255, 85, 85])

    reddit_rows = RedditHeadline.query.order_by(desc(RedditHeadline.timestamp)).limit(100).all()
    r_reddit_headlines = []
    l_reddit_headlines = []
    for row in reddit_rows:
        if row.bias_class == 'left':
            l_reddit_headlines.append({'text': row.headline})
            color_perc = (row.bias_regression[0] - 0.5) * 2.
            color = color_perc * blue + (1 - color_perc) * white
            l_reddit_headlines[-1]['color'] = tuple(color)
            l_reddit_headlines[-1]['bias_perc'] = int(round(row.bias_regression[0] * 100))
            l_reddit_headlines[-1]['src_link'] = row.headline_src
            url_data = urlparse(row.headline_src)
            url_base = url_data.netloc
            l_reddit_headlines[-1]['src'] = url_base[url_base.find('www.')+4:url_base.rfind('.')]
        elif row.bias_class == 'right':
            r_reddit_headlines.append({'text': row.headline})
            color_perc = (row.bias_regression[1] - 0.5) * 2.
            color = color_perc * red + (1 - color_perc) * white
            r_reddit_headlines[-1]['color'] = tuple(color)
            r_reddit_headlines[-1]['bias_perc'] = int(round(row.bias_regression[1] * 100))
            r_reddit_headlines[-1]['src_link'] = row.headline_src
            url_data = urlparse(row.headline_src)
            url_base = url_data.netloc
            r_reddit_headlines[-1]['src'] = url_base[url_base.find('www.')+4:url_base.rfind('.')]

    # Poynter
    c = session.get('class')
    if c == 'left':
        c = 'LEFT'
        cp = session['regres'][0]
        cc = 'rgb' + str(tuple(blue * (cp - 0.5) * 2. + white * (1 - (cp - 0.5) * 2.)))
        cp = int(round(cp * 100))
    elif c == 'right':
        c = 'RIGHT'
        cp = session['regres'][1]
        cc = 'rgb' + str(tuple(red * (cp - 0.5) * 2. + white * (1 - (cp - 0.5) * 2.)))
        cp = int(round(cp * 100))
    else:
        c = ''
        cc = 'rgb(255, 255, 255)'
        cp = 0
    
    return render_template('home.html', Class=c, ClassColor=cc, ClassPercent=cp, RightReddit=r_reddit_headlines,
                            LeftReddit=l_reddit_headlines)

@app.route('/classify', methods=['POST'])
def classify():
    headline = request.form['headline']
    regression = clf.classify_sentence(headline, discrete=False)
    session['regres'] = regression
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