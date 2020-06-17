from flask import Flask, render_template, request,redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from form import RegisterForm, LoginForm, EmailForm, ResetPasswordForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os 
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime 
import math, random

mail=Mail()
app = Flask(__name__)



ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SECRET_KEY'] = os.urandom(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:spoo88#asA@localhost/rove'
else:
    app.debug = False
    app.config['SECRET_KEY'] = ''
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['DEBUG'] = True
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'roveapc.2020@gmail.com'
app.config['MAIL_PASSWORD'] = '@cademic123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

bootstrap = Bootstrap(app)
db= SQLAlchemy(app)

mail.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin,db.Model):
    __tablename__ = 'User_login'
    id = db.Column(db.Integer, primary_key = True) 
    username = db.Column(db.String(15),unique=True)
    password = db.Column(db.String(80))

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer,db.ForeignKey('User_login.id'),primary_key = True)
    name = db.Column(db.String(40))
    mobile = db.Column(db.BigInteger,unique = True)
    email=db.Column(db.String(40),unique = True)
    wallet = db.Column(db.Integer,default=0)

    def __init__(self,id,name, mobile ,email,):
        self.id = id  
        self.name = name
        self.mobile = mobile
        self.email = email
    
    

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    vehicle_number = db.Column(db.String(20), primary_key = True)
    model = db.Column(db.String(20))
    address = db.Column(db.Integer, db.ForeignKey('location.id'))
    status = db.Column(db.String(20))
    curr_user = db.Column(db.Integer, db.ForeignKey('User_login.id'))
    
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
    datentime = db.Column(db.DateTime,unique= True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('User_login.id'))
   
    def __init__(self, vehicle_num, from_loc, to_loc, datentime, customer_id):
        self.vehicle_num = vehicle_num
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.datentime = datentime
        self.customer_id = customer_id
        

class Rating(db.Model):
    __tablename__="ratings"
    id = db.Column(db.Integer,db.ForeignKey('ride.id'), primary_key = True )
    rating = db.Column(db.Integer)
    feedback = db.Column(db.String)

    def __init__(self, ride_id , rating, feedback):
        self.ride_id = ride_id
        self.rating = rating
        self.feedback = feedback


