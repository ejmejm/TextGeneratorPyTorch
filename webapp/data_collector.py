import praw
import json
import time

class RedditAgent():
    def __init__(self):
        self.login_info = json.load(open('info/li.key', 'r'))
        self.reddit = praw.Reddit(client_id=self.login_info['client_id'],
                     client_secret=self.login_info['client_secret'],
                     password=self.login_info['password'],
                     user_agent='headline-bias by Edan Meyer',
                     username=self.login_info['username'])

    def get_hot(self, subreddit_name, limit=50):
        subreddit = self.reddit.subreddit(subreddit_name)
        headlines = []
        for submission in subreddit.hot(limit=limit):
            headlines.append(submission.title)
        return headlines

    def get_politics(self, limit=50):
        return self.get_hot('politics', limit)

    def get_worldnews(self, limit=50):
        return self.get_hot('worldnews', limit)

def reddit_db_updater(agent, db, row_type, clf, stop_event, n_headlines=50, update_freq=24*60*60):
    try:
        with open('info/last_update.txt', 'r') as f:
            last_update = float(f.read())
    except FileNotFoundError:
        last_update = 0
    
    while not stop_event.is_set():
        while time.time() - last_update < update_freq:
            time.sleep(1)
            if stop_event:
                break

        headlines = agent.get_worldnews() + agent.get_politics()

        for headline in headlines:
            regression = clf.classify_sentence(headline, discrete=False)
            class_pred = clf.prediction_to_str(regression)
            reddit_headline = row_type(headline, regression, class_pred)
            db.session.add(reddit_headline)
        db.session.commit()

        last_update = time.time()
        with open('info/last_update.txt', 'w+') as f:
            f.write(str(last_update))