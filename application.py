from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import string
import os
import sqlalchemy

from functools import wraps
# Configure application
app = Flask(__name__)



def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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

    # gets compiled list of all the items user wants to buy and groups them together
    lists = db.execute("SELECT item_name, store_name, SUM(quantity) FROM stores, items, users WHERE users.id = :id AND users.id = items.user_id AND stores.store_id = items.store_id GROUP BY item_name, store_name",
                         id=session["user_id"])

    # Adds an escape backslash to names with apostrophes so that they may show up in HTML code
    for i in lists:
        if i["item_name"].find("'") != -1:
            i["item_name"] = i["item_name"].replace("'", "\\'")
        if i["store_name"].find("'") != -1:
            i["store_name"] = i["store_name"].replace("'", "\\'")

    # Render shopping list
    return render_template("index.html", lists=lists)

@app.route("/edit", methods=["POST"])
@login_required
def edit():
    if request.method == "POST":

        # original values
        oname = request.form.get("oname")
        ostore = request.form.get("ostore")
        oquan = int(request.form.get("oquan"))

        # store id of original store
        sid = db.execute("SELECT store_id FROM stores WHERE store_name = :store", store=ostore)

        # delete the given row from where you clicked update --> delete
        if request.form["submit"] == "delete":
            db.execute("DELETE FROM items WHERE store_id = :store AND item_name LIKE :item AND user_id = :user_id",
                        store=sid[0]["store_id"], item=oname, user_id = session["user_id"])
            flash("Deleted.", 'danger')
            return redirect("/")
        # updates
        else:
            # new values
            nname = request.form.get("item")
            nstore = request.form.get("store")
            nquan = int(request.form.get("quantity"))

            # new quantity
            quan = nquan-oquan

            if not (db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store=nstore)):
                flash("Store not found.", 'danger')
                return redirect("/")

            # changes quantity
            if quan < 0:
                db.execute("DELETE FROM items WHERE store_id = :store AND item_name LIKE :item AND user_id = :user_id",
                            store=sid[0]["store_id"], item=oname, user_id = session["user_id"])
                db.execute("""INSERT INTO items (user_id, item_name, store_id, quantity) VALUES (:user_id, :item_name, :store_id, :quantity)""",
                            user_id = session["user_id"], item_name = oname, store_id = sid[0]["store_id"], quantity = nquan)
            elif quan > 0:
                db.execute("""INSERT INTO items (user_id, item_name, store_id, quantity) VALUES (:user_id, :item_name, :store_id, :quantity)""",
                            user_id = session["user_id"], item_name = oname, store_id = sid[0]["store_id"], quantity = quan)
            # changes item name
            if nname != oname:
                existname = db.execute("SELECT item_name FROM items WHERE item_name LIKE :name AND user_id = :userid", name = nname, userid = session["user_id"])
                if existname:
                    nname = existname[0]["item_name"]
                db.execute("""UPDATE items SET item_name=:new WHERE item_name = :oname AND store_id = :storeid AND user_id=:userid""",
                            new = nname, oname=oname, storeid=sid[0]["store_id"],userid=session["user_id"])
            # changes store name
            if nstore != ostore:
                db.execute("UPDATE items SET store_id = :storeid WHERE item_name=:name AND store_id=:oldid AND user_id=:userid",
                            storeid=(db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store=nstore))[0]["store_id"],
                            name=nname, oldid=sid[0]["store_id"], userid=session["user_id"])
        flash("Success!", 'success')
        return redirect("/")


