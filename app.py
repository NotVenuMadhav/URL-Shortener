from distutils.log import debug
from operator import methodcaller
import random
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key = True)
    long_ = db.Column("long", db.String())
    short_ = db.Column("short", db.String(3))

    def __init__(self, long_, short_):
        self.long_ = long_
        self.short_ = short_


@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url():
    letters = string.ascii_lowercase + string.ascii_uppercase
    while True:
        rand_letters =  random.choices(letters, k=2)
        #because the letters are given as list convert to a string
        rand_letters = "".join(rand_letters) 
        short_url = Urls.query.filter_by(short_=rand_letters).first()
        #if the same pattern is present while loop runs again if not then if condition runs
        if not short_url:
            return rand_letters


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        url_received = request.form['nm']

        #Check if the received URL is already present in the DB
        found_url = Urls.query.filter_by(long_=url_received).first()
        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short_))
        else:
            #create short url if not found
            short_url = shorten_url()
            new_url = Urls(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))

    else:
        return render_template("home.html")

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('short.html', short_url_display=url)


@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(short_=short_url).first()
    if long_url:
        return redirect(long_url.long_)
    else:
        return f'<h1>Url doesnt exist</h1>'

if __name__ == '__main__':
    app.run(port=5000, debug=True)