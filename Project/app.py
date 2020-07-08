from flask import Flask, render_template, request,redirect, url_for, flash,send_file
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from form import RegisterForm, LoginForm, EmailForm, ResetPasswordForm,UploadForm,UpdateProfile
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_uploads import UploadSet,configure_uploads,IMAGES
import os 
from io import BytesIO

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime 
import math, random


app = Flask(__name__)



ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SECRET_KEY'] = os.urandom(16)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:spoo88#asA@localhost/rove'
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
else:
    app.debug = False
    app.config['SECRET_KEY'] = ''
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['UPLOADS_DEFAULT_DEST']='static/images/uploads'


app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'roveapc.2020@gmail.com'
app.config['MAIL_PASSWORD'] = '@cademic123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True



bootstrap = Bootstrap(app)
db= SQLAlchemy(app)
mail=Mail(app)

pics = UploadSet('pics',IMAGES)
configure_uploads(app,pics)


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
 

    def __init__(self,id,name, mobile ,email):
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
        self.id = ride_id
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

class Picture(db.Model):
    __tablename__="customer_License"
    id=db.Column(db.Integer,db.ForeignKey('customer.id'),primary_key=True)
    License=db.Column(db.LargeBinary)
                                            
    def __init__(self,customer_id,License):
        self.id=customer_id
        self.License=License
class Propic(db.Model):
    __tablename__="profile"
    id=db.Column(db.Integer,db.ForeignKey('customer.id'),primary_key=True)
    pic_url=db.Column(db.String(256))

    def __init__(self,customer_id,pic_url):
        self.id=customer_id
        self.pic_url=pic_url

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
    if current_user.is_authenticated:
        return render_template('index.html',opt=1)

    return render_template('index.html',opt=2)

balance = 0

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if current_user.is_authenticated:
        flash(f'Logged in as {current_user.username} ','success')
        return redirect(url_for('book'))

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                
                login_user(user, remember = form.remember.data)
               
                return redirect(url_for('book'))
            flash('Invalid Password ','warning')
            return render_template('login.html', form=form)
        flash('Invalid Login credentials','danger')  
        return redirect(url_for('login'))     
    
    return render_template('login.html', form=form)
  
@app.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        flash('Already Signed In .Press Log In to continue','success')
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
        flash('Upload Your two Wheeler License and continue','success')
        return redirect(url_for('DL',name=form.name.data))
    return render_template('signup.html',form=form)

@app.route('/DL:<name>',methods=['GET','POST'])
def DL(name):
    form= UploadForm()
    if form.validate_on_submit():
        customer= Customer.query.filter_by(name=name).first()
        if customer is None :
            flash('No customer with this name','warning')
            return redirect(url_for('signup'))
       
        try:
            files = form.license.data
            
            picture=Picture(customer_id=customer.id,License=files.read())
            db.session.add(picture)
            uril="https://static.wixstatic.com/media/cd5c35_e4e3005990ea4a879a280fd6dfe3bdbf~mv2.jpg/v1/fill/w_312,h_318,al_c,q_80,usm_0.66_1.00_0.01/empty-dp.webp"
            newprofile = Propic(customer_id=customer.id,pic_url=uril)
            db.session.add(newprofile)
            db.session.commit()
        except:
            flash('Couldnt Insert License','danger')
            db.session.execute('delete from "customer" where id= :ids',{"ids":customer.id})
            db.session.execute('DELETE from "User_login" where id = :ids',{"ids":customer.id})
            db.session.execute('DELETE from "profile" where id= : ids',{"ids":customer.id})
            db.session.commit()
            return redirect(url_for('signup'))
        flash(f'Account created for {name}  Please Login !','success')
        return redirect(url_for('login'))
    return render_template("imageupload.html",form=form)

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
        flash('An email has been sent with instructions to reset your password.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', form=form)


    

@app.route('/download',methods=['GET','POST'])
@login_required
def download():
    mylicense=Picture.query.filter_by(id=current_user.id).first()
    return send_file(BytesIO(mylicense.License),attachment_filename=f'{current_user.username} License.jpeg' ,as_attachment=True)

@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    
    myprofile = db.session.execute('select u.username,c.name,c.mobile,c.email,c.wallet from "User_login" as u, customer as c where c.id=u.id and c.id=:ids',{"ids":current_user.id}).fetchone()
    history=db.session.execute('select r.vehicle_num, v.model, l1.loc_name as from, l2.loc_name as to, r.datentime from ride as r ,location  as l1,location as l2,vehicle as v where r.vehicle_num=v.vehicle_number and r.from_loc=l1.id and r.to_loc=l2.id and customer_id =:ids',{"ids":current_user.id}).fetchall() 
    url=db.session.execute('select pic_url from profile where id=:ids',{"ids":current_user.id}).fetchone() 
    return render_template('profile.html',myprofile=myprofile,history=history,profileurl=url[0])


