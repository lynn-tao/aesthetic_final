import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from statistics import mode

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///aesthetic.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def homepage():
    """Show homepage"""
    # get user's aesthetic
    aesthetic = db.execute("SELECT aesthetic FROM results WHERE username = ?", session["user_id"])
    # print(aesthetic)
    # if no user has no aesthetic, direct them to take the quiz first
    if len(aesthetic) == 0:
        return render_template("index.html")
    # else, display their aesthetic and link to other pages
    else:
        return render_template("homepage.html", aesthetic=aesthetic[0]["aesthetic"])


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    """Show Aesthetic Quiz"""
    if request.method == "GET":
        return render_template("quiz.html")
    if request.method == "POST":
        # get all answers returns
        answers = [request.form.get("q1"), request.form.get("q2"), request.form.get("q3"), request.form.get(
            "q4"), request.form.get("q5"), request.form.get("q6"), request.form.get("q7"), request.form.get("q8"), request.form.get("q10")]
        slider_val = int(request.form.get("q9"))
        # translate slider result into aesthethic category
        if 0 < slider_val <= 2:
            answers.append("GCF")
        elif 2 < slider_val <= 5:
            answers.append("WIG")
        elif 6 < slider_val <= 7:
            answers.append("VEC")
        else:
            answers.append("GKBS")
        # identify most commonly selected answer
        aesthetic_short = mode(answers)
        # get user identifying information
        first = request.form.get("first")
        last = request.form.get("last")
        handle = request.form.get("insta")
        # translate shorthand answer into full length aesthetic
        if aesthetic_short == "GKBS":
            aesthetic = "gifted kid burnout syndrome"
        elif aesthetic_short == "WIG":
            aesthetic = "wannabe indie girlie"
        elif aesthetic_short == "VEC":
            aesthetic = "victorian era child"
        elif aesthetic_short == "GCF":
            aesthetic = "gentrified cottagecore fairy"

        # update quiz result to SQL table of user aesthetics
        user_exists = db.execute("SELECT * FROM results WHERE username = ?", session["user_id"])
        # if user already took quiz, replace their previous aesthetic with new one
        if len(user_exists) != 0:
            db.execute("UPDATE results SET first = ?, last = ?, instagram = ?, aesthetic = ? WHERE username = ?",
                       first, last, handle, aesthetic, session["user_id"])
        # if first-time quiz, create new entry for user with aesthetic
        else:
            db.execute("INSERT INTO results(username, first, last, instagram, aesthetic) VALUES(?, ?, ?, ?, ?)",
                       session["user_id"], first, last, handle, aesthetic)

        # add to user's history of all quizzes
        db.execute("INSERT INTO history(username, first, last, aesthetic, date) VALUES(?, ?, ?, ?, ?)",
                   session["user_id"], first, last, aesthetic, datetime.now())

        # get user feedback
        comments = request.form.get("comments")
        # insert user feedback into SQL table
        db.execute("INSERT INTO feedback(first, last, comments) VALUES(?, ?, ?)",
                   first, last, comments)

        return render_template("quizresults.html", aesthetic=aesthetic_short)


@app.route("/shop")
@login_required
def shop():
    """Show shop"""
    # get user's aesthetic to display personalized storefront
    aesthetic = db.execute("SELECT aesthetic FROM results WHERE username = ?", session["user_id"])
    # if user has no aesthetic, redirect them to take the quiz first
    if len(aesthetic) == 0:
        return render_template("shoploading.html")
    # else, display personalized purchase suggestions
    else:
        return render_template("shop.html", aesthetic=aesthetic[0]["aesthetic"])


@app.route("/meet", methods=["GET"])
def meet():
    """Display other users"""
    # Query for all users
    users = db.execute("SELECT * FROM results ORDER BY first")
    # print(users)

    # get aesthetic to determine which users are a match
    aesthetic = db.execute("SELECT aesthetic FROM results WHERE username = ?", session["user_id"])
    # if user has no aesthetic, redirect them to take the quiz first
    if len(aesthetic) == 0:
        return render_template("shoploading.html")
    # print(aesthetic[0]["aesthetic"])

    # calculate summary statistics
    gkbs = db.execute("SELECT COUNT(*) FROM results WHERE aesthetic=?",
                      "gifted kid burnout syndrome")[0]['COUNT(*)']
    vec = db.execute("SELECT COUNT(*) FROM results WHERE aesthetic=?",
                     "victorian era child")[0]['COUNT(*)']
    wig = db.execute("SELECT COUNT(*) FROM results WHERE aesthetic=?",
                     "wannabe indie girlie")[0]['COUNT(*)']
    gcf = db.execute("SELECT COUNT(*) FROM results WHERE aesthetic=?",
                     "gentrified cottagecore fairy")[0]['COUNT(*)']
    total = gkbs + vec + wig + gcf
    stats = ["{:.2f}".format((float)(gkbs/total)* 100), "{:.2f}".format((float)(vec/total)* 100),
             "{:.2f}".format((float)(wig/total)* 100), "{:.2f}".format((float)(gcf/total)* 100), total]
    # print(stats)

    # Render all users and summary statistics page
    return render_template("meet.html", users=users, aesthetic=aesthetic[0]["aesthetic"], stats=stats)


@app.route("/music", methods=["GET"])
def music():
    """Display other users"""
    # get user's aesthetic for personalized collaborative playlist
    aesthetic = db.execute("SELECT aesthetic FROM results WHERE username = ?", session["user_id"])
    # if no user has no aesthetic, tell them to take the quiz first
    if len(aesthetic) == 0:
        return render_template("shoploading.html")
    # display personalized collaborative playlist
    else:
        return render_template("music.html", aesthetic=aesthetic[0]["aesthetic"])


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
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
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


@app.route("/history")
@login_required
def history():
    """Show homepage"""
    # display user's personal quiz history
    history = db.execute(
        "SELECT * FROM history WHERE username = ? ORDER BY date DESC", session["user_id"])
    print(history)
    # if no user has no aesthetic, tell them to take the quiz first
    if len(history) == 0:
        return render_template("shoploading.html")

    # Render history of quizzes page
    return render_template("history.html", history=history)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # error checking
    if request.method == "POST":
        # Access form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # error checking if valid input was entered
        if not username or not password or not confirmation:
            return apology("must enter username, password, and confirmation! nothing can be blank >:()")
        if password != confirmation:
            return apology("passwords must match!")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            return apology("that username already exists!")

        # Insert new user data into database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   username, generate_password_hash(password))

        # success message, let the user log in
        flash("Your registration was successful! Please log in.")

    return render_template("register.html")
