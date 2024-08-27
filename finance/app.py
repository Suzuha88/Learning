from helpers import apology, login_required, lookup, usd
from datetime import datetime
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import time
time.strftime('%Y-%m-%d %H:%M:%S')


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    try:
        stocks = db.execute(
            "SELECT stock_id, SUM(amount) AS shares FROM history WHERE user_id=? GROUP BY stock_id;", user_id)
    except:
        stocks = []
    print(stocks)

    table = []
    total = 0
    for stock in stocks:
        tmp = {}
        st = lookup(db.execute(
            "SELECT symbol FROM stocks WHERE id=?;", stock["stock_id"])[0]["symbol"])
        total += st["price"] * stock["shares"]

        tmp["symbol"] = st["symbol"]
        tmp["price"] = usd(st["price"])
        tmp["shares"] = stock["shares"]
        tmp["total"] = usd(st["price"] * stock["shares"])
        if stock["shares"]:
            table.append(tmp)
    print(table)
    cash = db.execute("SELECT cash FROM users WHERE id=?;", user_id)[0]["cash"]

    return render_template("index.html", table=table, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        try:
            shares = int(request.form.get("shares"))
        except:
            return apology("number of shares must be of type integer")
        if not symbol:
            return apology("must provide stock")
        if not shares:
            return apology("must provide the number of shares")
        if shares < 1:
            return apology("to sell shares go to /sell")
        # Buy stock logic bellow
        stock = lookup(symbol)

        if not stock:
            return apology(f"Couldn't find {symbol} stock", 400)

        symbol = stock["symbol"]
        price = stock["price"]
        user_id = session["user_id"]

        cash = db.execute("SELECT cash FROM users WHERE id=?;", user_id)[
            0]["cash"]
        cash -= shares * price

        if cash < 0:
            return apology("insufficent funds", 403)

        try:
            stock_id = db.execute(
                "SELECT id FROM stocks WHERE symbol=?;", symbol)[0]["id"]
        except:
            # add new stock to stock table
            stock_id = db.execute(
                "INSERT INTO stocks (symbol) VALUES(?);", symbol)

        time = datetime.now()

        db.execute("INSERT INTO history (user_id, stock_id, amount, timestamp, price) VALUES (?, ?, ?, ?, ?);",
                   user_id, stock_id, shares, time, price)  # remember action
        db.execute("UPDATE users SET cash=? WHERE id=?;",
                   cash, user_id)  # update user's cash

        return redirect('/')

    else:
        return render_template("buy.html")
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute(
        "SELECT symbol, amount, price, timestamp FROM history JOIN stocks on history.stock_id=stocks.id WHERE user_id=?;", session["user_id"])
    print(transactions)
    for transaction in transactions:
        transaction["price"] = usd(transaction["price"])
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?;", request.form.get(
                "username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("please enter symbol of the stock", 400)
        else:
            stock = lookup(symbol)
            if stock:
                return render_template("quoted.html", symbol=stock["symbol"], price=usd(stock["price"]))
            else:
                return apology("couldn't get the price", 400)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)
        # Ensure confirmation of the password was submitted
        elif not confirmation:
            return apology("must confirm password", 400)
        # Ensure passwords match
        elif not confirmation == password:
            return apology("passwords don't match", 400)

        try:
            hash = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?);", username, hash)
            id = db.execute(
                "SELECT id FROM users WHERE ? = username AND hash = ?;", username, hash)[0]["id"]
            # Remember which user has logged in
            session["user_id"] = id

            return redirect("/")
        except ValueError:
            return apology("user with this username already exists", 400)

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user_id = session["user_id"]
    """Sell shares of stock"""
    if request.method == "POST":
        shares = int(request.form.get("shares"))
        symbol = request.form.get("symbol")
        # check if values weren't provided
        if not symbol:
            return apology("")
        elif not shares:
            return apology("")

        stock = lookup(symbol)
        # check if stock is real
        if not stock:
            return apology("")

        # find stock in database
        stock_id = db.execute(
            "SELECT id FROM stocks WHERE symbol=?;", symbol)[0]["id"]
        if not stock_id:
            return apology("you didn't buy this stock")

        # check how many shares of this stock user owns
        user_stock = db.execute(
            "SELECT SUM(amount) AS shares FROM history WHERE user_id=? AND stock_id=? GROUP BY stock_id;", user_id, stock_id)
        if not user_stock:
            return apology("you didn't buy this stock")
        elif user_stock[0]["shares"] < shares:
            return apology("you don't have this amount of this stock")

        # get user's cash from database
        cash = db.execute("SELECT cash FROM users WHERE id=?", user_id)[
            0]["cash"]
        cash += stock["price"] * shares

        time = datetime.now()

        db.execute("INSERT INTO history (user_id, stock_id, amount, timestamp, price) VALUES (?, ?, ?, ?, ?);",
                   # remember action
                   user_id, stock_id, -shares, time, stock["price"])
        db.execute("UPDATE users SET cash=? WHERE id=?;",
                   cash, user_id)  # update user's cash

        return redirect("/")
    else:
        stocks = db.execute(
            "SELECT symbol, SUM(amount) as shares FROM (stocks JOIN history ON stocks.id=history.stock_id) WHERE user_id=? GROUP BY stock_id;", user_id)
        print(stocks)
        return render_template("sell.html", stocks=stocks)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        user_id = session["user_id"]
        # Check inputs
        old = request.form.get("old_password")
        new = request.form.get("new_password")
        confirmation = request.form.get("confirmation")
        if not old or not new or not confirmation:
            return apology("fill out all boxes", 403)
        elif new != confirmation:
            return apology("new passwords don't match")
        hash = db.execute("SELECT hash FROM users WHERE id=?;", user_id)[
            0]["hash"]
        if not check_password_hash(hash, old):
            return apology("wrong password")
        new_hash = generate_password_hash(new)

        db.execute("UPDATE users SET hash=? WHERE id=?", new_hash, user_id)

        return redirect("/")
    else:
        return render_template("change_password.html")
