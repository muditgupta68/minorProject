from flask import Flask,render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    pass
    # return render_template('about.html')

@app.route("/contact")
def contact():
    return "<h1>Hello, Contact!</h1>"

if __name__ == "__main__":
    app.run(debug=True,port=8000)