import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_books")
def get_books():
    books = list(mongo.db.books.find())
    return render_template("books.html", books=books)


#Register to app
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("This username already exists, please try anothe")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)


        session["user"] = request.form.get("username").lower()
        flash("Welcome to our library!")
        return redirect(url_for("mypage", username=session["user"]))
    return render_template("register.html")


# Log in
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Welcome, {}".format(
                        request.form.get("username")))
                    return redirect(url_for(
                        "mypage", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))
    return render_template("login.html")


# Users My Page
@app.route("/mypage/<username>", methods=["GET", "POST"])
def mypage(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("mypage.html", username=username)

    return redirect(url_for("login"))


# Log out of profile
@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Add New Books
@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        book = {
            "book_name": request.form.get("book_name"),
            "book_author": request.form.get("book_author"),
            "published_year": request.form.get("published_year"),
            "book_pages": request.form.get("book_pages"),
            "book_description": request.form.get("book_description"),
            "purchase_link": request.form.get("purchase_link"),
            "books_style": request.form.get("books_style"),
        }
        mongo.db.books.insert_one(book)
        flash("Book Successfully Added to Library")
        return redirect(url_for("get_books"))

    styles = mongo.db.styles.find().sort("books_style", 1)
    return render_template("add_book.html", styles=styles)


# Edit Books 
@app.route("/edit_books/<books_id>", methods=["GET", "POST"])
def edit_books(books_id):
    if request.method == "POST":
        submit = {
            "book_name": request.form.get("book_name"),
            "book_author": request.form.get("book_author"),
            "published_year": request.form.get("published_year"),
            "book_pages": request.form.get("book_pages"),
            "book_description": request.form.get("book_description"),
            "purchase_link": request.form.get("purchase_link"),
            "books_style": request.form.get("books_style"),
        }
        mongo.db.books.update({"_id": ObjectId(books_id)}, submit)
        flash("Book Successfully Updated")

    book = mongo.db.books.find_one({"_id": ObjectId(books_id)})
    styles = mongo.db.styles.find().sort("books_style", 1)
    return render_template("edit_books.html", book=book, styles=styles)


# Delete Button
@app.route("/delete_books/<books_id>")
def delete_books(books_id):
    mongo.db.books.remove({"_id": ObjectId(books_id)})
    flash("Book Succesfully Deleted")
    return redirect(url_for("get_books"))


# Wish List Page
@app.route("/wish_list/<username>", methods=["GET", "POST"])
def wish_list(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("wish_list.html", username=username)

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=False)