from flask import Flask,render_template,request,redirect, url_for,flash, session,make_response,jsonify
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps
from datetime import datetime, timedelta

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# models initializations
class Contact(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(70),nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(15000), nullable=False)
    date = db.Column(db.DateTime,default=datetime.utcnow)
    
    def __repr__(self):
        return f"{self.id} - {self.name}"

class User(db.Model):
    
    id = db.Column(db.Integer,primary_key=True)
    userName = db.Column(db.String(70),nullable=False)
    userEmail = db.Column(db.String(120), nullable=False,unique=True)
    password = db.Column(db.String(12), nullable=False,unique=True)
    active = db.Column(db.Boolean,default=True)
    date = db.Column(db.DateTime,default=datetime.utcnow)
    
    def __repr__(self):
        return f"{self.id} - {self.userName}:{self.userEmail}:{self.active}:{self.date}"

# initiate vars
PORT = int(app.config['PORT'])
DEBUG = int(app.config['DEBUG'])
SECRET_KEY = app.config['SECRET_KEY']

gmail_user = os.environ.get('gmail_user')
gmail_pass = os.environ.get('gmail_pass')

bcrypt.init_app(app)
    
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME = gmail_user,
    MAIL_PASSWORD = gmail_pass
)
mail = Mail(app)

# main begins apps

def load_user(email):
    return User.query.filter_by(userEmail=email).first()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if session.get("token"):
            token = session.get("token")
        
        if not token:
            flash("Authorization not granted! Please login")
            return redirect(url_for('login'))

        # print(token,type(token))
        print(session.get("token_exp") == datetime.utcnow() + timedelta(seconds=0))
        
        if session.get("token_exp") == datetime.utcnow() + timedelta(seconds=0):
            session.clear()
            flash("Authentication Expired, Login Again!")
            return redirect(url_for('login'))
        
        try:
            data = jwt.decode(token, SECRET_KEY,'utf-8')
            current_user = User.query\
                    .filter_by(id = data['userId'])\
                    .first()
            session["current_user"] = current_user
            print(current_user)
            if current_user.active == False:
                session.clear()
                flash("Please Activate your account! ERR:500")
                return redirect(url_for('login'))
            
            # to extract data
            # data = session.get("current_user")
            # print(data.id)
            return f(current_user, *args, **kwargs)

        except:
            session.clear()
            flash("Token-Auth Error! Try Again!")
            return redirect(url_for('login'))
        
    return decorated

def check_user(route_name):
    @wraps(route_name)
    def check_user_decoration(*args, **kwargs):
        if session.get('user_Login') and session.get('user_Login')==True:
            return redirect(url_for('dashboard'))
        else:
            return route_name()
    return check_user_decoration

@app.route("/", methods =['GET'])
def home():
    # if session.get('user_Login') and session.get('user_Login')==True:
    #     return redirect(url_for('dashboard'))
    userData = None
    if session.get('current_user'):
        userData = session.get("current_user")
    return render_template('home.html',userData=userData)

@app.route("/dashboard", methods =['GET'])
@token_required
def dashboard(current_user):
    userData = session.get("current_user")
    return render_template('dashIndex.html',userData=userData)

@app.route("/logout", methods =['GET'])
@token_required
def logout(current_user):
    if current_user:
        session.clear()
        return redirect(url_for('home'))
    
@app.route("/deactivate", methods =['GET'])
@token_required
def deactivate(current_user):
    if current_user:
        userData = load_user(current_user.userEmail)
        userData.active = False
        db.session.commit()
        session.clear()
        return redirect(url_for('home'))
    
@app.route("/allMembers", methods =['GET'])
@token_required
def allMembers(current_user):
    userData = session.get("current_user")
    allUsers = getAllMembers();
    return render_template('members.html',userData=userData,allUsers=allUsers)

@app.route("/detection", methods =['GET'])
@token_required
def detection(current_user):
    userData = session.get("current_user")
    return render_template('dashPredict.html',userData=userData)

def getAllMembers():
    users = User.query.all()
    # print(users);
    return users;
    

