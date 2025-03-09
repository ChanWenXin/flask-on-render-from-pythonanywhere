# Import necessary libraries and modules
from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    LoginManager,
    logout_user,
    UserMixin,
)
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash
import pytz  # Import for time zone handling

# Initialize the Flask application
app = Flask(__name__)

# Enable debugging mode for easier troubleshooting during development
app.config["DEBUG"] = True

# Database connection URI
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="wenxin",  # Replace with your database username
    password="SQL123456",  # Replace with your database password
    hostname="wenxin.mysql.pythonanywhere-services.com",  # Database hostname
    databasename="wenxin$comments",  # Database name
)

# Configure SQLAlchemy for the Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299  # Recycle database connections
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Suppress modification tracking warnings
db = SQLAlchemy(app)  # Initialize SQLAlchemy
migrate = Migrate(app, db)  # Enable database migrations

# Secret key for session management and login functionality
app.secret_key = "SOMETHING RANDOM"

# Initialize Flask-Login for user session management
login_manager = LoginManager()
login_manager.init_app(app)

# Define Singapore timezone
singapore_tz = pytz.timezone("Asia/Singapore")

# User model: Represents users in the database
class User(UserMixin, db.Model):
    __tablename__ = "users"

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    username = db.Column(db.String(128))  # Username column
    password_hash = db.Column(db.String(128))  # Hashed password column

    # Method to check the user's password during login
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Flask-Login requires a method to get the user's ID
    def get_id(self):
        return self.username


# Flask-Login loader: Load a user based on their username
@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()


# Comment model: Represents comments posted by users
class Comment(db.Model):
    __tablename__ = "comments"

    # Define table columns
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    content = db.Column(db.String(4096))  # Comment content
    posted = db.Column(db.DateTime, default=datetime.now)  # Date and time posted
    commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    commenter = db.relationship("User", foreign_keys=commenter_id)  # Relationship to User table

# Home Page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("home_page.html")

# Skills Page
@app.route("/skills/")
def skills():
    return render_template("skills_page.html")

# Projects Page
@app.route("/projects/")
def projects():
    return render_template("project_page.html")

# Education Page
@app.route("/education/")
def education():
    return render_template("education_page.html")

# Experience Page
@app.route("/experience/")
def experience():
    return render_template("experience_page.html")

# Comment Page
# Home page: Displays comments and allows logged-in users to post comments
@app.route("/comments", methods=["GET", "POST"])
def comments():
    if request.method == "GET":
        # Convert times to Singapore time before sending them to the template
        comments = Comment.query.all()
        for comment in comments:
            if comment.posted:
                comment.posted = comment.posted.replace(tzinfo=pytz.utc).astimezone(singapore_tz)
        return render_template("comment_page.html", comments=comments)


    # Ensure only logged-in users can post comments
    if not current_user.is_authenticated:
        return redirect(url_for("comments"))

    # Add a new comment to the database
    comment = Comment(content=request.form["contents"], commenter=current_user)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for("comments"))


# Login page: Allows users to log in with their credentials
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # Render the login page
        return render_template("login_page.html", error=False)

    # Load the user based on the username provided
    user = load_user(request.form["username"])
    # Validate username and password
    if user is None or not user.check_password(request.form["password"]):
        return render_template("login_page.html", error=True)

    # Log in the user and redirect to the home page
    login_user(user)
    return redirect(url_for("comments"))


# Logout route: Logs out the current user
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("comments"))