@app.route("/subedit", methods=["POST"])
@login_required
def subedit():
    if request.method == "POST":

        # original values
        oname = request.form.get("oname")
        ostore = request.form.get("ostore")
        oquan = int(request.form.get("oquan"))

        # store id of original store
        sid = db.execute("SELECT store_id FROM stores WHERE store_name = :store", store=ostore)

        # delete the given row from where you clicked update --> delete
        if request.form["submit"] == "delete":
            db.execute("DELETE FROM items WHERE store_id = :store AND item_name LIKE :item AND user_id = :user_id",
                        store=sid[0]["store_id"], item=oname, user_id = session["user_id"])
            flash("Deleted.", 'danger')
        # updates
        else:
            # new values
            nname = request.form.get("item")
            nstore = request.form.get("store")
            nquan = int(request.form.get("quantity"))

            # new quantity
            quan = nquan-oquan

            if not (db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store=nstore)):
                flash("Store not found.", 'danger')

            # changes quantity
            if quan < 0:
                db.execute("DELETE FROM items WHERE store_id = :store AND item_name LIKE :item AND user_id = :user_id",
                            store=sid[0]["store_id"], item=oname, user_id = session["user_id"])
                db.execute("""INSERT INTO items (user_id, item_name, store_id, quantity) VALUES (:user_id, :item_name, :store_id, :quantity)""",
                            user_id = session["user_id"], item_name = oname, store_id = sid[0]["store_id"], quantity = nquan)
            elif quan > 0:
                db.execute("""INSERT INTO items (user_id, item_name, store_id, quantity) VALUES (:user_id, :item_name, :store_id, :quantity)""",
                            user_id = session["user_id"], item_name = oname, store_id = sid[0]["store_id"], quantity = quan)
            # changes item name
            if nname != oname:
                existname = db.execute("SELECT item_name FROM items WHERE item_name LIKE :name AND user_id = :userid", name = nname, userid = session["user_id"])
                if existname:
                    nname = existname[0]["item_name"]
                db.execute("""UPDATE items SET item_name=:new WHERE item_name = :oname AND store_id = :storeid AND user_id=:userid""",
                            new = nname, oname=oname, storeid=sid[0]["store_id"],userid=session["user_id"])
            # changes store name
            if nstore != ostore:
                db.execute("UPDATE items SET store_id = :storeid WHERE item_name=:name AND store_id=:oldid AND user_id=:userid",
                            storeid=(db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store=nstore))[0]["store_id"],
                            name=nname, oldid=sid[0]["store_id"], userid=session["user_id"])
            flash("Success!", 'success')

        stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = ostore)

        userstores = db.execute("SELECT store_id FROM items WHERE store_id LIKE :store AND user_id=:userid",
                                store=stores[0]["store_id"], userid=session["user_id"])

        if not userstores:
            flash("You do not need any items from " + ostore + " anymore!", 'danger')
            return redirect("/")

        items = db.execute('SELECT item_name, store_name, SUM(quantity) FROM items, stores, users WHERE items.store_id = stores.store_id AND stores.store_name LIKE :name AND items.user_id = users.id AND users.id = :id GROUP BY item_name',
                            id=session["user_id"], name=request.form.get("store"))

        for i in items:
            if i["item_name"].find("'") != -1:
                i["item_name"] = i["item_name"].replace("'", "\\'")

        store=items[0]["store_name"]
        if store.find("'") != -1:
            store = store.replace("'", "\\'")

        # Display portfolio
        return render_template("list.html", items=items, store=store)

@app.route("/add", methods=["POST"])
@login_required
def add():
    """Enable user to add an item to his/her shopping list."""

    # Wait for user to fill out form and submit
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("item"):
            flash("Please input an item.", 'danger')
        elif not request.form.get("store"):
            flash("Please input a store.", 'danger')

        # Check that store exists
        stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))

        if not stores:
            flash("Store was not found.", 'danger')
            return redirect("/")

        # Checks if item name AND store name already exist in user's shopping list (so that user can just add to existing row in list)
        exists = db.execute("SELECT store_name, items.store_id, item_name FROM items, stores WHERE stores.store_id = items.store_id AND items.store_id = :store AND item_name LIKE :item AND user_id = :id",
                            store=stores[0]["store_id"], item=request.form.get("item"), id=session["user_id"])

        if not exists:
            # Add item to list
            db.execute("""INSERT INTO items (user_id, item_name, store_id, quantity)
                VALUES(:user_id, :item_name, :store_id, :quantity)""",
                    user_id=session["user_id"], item_name=request.form.get("item"), store_id = stores[0]["store_id"], quantity=int(request.form.get("quantity")))

            # Display portfolio
            flash("Items added to shopping list!", 'success')
            return redirect("/")

        else:
            return render_template("add2.html", item=exists[0]["item_name"], store=exists[0]["store_name"], quantity=request.form.get("quantity"))

@app.route("/add2", methods=["POST"])
@login_required
def add2():
    # Gives user choice to add repeated items onto shopping list
    if request.method == "POST":
        if request.form["submit"] == "n":
            flash("Item not added to shopping list.", 'danger')
            return redirect("/")
        else:
            item,store,quan=(request.form["submit"]).split(",")

            quantity = int(quan)

            stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = store)

            db.execute("""INSERT INTO items (user_id, item_name, store_id, quantity)
                VALUES(:user_id, :item_name, :store_id, :quantity)""",
                    user_id=session["user_id"], item_name=item, store_id = stores[0]["store_id"], quantity=quantity)

            flash("Item Added!", 'success')
            return redirect("/")