@app.route("/about", methods =['GET'])
def about():
    secondaryNav = True;
    userData = None
    if session.get('current_user'):
        userData = session.get("current_user")
    return render_template('about.html',secondaryNav = secondaryNav,userData=userData)

@app.route("/team", methods =['GET'])
def teams():
    secondaryNav = True;
    userData = None
    if session.get('current_user'):
        userData = session.get("current_user")
    return render_template('team.html',secondaryNav = secondaryNav,userData=userData)

@app.route("/contact",methods=['GET','POST'])
def contact():
    secondaryNav = False
    userData = None
    if session.get('current_user'):
        userData = session.get("current_user")
    if request.method == 'POST':
        form = request.form
        name = form['name']
        email = form['email']
        phone = form['phone']
        message = form['message']

        contactData = Contact(name=name,email=email,phone=phone,message=message)
        db.session.add(contactData)
        db.session.commit()
        
        mail.send_message(' 📦 New message for PedDetector',
                            sender = 'yourId@gmail.com',
                            recipients = [gmail_user],
                            html = render_template('/emails/contactMessage.html',
                                                   name=name,msg=message,phone=phone,email=email)
                        )
        
        if userData:
            return redirect(url_for("dashboard"))
        return redirect(url_for("home"))
        
    return render_template('contact.html',secondaryNav = secondaryNav,userData = userData)

@app.route("/login",methods=['GET','POST'])
@check_user
def login():
    secondaryNav = True;
    msg = ""
    if request.method == 'POST':
        auth = request.form
        userEmail = auth['userEmail']
        password = auth['password']
        
        userData = load_user(userEmail)
        
        # print(userData)
        
        if not userData:
            msg = "WWW-Authenticate : /ERROR 404 = User does not exist!!"
            make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm = "Login required !!"'}
            )
            return render_template('login.html',secondaryNav = secondaryNav,msg=msg)
        
        if bcrypt.check_password_hash(userData.password, password):
            
            userData.active = True
            db.session.commit()
            
            claims = {
                'userId': userData.id,
                'exp' : datetime.utcnow() + timedelta(hours=2)
            }
            
            # token = jwt.encode(claims,SECRET_KEY, algorithm='HS256')
            
            encoded_token = jwt.encode(claims, SECRET_KEY,'HS256').decode('utf-8')
            
            # print(encoded_token)
            
            make_response(jsonify({'token' : encoded_token},201))
            
            # session["email"] = request.form.get("userEmail")
            session["token"] = encoded_token
            session["user_Login"] = True
            session["token_exp"] = claims['exp']
            
            # print(datetime.utcnow() + timedelta(seconds=0) == claims['exp'])
            
            # print(session['email'])
            # print(token)
            
            return redirect(url_for('dashboard'))
        
        msg = "Incorrect Credentials, Try Again!"
        return render_template('login.html',secondaryNav = secondaryNav,msg=msg)
            
            

    return render_template('login.html',secondaryNav = secondaryNav,msg=msg)

@app.route("/register",methods=['GET','POST'])
@check_user
def register():
    secondaryNav = True;
    msg = ""
    if request.method == 'POST':
        
        auth = request.form
        userName = auth['userName']
        userEmail = auth['userEmail']
        password = auth['password']
        cPassword = auth['cPassword']
        
        userData = load_user(userEmail)
        
        if not userData:
            if cPassword == password:
                pw_hash = bcrypt.generate_password_hash(password,12).decode('utf-8')
                userResp = User(userName=userName,userEmail=userEmail,password=pw_hash)
                db.session.add(userResp)
                db.session.commit()
                flash("Your Data has been registered")
                return redirect(url_for('login'))
            else:
                msg="No valid Credentials, Try Again!"
                return render_template('register.html',secondaryNav = secondaryNav,msg = msg)       
        else:
            msg="User Already Exists!"
            return render_template('register.html',secondaryNav = secondaryNav,msg = msg)
        
    return render_template('register.html',secondaryNav = secondaryNav,msg = msg)

@app.errorhandler(404)
def page_not_found(e):
    secondaryNav = True;
    return render_template('404.html',secondaryNav = secondaryNav), 404

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=DEBUG,port = PORT)