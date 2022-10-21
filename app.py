
from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object('config')
db = SQLAlchemy(app)

PORT = int(app.config['PORT'])
DEBUG = bool(app.config['DEBUG'])
    
@app.route("/")
def home():

    # contact = Contact(name="Mudit",email="mg@gmail.com",phone="9654238322",message="hello test")

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
        print('form Submitted!',form)
        
    return render_template('contact.html',secondaryNav = secondaryNav)

@app.route("/login")
def login():
    # secondaryNav = True;
    return "/login"

@app.route("/register")
def register():
    # secondaryNav = True;
    return "/register"

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=DEBUG,port = PORT)
    # app.run(debug=True,port = 8000)