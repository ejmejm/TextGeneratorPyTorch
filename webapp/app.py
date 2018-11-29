from flask import Flask, render_template, request, redirect, session
import sys
from classifier import Classifier

app = Flask(__name__)

clf = Classifier()

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
    session['class'] = clf.classify_sentence(headline)
    return redirect('/')

if __name__ == '__main__':
    app.secret_key = 'TISDF82FS3U2LVJ'
    app.run(debug=True)