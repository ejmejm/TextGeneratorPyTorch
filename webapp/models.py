from app import db
from datetime import datetime

class UserHeadline(db.Model):
    __tablename__ = 'user_headline'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime())
    headline = db.Column(db.String(255))
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
    headline = db.Column(db.String(255))
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