@app.route("/add3", methods=["POST"])
@login_required
def add3():
    """Enable user to add an item to his/her shopping list."""

    # Wait for user to fill out form and submit
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("item"):
            flash("Please input an item.", 'danger')
        elif not request.form.get("store"):
            flash("Please input a store.", 'danger')

        # Check that store exists
        stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))

        if not stores:
            flash("Store was not found.", 'danger')
            return redirect("/")

        # Checks if item name AND store name already exist in user's shopping list (so that user can just add to existing row in list)
        exists = db.execute("SELECT store_name, items.store_id, item_name FROM items, stores WHERE stores.store_id = items.store_id AND items.store_id = :store AND item_name LIKE :item AND user_id = :id",
                            store=stores[0]["store_id"], item=request.form.get("item"), id=session["user_id"])

        if not exists:
            # Add item to list
            db.execute("""INSERT INTO items (user_id, item_name, store_id, quantity)
                VALUES(:user_id, :item_name, :store_id, :quantity)""",
                    user_id=session["user_id"], item_name=request.form.get("item"), store_id = stores[0]["store_id"], quantity=int(request.form.get("quantity")))

            # Display portfolio
            flash("Items added to shopping list!", 'success')
        stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))

        userstores = db.execute("SELECT store_id FROM items WHERE store_id LIKE :store AND user_id=:userid",
                                store=stores[0]["store_id"], userid=session["user_id"])

        if not userstores:
            flash("You do not need any items from this store.", 'danger')
            return render_template("shop.html")

        items = db.execute('SELECT item_name, store_name, SUM(quantity) FROM items, stores, users WHERE items.store_id = stores.store_id AND stores.store_name LIKE :name AND items.user_id = users.id AND users.id = :id GROUP BY item_name',
                            id=session["user_id"], name=request.form.get("store"))

        for i in items:
            if i["item_name"].find("'") != -1:
                i["item_name"] = i["item_name"].replace("'", "\\'")

        store=items[0]["store_name"]
        if store.find("'") != -1:
            store = store.replace("'", "\\'")

        # Display portfolio
        return render_template("list.html", items=items, store=store)


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
            flash("Incorrect username and/or password.", 'danger')
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


@app.route("/check", methods=["POST"])
@login_required
def check():
    """Check if a store exists in the current database."""

    # Prompts user to see if store of interest exists in the database
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("store"):
            flash("Must input a store.", 'danger')
            return render_template("check.html")

        # Get store id
        store = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))
        if not store:
            return render_template("newstore.html", store=request.form.get("store"))

        # Display if store exists
        flash("Store Exists!", 'success')
        return redirect("/")


@app.route("/newstore", methods=["POST"])
@login_required
def newstore():
    # Gives user choice to addnew store not in database
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

    # Generates store specific shopping list for user after inputting store name
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("store"):
            flash("Where are you shopping?", 'danger')
            return render_template("shop.html")

        stores = db.execute("SELECT store_id FROM stores WHERE store_name LIKE :store", store = request.form.get("store"))

        if not stores:
            flash("Store was not found.", 'danger')
            return render_template("shop.html")

        userstores = db.execute("SELECT store_id FROM items WHERE store_id LIKE :store AND user_id=:userid",
                                store=stores[0]["store_id"], userid=session["user_id"])

        if not userstores:
            flash("You do not need any items from this store.", 'danger')
            return render_template("shop.html")

        items = db.execute('SELECT item_name, store_name, SUM(quantity) FROM items, stores, users WHERE items.store_id = stores.store_id AND stores.store_name LIKE :name AND items.user_id = users.id AND users.id = :id GROUP BY item_name',
                            id=session["user_id"], name=request.form.get("store"))

        for i in items:
            if i["item_name"].find("'") != -1:
                i["item_name"] = i["item_name"].replace("'", "\\'")

        store=items[0]["store_name"]
        if store.find("'") != -1:
            store = store.replace("'", "\\'")

        # Display portfolio
        return render_template("list.html", items=items, store=store)

    # GET
    else:

        # Display sales form
        return render_template("shop.html")

# capitalize store names
def capitalize(store):
    return ' '.join(s[:1].upper() + s[1:] for s in store.split(' '))
if __name__ == '__main__':
 app.debug = True
 port = int(os.environ.get("PORT", 5000))
 app.run(host='0.0.0.0', port=port)