from pickle import FALSE
from flask import Flask,render_template

app = Flask(__name__)

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

@app.route("/contact")
def contact():
    secondaryNav = False;
    return render_template('contact.html',secondaryNav = secondaryNav)

if __name__ == "__main__":
    app.run(debug=True,port=8000)