from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash
from flask import Flask
from config import Config
from models import db
from werkzeug.security import check_password_hash
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.config.from_object(Config)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("home.html")
from models import db, User , Item

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered"

        hashed_password = generate_password_hash(password)

        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")
@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html",
        user=current_user
    )
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect("/")
@app.route("/add-lost", methods=["GET", "POST"])
@login_required
def add_lost():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]

        new_item = Item(
            title=title,
            description=description,
            location=location,
            status="LOST",
            user_id=current_user.id
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("add_lost.html")

if __name__ == "__main__":
    app.run(debug=True)