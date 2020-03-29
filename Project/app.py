from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import math


app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:123@localhost/RoveTest'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db= SQLAlchemy(app)

@app.route('/', methods=["GET","POST"])
def index():
    return render_template('index.html')  

@app.route('/signup', methods = ["GET","POST"])
def signup():
    if request.method == 'POST':
        if request.form['btn'] == 'Sign Up':
            username = request.form['username']
            email = request.form['email']
            password = request.form['pass']
            print(username)
            print(email)
            print(password)
    
    return render_template('signup.html')
    
