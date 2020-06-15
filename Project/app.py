from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import math, random


app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:123@localhost/rove'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db= SQLAlchemy(app)

class Customer_login(db.Model):
    __tablename__ = 'customer_login'
    id = db.Column(db.Integer, db.ForeignKey('customer.id'), primary_key = True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(50))

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(40))
    mobile = db.Column(db.BigInteger)
    wallet = db.Column(db.Integer)

    def __init__(self, name, mobile):
        self.name = name
        self.moblie = moblie

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    vehicle_number = db.Column(db.String(20), primary_key = True)
    model = db.Column(db.String(20))
    address = db.Column(db.Integer, db.ForeignKey('location.id'))
    status = db.Column(db.String(20))
    curr_user = db.Column(db.Integer, db.ForeignKey('customer.id'))
    def __init__(self, vehicle_number, model, status, curr_user):
        self.vehicle_number = vehicle_number
        self.model = model
        self.status = status
        self.curr_user = curr_user


class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, primary_key = True)
    loc_name = db.Column(db.String(40))
    x_coordinate = db.Column(db.Float)
    y_coordinate = db.Column(db.Float)

    def __init__(self, loc_name, x, y):
        self.loc_name = loc_name
        self.x_coordinate = x
        self.y_coordinate = y

class Ride(db.Model):
    __tablename__ = "ride"
    id = db.Column(db.Integer, primary_key = True)
    vehicle_num = db.Column(db.String, db.ForeignKey('vehicle.vehicle_number'))
    from_loc = db.Column(db.Integer, db.ForeignKey('location.id'))
    to_loc = db.Column(db.Integer, db.ForeignKey('location.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    rating = db.Column(db.Integer)
    feedback = db.Column(db.String)

    def __init__(self, vehicle_num, from_loc, to_loc, customer_id, rating, feedback):
        self.vehicle_num = vehicle_num
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.customer_id = customer_id
        self.rating = rating
        self.feedback = feedback

class Complaint(db.Model):
    __tablename__ = "complaint"
    id = db.Column(db.Integer, primary_key = True)
    cust_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    complaint = db.Column(db.String)

    def __init__(self, cust_id, complaint):
        self.cust_id = cust_id
        self.complaint = complaint


def generateOTP():
    digits = "0123456789"
    OTP = ""

    for i in range(4):
        OTP += digits[math.floor(random.random()*10)]
    return OTP 


@app.route('/', methods=["GET","POST"])
def index():
    return render_template('index.html')  
curr_customer_id = 0
balance = 0
@app.route('/signup', methods = ["GET","POST"])
def signup():
    global curr_customer_id
    if request.method == 'POST':
        if request.form['btn'] == 'Sign Up':
            name = request.form['name']
            mobile = request.form['moblie']
            username = request.form['username']
            password = request.form['pass']
            db.session.execute('INSERT INTO "customer"(name, mobile, wallet) values(:name, :mobile, 0)',{"name": name, "mobile": mobile})
            db.session.commit()
            res = db.session.execute('SELECT id from "customer" where name=:n',{"n":name}).fetchone()
            curr_customer_id = res[0] 
            db.session.execute('INSERT INTO "customer_login" values(:id, :username, :password)',{"username": username, "password": password,"id":curr_customer_id})
            db.session.commit()
            return render_template('login.html')

    
    return render_template('signup.html')
locations = " "
loc = " "
@app.route('/login', methods = ["GET","POST"])
def login():
    global curr_customer_id
    global balance
    global locations
    global loc
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['pass']

        count = db.session.execute('SELECT COUNT(*) FROM "customer_login" where username = :username', {"username": username}).fetchone()
        
        if count[0] == 0:
            return render_template('login.html', message="Username does not exist")
        res = db.session.execute('SELECT password FROM "customer_login" WHERE username = :username', {"username": username}).fetchone()
        
        if res[0] == password:
            A = "A"
            res = db.session.execute('SELECT id from "customer_login" where username = :u',{"u":username}).fetchone()
            curr_customer_id = res[0]
            locations = db.session.execute('SELECT distinct loc_name FROM "location" as l,"vehicle" as v where l.id = v.address and v.status=:A',{"A":A}).fetchall()
            loc = db.session.execute('SELECT loc_name FROM "location"').fetchall()
            res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":curr_customer_id}).fetchone()
            balance = res[0]
            return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1)
        return render_template('login.html', message="Wrong password")
    
    return render_template('login.html')
from_location = 'abc'
to_location = 'abc'
cost = 0
dist = 0.0
vehicle_number = "KA"
otp = "0000"

@app.route("/book", methods=["POST"])
def book():
    
    global from_location
    global to_location
    global cost
    global dist
    global vehicle_number
    global otp
    global balance
    if request.form['btn'] == "book ride":
        f = request.form['from']

        from_location = f
        t = request.form['to']
        to_location = t
        print(from_location)
        res = db.session.execute('SELECT x_coordinate, y_coordinate FROM "location" where loc_name =:from ',{"from":f}).fetchone()
        x1 = res[0]
        y1 = res[1]
        res = db.session.execute('SELECT x_coordinate, y_coordinate FROM "location" where loc_name =:to ',{"to":t}).fetchone()
        x2 = res[0]
        y2 = res[1]
        dist = round((math.sqrt((x1-x2)**2 + (y1-y2)**2)), 2)
        cost = int(dist * 3)
        A = "A"
        return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2)
    if request.form['btn'] == "start ride":
        if request.form['otp'] == otp:
            return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 4)
        else:
            return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 3, mesg = "wrong OTP, try again", OTP = otp)

    if request.form['btn'] == "Add money":
        
        amount = request.form['amount']
        
        db.session.execute('UPDATE "customer" set wallet = wallet + :amt where id = :id',{"amt":amount, "id":curr_customer_id})
        db.session.commit()
        res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":curr_customer_id}).fetchone()
        balance = res[0]
        return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1)

    if request.form['btn'] == "Add money ":
        
        amount = request.form['amount']
        
        db.session.execute('UPDATE "customer" set wallet = wallet + :amt where id = :id',{"amt":amount, "id":curr_customer_id})
        db.session.commit()
        res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":curr_customer_id}).fetchone()
        balance = res[0]
        return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2)

    if request.form['btn'] == "Confirm Booking":
        
        
        res = db.session.execute('SELECT id from "location" where loc_name = :f',{"f":from_location}).fetchone()
        
        id = res[0]
        NA = "NA"
        res = db.session.execute('select vehicle_number from "vehicle" where address = :i limit 1' ,{"i": id}).fetchone()
        vehicle_number = res[0]
        print(vehicle_number)
        db.session.execute('UPDATE "vehicle" set status = :NA where vehicle_number = :v',{"NA":NA, "v":vehicle_number})
        db.session.commit()
        otp = generateOTP()
        return render_template('book.html', from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, OTP = otp, opt = 3, balance = balance)
       
        
    
    if request.form['btn'] == "finish ride":
        A = "A"
        res = db.session.execute('SELECT id from "location" where loc_name = :t',{"t":to_location}).fetchone()
        to_location_id = res[0]
        db.session.execute('UPDATE "vehicle" set status = :A, address = :to where vehicle_number = :v',{"A": A,"to": to_location_id, "v": vehicle_number})
        db.session.execute('UPDATE "customer" set wallet = wallet - :cost where id = :cust_id ',{"cust_id":curr_customer_id, "cost":cost})
        db.session.commit()
        return render_template("feedback.html")
        
