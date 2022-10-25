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

def load_user(email):
    from models import User
    return User.query.filter_by(userEmail=email).first()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if session.get("token"):
            token = session.get("token")
        
        if not token and not session.get("email"):
            flash("No authorization found! Please login")
            return redirect(url_for('login'))
        
        # print(token,type(token))
        
        try:
            data = jwt.decode(token, 'hello','utf-8')
            from models import User
            current_user = User.query\
                    .filter_by(id = data['userId'])\
                    .first()
            print(current_user)
            return render_template('dashboard.html',userData = current_user)
        except:
            # print("decoded_DATA:",data)
            # print(data['userId'])
            flash("Token-Auth Error! Try Again!")
            return redirect(url_for('login'))
        
    return decorated

@app.route("/", methods =['GET'])
def home():
    return render_template('home.html')

@app.route("/dashboard", methods =['GET'])
@token_required
def dashboard():
    return '/dashboard'

@app.route("/about")
def about():
    secondaryNav = True;
    return render_template('about.html',secondaryNav = secondaryNav)

@app.route("/team")
def teams():
    secondaryNav = True;
    return render_template('team.html',secondaryNav = secondaryNav)

@app.route("/contact",methods=['GET','POST'])
def contact():
    secondaryNav = False;
    if request.method == 'POST':
        form = request.form
        name = form['name']
        email = form['email']
        phone = form['phone']
        message = form['message']
        
        from models import Contact
        contactData = Contact(name=name,email=email,phone=phone,message=message)
        db.session.add(contactData)
        db.session.commit()
        
        mail.send_message(' 📦 New message for PedDetector',
                            sender = 'yourId@gmail.com',
                            recipients = [gmail_user],
                            # body = f"Respected Team,\n\n{message}\n\nRegards,\n{name}\n{phone}",
                            # body="\nMESSAGE:\n" + message + "\nRegards,\n"+name+"\n"+phone
                            html = render_template('/emails/contactMessage.html',
                                                   name=name,msg=message,phone=phone,email=email)
                            )
        
        return redirect(url_for("home"))
        
    return render_template('contact.html',secondaryNav = secondaryNav)

@app.route("/login",methods=['GET','POST'])
def login():
    secondaryNav = True;
    msg = ""
    if request.method == 'POST':
        from models import User
        auth = request.form
        userEmail = auth['userEmail']
        password = auth['password']
        
        userData = load_user(userEmail)
        
        # print(userData)
        
        if not userData:
            msg = "WWW-Authenticate : 'Basic realm' = User does not exist !!"
            make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
            )
            return render_template('login.html',secondaryNav = secondaryNav,msg=msg)
        
        if bcrypt.check_password_hash(userData.password, password):
            
            claims = {
                'userId': userData.id,
                'exp' : datetime.utcnow() + timedelta(minutes = 30)
            }
            
            # token = jwt.encode(claims,SECRET_KEY, algorithm='HS256')
            
            encoded_token = jwt.encode(claims, 'hello','HS256').decode('utf-8')
            
            # print(encoded_token)
            
            make_response(jsonify({'token' : encoded_token},201))
            
            session["email"] = request.form.get("userEmail")
            session["token"] = encoded_token
            
            # print(session['email'])
            # print(token)
            
            return redirect(url_for('dashboard'))
        
        msg = "Incorrect Credentials, Try Again!"
        return render_template('login.html',secondaryNav = secondaryNav,msg=msg)
            
            

    return render_template('login.html',secondaryNav = secondaryNav,msg=msg)

@app.route("/register",methods=['GET','POST'])
def register():
    secondaryNav = True;
    msg = ""
    if request.method == 'POST':
        from models import User
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