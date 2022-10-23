from flask import Flask,render_template,request,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

PORT = int(app.config['PORT'])
DEBUG = int(app.config['DEBUG'])

gmail_user = os.environ.get('gmail_user')
gmail_pass = os.environ.get('gmail_pass')

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False,
    MAIL_USERNAME = gmail_user,
    MAIL_PASSWORD = gmail_pass
)
mail = Mail(app)
    
@app.route("/")
def home():
    return render_template('home.html')

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
        
        return redirect(url_for("home"),200)
        
    return render_template('contact.html',secondaryNav = secondaryNav)

@app.route("/login",methods=['GET','POST'])
def login():
    secondaryNav = True;
    if request.method == 'POST':
        pass
    return render_template('login.html',secondaryNav = secondaryNav)

@app.route("/register",methods=['GET','POST'])
def register():
    secondaryNav = True;
    if request.method == 'POST':
        pass
    return render_template('register.html',secondaryNav = secondaryNav)

@app.errorhandler(404)
def page_not_found(e):
    secondaryNav = True;
    return render_template('404.html',secondaryNav = secondaryNav), 404

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=DEBUG,port = PORT)