class Complaint(db.Model):
    __tablename__ = "complaint"
    id = db.Column(db.Integer, primary_key = True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.id'))
    complaint = db.Column(db.String)

    def __init__(self, ride_id, complaint):
        self.ride_id = ride_id
        self.complaint = complaint


def generateOTP():
    digits = "0123456789"
    OTP = ""

    for i in range(4):
        OTP += digits[math.floor(random.random()*10)]
    return OTP 

def reset_email(user):
    token = user.get_reset_token()
    customer=Customer.query.filter_by(id=user.id).first()
    msg = Message('Password Reset Request',
                  sender='roveapc.2020@gmail.com',
                  recipients=[customer.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset', token=token, _external=True)}
Please ignore if request is not made by you. The token gets expired.
-By Team Rove 
'''
    mail.send(msg)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')

balance = 0

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                form.remember.data 
                login_user(user, remember = form.remember.data )
                print(form.remember.data)
                return redirect(url_for('book'))
            flash('Invalid Password ','warning')
            return render_template('login.html', form=form)
        flash('Invalid Login credentials','danger')  
        return redirect(url_for('login'))     
    
    return render_template('login.html', form=form)
  
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()
    fi="Username already in use."
    if form.validate_on_submit():
        
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        try :
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            try :
                new_customer = Customer(id=new_user.id ,name=form.name.data, mobile= int(form.mobile.data),email=form.email.data)
                db.session.add(new_customer)
                db.session.commit()
            except:
                fi=""
                flash('Mobile or Email already in use.','warning')
                db.session.execute('DELETE from "User_login" where username = :ids',{"ids":form.username.data})
                db.session.commit()
                return redirect(url_for('signup'))
        except:
            flash(f'{fi} Failed to create an Account .Create Account again !!','danger')
            return redirect(url_for('signup'))
        flash(f'Account created for {form.name.data}  Please Login !','success')
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)

@app.route('/resetpassword', methods=['GET','POST'])
def forgot():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = EmailForm()
    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()
        if customer is None:
            flash('There is no Account with this email. Please Register.','warning')
            return redirect(url_for('forgot'))
        user = User.query.filter_by(id = customer.id).first()
        reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)

    



@app.route('/resetpassword/<token>',methods=['GET','POST'])
def reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    user = User.verify_reset_token(token)
    if user is None:
        flash('The Token was invalid or expired ! Try Again', 'warning')
        return redirect(url_for('forgot'))
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You can Log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    
    return redirect(url_for('index'))


from_location = 'abc'
to_location = 'abc'
cost = 0
dist = 0.0
vehicle_number = "KA"
otp=0000

@app.route("/book", methods=['GET','POST'])
@login_required
def book():
    
    global from_location
    global to_location
    global cost
    global dist
    global vehicle_number
    global otp
    global n
    A = "A"
    locations = db.session.execute('SELECT distinct loc_name FROM "location" as l,"vehicle" as v where l.id = v.address and v.status=:A',{"A":A}).fetchall()
    loc = db.session.execute('SELECT loc_name FROM "location" ').fetchall()
    if request.method == "POST":

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
            res= db.session.execute('select wallet from "customer" where id= :fid',{"fid":current_user.id}).fetchone()
            balance=res[0]
            if balance < cost:
                flash(f'Balance insufficient! Please recharge your wallet.','danger')
            return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2)
            

        if request.form['btn'] == "start ride":
            if request.form['otp'] == otp:
                return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 4)
            else:
                return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 3, mesg = "wrong OTP, try again")

        if request.form['btn'] == "Add money":
            
            amount = request.form['amount']
            
            db.session.execute('UPDATE "customer" set wallet = wallet + :amt where id = :id',{"amt":amount, "id":current_user.id})
            db.session.commit()
            res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
            balance = res[0]
            return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1)

        if request.form['btn'] == "Add money ":
            
            amount = request.form['amount']
            
            db.session.execute('UPDATE "customer" set wallet = wallet + :amt where id = :id',{"amt":amount, "id":current_user.id})
            db.session.commit()
            res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
            balance = res[0]
            if balance < cost:
                flash(f'Balance insufficient! Please recharge your wallet.','warning')
            return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2)

        if request.form['btn'] == "Confirm Booking":
            res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
            balance = res[0]
            if balance < cost:
                flash(f'Balance insufficient! Please recharge your wallet.','warning')
                return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2)
            n = datetime.now()
            res = db.session.execute('SELECT id from "location" where loc_name = :f',{"f":from_location}).fetchone()
            
            fid = res[0]
            NA = "NA"
            res = db.session.execute('select vehicle_number from "vehicle" where address = :i limit 1' ,{"i": fid}).fetchone()
            vehicle_number = res[0]
            print(vehicle_number)
            db.session.execute('UPDATE "vehicle" set status = :NA where vehicle_number = :v',{"NA":NA, "v":vehicle_number})
            db.session.commit()
            db.session.execute('UPDATE "vehicle" set curr_user = :user where vehicle_number = :v',{"user":current_user.id, "v":vehicle_number})
            db.session.commit()
            otp = generateOTP()
            res = db.session.execute('SELECT email from "customer" where id = :id', {"id":current_user.id}).fetchone()
            email_id = res[0]
            msg = Message(subject=' OTP For ur Ride ', sender = 'roveapc.2020@gmail.com', recipients = [email_id])
            msg.body = f"The One Time Password for your ride is {otp} .Have a safe Journey . -by Team ROVE ."
            mail.send(msg)
            print('sent')
            res = db.session.execute('SELECT id from "location" where loc_name = :t',{"t": to_location}).fetchone()
            t = res[0]
            db.session.execute('INSERT into "ride"(vehicle_num, from_loc, to_loc, datentime, customer_id) values(:v, :f , :t, :tnc, :c)',{"v": vehicle_number, "f": fid, "t":t, "tnc":n ,"c":current_user.id})
            db.session.commit()
            res = db.session.execute('select model from "vehicle" where vehicle_number = :v ',{"v": vehicle_number}).fetchone()
            model = res[0]
            return render_template('book.html', from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 3, balance = balance, vn = vehicle_number, model = model)
        
        
        if request.form['btn'] == "finish ride":
            A = "A"
            res = db.session.execute('SELECT id from "location" where loc_name = :t',{"t":to_location}).fetchone()
            to_location_id = res[0]
            db.session.execute('UPDATE "vehicle" set status = :A, address = :to , curr_user= :Q  where vehicle_number = :v',{"A": A,"to": to_location_id,"Q":None ,"v": vehicle_number})
            db.session.execute('UPDATE "customer" set wallet = wallet - :cost where id = :cust_id ',{"cust_id":current_user.id, "cost":cost})
            db.session.commit()
            return render_template("feedback.html")
                
    res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
    balance = res[0]
    return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1)
             
    
@app.route("/feedback", methods=["POST"])
@login_required
def feedback():
    rating = request.form['rating']
    comments = request.form['comments']
    isi = db.session.execute('select id from "ride" where datentime = :t',{"t":n}).fetchone()
    idn = isi[0]
    db.session.execute('INSERT into "ratings"(id, rating, feedback) values(:v, :r, :com)',{"v":idn, "r":rating, "com":comments})
    db.session.commit()
    return render_template("done.html", opt = 1)

@app.route("/done", methods = ["POST"])
@login_required
def done():
    if request.method == "POST":
        
        if request.form['btn'] == 'New Ride':
            return redirect(url_for('book'))

        if request.form['btn'] == 'comp':
            complaint = request.form['complaint']
            res = db.session.execute('select id from "ride" where datentime = :tnc',{"tnc":n}).fetchone()
            db.session.execute('INSERT into "complaint"(ride_id, complaint) values (:iid, :c)',{"iid":res[0],"c":complaint})
            db.session.commit()  
            return render_template('done.html', message = "Sorry for the inconvinience, your complaint has been registered", opt = 2)

        if request.form['btn'] == 'sign-out':
            return redirect(url_for('logout'))

if __name__ == '__main__':
    app.run(debug=True)

'''A = "A"
                locations = db.session.execute('SELECT distinct loc_name FROM "location" as l,"vehicle" as v where l.id = v.address and v.status=:A',{"A":A}).fetchall()
                loc = db.session.execute('SELECT loc_name FROM "location" ').fetchall()
                res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
                balance = res[0]
                return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1)'''   
