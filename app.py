from flask import Flask, render_template, request, redirect
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import db, User, Item


# ---------------- APP INIT ----------------

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# ---------------- USER LOADER ----------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------- CREATE TABLES ----------------

with app.app_context():
    db.create_all()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("home.html")


# ---------------- REGISTER ----------------

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

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)
            return redirect("/dashboard")

        return "Invalid Email or Password"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    items = Item.query.filter_by(
        user_id=current_user.id,
        status="FOUND"
    ).order_by(
        Item.created_at.desc()
    ).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        items=items
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
@login_required
def logout():

    logout_user()
    return redirect("/")


# ---------------- ADD FOUND ITEM ----------------

@app.route("/add-found", methods=["GET", "POST"])
@login_required
def add_found():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        location = request.form["location"]

        # OPTIONAL (if you added category)
        category = request.form.get("category", "Other")

        new_item = Item(
            title=title,
            description=description,
            location=location,
            category=category,
            status="FOUND",
            user_id=current_user.id
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect("/dashboard")

    return render_template("add_found.html")


# ---------------- ITEMS FEED (FOUND ONLY) ----------------

@app.route("/items")
@login_required
def items():

    all_items = Item.query.filter_by(
        status="FOUND"
    ).order_by(
        Item.created_at.desc()
    ).all()

    return render_template("items.html", items=all_items)


# ---------------- DELETE ITEM ----------------

@app.route("/delete-item/<int:item_id>")
@login_required
def delete_item(item_id):

    item = Item.query.get_or_404(item_id)

    if item.user_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(item)
    db.session.commit()

    return redirect("/dashboard")


# ---------------- ITEM DETAIL PAGE ----------------

@app.route("/item/<int:item_id>")
@login_required
def item_detail(item_id):

    item = Item.query.get_or_404(item_id)

    return render_template("item_detail.html", item=item)


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)