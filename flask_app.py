
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="wenxin",
    password="SQL123456",
    hostname="wenxin.mysql.pythonanywhere-services.com",
    databasename="wenxin$comments",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Comment model
class Comment(db.Model):

    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))


@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("main_page.html", comments=Comment.query.all())

    comment = Comment(content=request.form["contents"])
    db.session.add(comment)
    db.session.commit()
    return redirect (url_for('index'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login_page.html", error=False)

    if request.form["username"] != "admin" or request.form["password"] != "secret":
        return render_template("login_page.html", error=True)

    return redirect(url_for('index'))