@app.route('/update',methods=["GET","POST"])
@login_required
def update():
    form = UpdateProfile()
    if form.validate_on_submit():
        filename=secure_filename(pics.save(form.pic.data))
        filename_url=pics.url(filename)
        
        
        f"filename = {filename_url}"
        db.session.execute('UPDATE profile set pic_url=:url where id=:ids',{"url":filename_url,"ids":current_user.id})
        db.session.commit()
        flash('Photo Updated Successfully','success')
        return redirect(url_for('profile'))
    return render_template('profileupdate.html',form=form)
    

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
        return render_template('success.html',message = user.username)
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
model=""
url=""
@app.route("/book", methods=['GET','POST'])
@login_required
def book():
    
    global from_location
    global to_location
    global cost
    global dist
    global vehicle_number
    global model
    global otp
    global n
    global url
    
    A = "A"
    locations = db.session.execute('SELECT distinct loc_name FROM "location" as l,"vehicle" as v where l.id = v.address and v.status=:A',{"A":A}).fetchall()
    loc = db.session.execute('SELECT loc_name FROM "location" ').fetchall()
    url=db.session.execute('select pic_url from profile where id=:ids',{"ids":current_user.id}).fetchone() 
    if request.method == "POST":

        if request.form['btn'] == "book ride":
            f = request.form['from']

            from_location = f
            t = request.form['to']
            to_location = t
            print(from_location)
            try:
                res = db.session.execute('SELECT x_coordinate, y_coordinate FROM "location" where loc_name =:from ',{"from":f}).fetchone()
                x1 = res[0]
                y1 = res[1]
                res = db.session.execute('SELECT x_coordinate, y_coordinate FROM "location" where loc_name =:to ',{"to":t}).fetchone()
                x2 = res[0]
                y2 = res[1]
            except:
                flash('Please select From and To Locations','danger')
                return redirect(url_for('book'))
            dist = round((math.sqrt((x1-x2)**2 + (y1-y2)**2)), 2)
            cost = int(dist * 3)
            A = "A"
            res= db.session.execute('select wallet from "customer" where id= :fid',{"fid":current_user.id}).fetchone()
            balance=res[0]
            if balance < cost:
                flash(f'Balance insufficient! Please recharge your wallet.','danger')
            return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2,username=current_user.username,profileurl=url[0])
            

        if request.form['btn'] == "start ride":
            if request.form['otp'] == otp:
                return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 4,username=current_user.username,profileurl=url[0])
            else:
                res= db.session.execute('select wallet from "customer" where id= :fid',{"fid":current_user.id}).fetchone()
                balance=res[0]
                return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 3, balance = balance, vn = vehicle_number, model = model, mesg = "wrong OTP, try again",username=current_user.username,profileurl=url[0])

        if request.form['btn'] == "Add money":
            
            amount = request.form['amount']
            try:
                if int(amount) > 0 :
                    db.session.execute('UPDATE "customer" set wallet = wallet + :amt where id = :id',{"amt":amount, "id":current_user.id})
                    db.session.commit()
                    res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
                    balance = res[0]
                else :
                    res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
                    balance = res[0]
                    flash('Negative Amount','danger')
            except:
                flash('Invalid Amount ','danger')
                return redirect(url_for('book'))
            
            return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1,username=current_user.username,profileurl=url[0])

        if request.form['btn'] == "Add money ":
            
            amount = request.form['amount']
            res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
            balance = res[0]
            try:
                if int(amount) > 0 :
                    db.session.execute('UPDATE "customer" set wallet = wallet + :amt where id = :id',{"amt":amount, "id":current_user.id})
                    db.session.commit()
                    res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
                    balance = res[0]
                else :
                    res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
                    balance = res[0]
                    flash('Negative Amount','danger')
            except:
                flash('Invalid Amount','danger')
            if balance < cost:
                flash(f'Balance insufficient! Please recharge your wallet.','warning')
            return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2,username=current_user.username,profileurl=url[0])

        if request.form['btn'] == "Confirm Booking":
            res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
            balance = res[0]
            if balance < cost:
                flash(f'Balance insufficient! Please recharge your wallet.','warning')
                return render_template('book.html',from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, balance = balance, opt = 2,username=current_user.username,profileurl=url[0])
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
            print(otp)
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
            return render_template('book.html', from_loc = from_location, to_loc = to_location, cost= cost, dist = dist, opt = 3, balance = balance, vn = vehicle_number, model = model,username=current_user.username,profileurl=url[0])
        
        
        if request.form['btn'] == "finish ride":
            A = "A"
            res = db.session.execute('SELECT id from "location" where loc_name = :t',{"t":to_location}).fetchone()
            to_location_id = res[0]
            db.session.execute('UPDATE "vehicle" set status = :A, address = :to , curr_user= :Q  where vehicle_number = :v',{"A": A,"to": to_location_id,"Q":None ,"v": vehicle_number})
            db.session.execute('UPDATE "customer" set wallet = wallet - :cost where id = :cust_id ',{"cust_id":current_user.id, "cost":cost})
            db.session.commit()
            return redirect (url_for('feedback'))               
    res = db.session.execute('SELECT wallet from "customer" where id = :id', {"id":current_user.id}).fetchone()
    balance = res[0]
    return render_template('book.html', locations = locations, loc = loc, balance = balance, opt = 1,username=current_user.username,profileurl=url[0])
             
    
@app.route("/feedback", methods=["GET","POST"])
@login_required
def feedback():
    
    if request.method == "POST":
        if request.form['btn'] == 'Submit':
            rating = request.form['rating']
            comments = request.form['comments']
            isi = db.session.execute('select id from "ride" where datentime = :t',{"t":n}).fetchone()
            idn = isi[0]
            db.session.execute('INSERT into "ratings"(id, rating, feedback) values(:v, :r, :com)',{"v":idn, "r":rating, "com":comments})
            db.session.commit()
            return redirect(url_for('done'))
    return render_template("feedback.html")

@app.route("/done", methods = ["GET","POST"])
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

        
    return render_template("done.html", opt = 1)

if __name__ == '__main__':
    app.run(debug=True)
