from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import string

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///shoppers.db")


@app.route("/")
@login_required
def index():
    """Show entire shopping list"""

    lists = db.execute("SELECT item_name, store_name, SUM(quantity) FROM stores, items, users WHERE users.id = :id AND users.id = items.user_id AND stores.store_id = items.store_id GROUP BY item_name, store_name",
                         id=session["user_id"])

    for i in lists:
        if i["item_name"].find("'") != -1:
            i["item_name"] = i["item_name"].replace("'", "\\'")
        if i["store_name"].find("'") != -1:
            i["store_name"] = i["store_name"].replace("'", "\\'")

    # Render portfolio
    return render_template("index.html", lists=lists)

@app.route("/edit", methods=["POST"])
@login_required
def edit():
    if request.method == "POST":
        return apology("edit page")
    else:
        return render_template("edit.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Enable user to add an item to his/her shopping list."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("item"):
            flash("Please input an item.", 'danger')
            return render_template("add.html")
        elif not request.form.get("store"):
            flash("Please input a store.", 'danger')
            return render_template("add.html")

        stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))

        if not stores:
            flash("Store was not found.", 'danger')
            return render_template("add.html")

        exists = db.execute("SELECT store_name, items.store_id, item_name FROM items, stores WHERE stores.store_id = items.store_id AND items.store_id = :store AND item_name LIKE :item AND user_id = :id",
                            store=stores[0]["store_id"], item=request.form.get("item"), id=session["user_id"])

        if not exists:
            # Add item to list
            db.execute("""INSERT INTO items (user_id, item_name, store_id)
                VALUES(:user_id, :item_name, :store_id)""",
                    user_id=session["user_id"], item_name=request.form.get("item"), store_id = stores[0]["store_id"])

            # Display portfolio
            flash("Items added to shopping list!", 'success')
            return redirect("/")

        else:
            return render_template("add2.html", item=exists[0]["item_name"], store=exists[0]["store_name"])

    # GET
    else:
        return render_template("add.html")

@app.route("/add2", methods=["POST"])
@login_required
def add2():
    if request.method == "POST":
        if request.form["submit"] == "n":
            flash("Item not added to shopping list.", 'danger')
            return redirect("/")
        else:
            item,store=(request.form["submit"]).split(",")

            stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = store)

            db.execute("""INSERT INTO items (user_id, item_name, store_id)
                VALUES(:user_id, :item_name, :store_id)""",
                    user_id=session["user_id"], item_name=item, store_id = stores[0]["store_id"])

            flash("Item Added!", 'success')
            return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide a username.", 'danger')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide a password.", 'danger')
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Username and password do not match.", 'danger')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/check", methods=["GET", "POST"])
@login_required
def check():
    """Check if a store exists in the current database."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("store"):
            flash("Must input a store.", 'danger')
            return render_template("check.html")

        # Get store id
        store = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))
        if not store:
            return render_template("newstore.html", store=request.form.get("store"))


        # return apology("Store does not exist")

        # Display if store exists
        flash("Store Exists!", 'success')
        return redirect("/")

    # GET
    else:
        return render_template("check.html")

@app.route("/newstore", methods=["POST"])
@login_required
def newstore():
    if request.method == "POST":
        if request.form["submit"] == "n":
            flash("Store Not Added.", 'danger')
            return redirect("/")
        else:
            db.execute("INSERT INTO stores (store_name) VALUES (:name)", name=capitalize(request.form["submit"]))
            flash("Store Added!", 'success')
            return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("username"):
            flash("Must provide a username.", 'danger')
            return render_template("register.html")
        elif not request.form.get("password"):
            flash("Must provide a password.", 'danger')
            return render_template("register.html")
        elif request.form.get("password") != request.form.get("confirmation"):
            flash("Password not confirmed.", 'danger')
            return render_template("register.html")

        # Add user to database
        id = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
                        username=request.form.get("username"),
                        hash=generate_password_hash(request.form.get("password")))
        if not id:
            flash("Username taken.", 'danger')
            return render_template("register.html")

        # Log user in
        session["user_id"] = id

        # Let user know they're registered
        flash("Registered!", 'success')
        return redirect("/")

    # GET
    else:
        return render_template("register.html")


@app.route("/shop", methods=["GET", "POST"])
@login_required
def shop():
    """Generates shopping sublist based on which store they are shopping at."""

    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("store"):
            flash("Where are you shopping?", 'danger')
            return render_template("shop.html")

        stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))

        if not stores:
            flash("Store was not found.", 'danger')
            return render_template("shop.html")

        items = db.execute('SELECT item_name, store_name, SUM(quantity) FROM items, stores, users WHERE items.store_id = stores.store_id AND stores.store_name LIKE :name AND items.user_id = users.id AND users.id = :id GROUP BY item_name',
                            id=session["user_id"], name=request.form.get("store"))

        # Display portfolio
        return render_template("list.html", items=items, store=items[0]["store_name"])

    # GET
    else:

        # Display sales form
        return render_template("shop.html")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# capitalize store names
def capitalize(store):
    return ' '.join(s[:1].upper() + s[1:] for s in store.split(' '))