@app.route("/feedback", methods=["POST"])
def feedback():
    rating = request.form['rating']
    comments = request.form['comments']
    res = db.session.execute('SELECT id from "location" where loc_name = :f',{"f": from_location}).fetchone()
    f = res[0]
    res = db.session.execute('SELECT id from "location" where loc_name = :t',{"t": to_location}).fetchone()
    t = res[0]
    db.session.execute('INSERT into "ride"(vehicle_num, from_loc, to_loc, customer_id, rating, feedback) values(:v, :f , :t, :c, :r, :com)',{"v": vehicle_number, "f": f, "t":t, "c":curr_customer_id, "r":rating, "com":comments})
    db.session.commit()
    return render_template("done.html", opt = 1)

@app.route("/done", methods = ["POST"])
def done():
    global balance
    global locations
    global loc
    if request.method == "POST":
        
        if request.form['btn'] == 'New Ride':
            A = "A"
            locations = db.session.execute('SELECT distinct loc_name FROM "location" as l,"vehicle" as v where l.id = v.address and v.status=:A',{"A":A}).fetchall()
            loc = db.session.execute('SELECT loc_name FROM "location"').fetchall()
            res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":curr_customer_id}).fetchone()
            balance = res[0]
            return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1)

        if request.form['btn'] == 'comp':
            complaint = request.form['complaint']
            db.session.execute('INSERT into "complaint"(cust_id, complaint) values (:id, :c)',{"id":curr_customer_id,"c":complaint})
            db.session.commit()  
            return render_template('done.html', message = "Sorry for the inconvinience, your complaint has been registered", opt = 2)

        if request.form['btn'] == 'sign-out':
            return render_template('index.html')
            

    
