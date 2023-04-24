from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from models import User
from database import db

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":   
        return render_template("authentication/login.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        return redirect(render_template("authentication/login.html"))
        

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("authentication/register.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        rPassword = request.form['repeatPassword']

        # Check if password meets the requirements
        if len(password) < 8 or len(password) > 64:
            flash('Parolei jābūt starp 8 un 64 simboliem garai', 'error')
            return redirect(url_for("auth.register"))
        elif rPassword != password:
            flash('Paroles nesakrīt!', 'error')
            return redirect(url_for("auth.register"))

        # Create a new user instance and add it to the database
        new_user = User(
            username="username123",
            password="password123",
            name = "name123",
            surname = "surname123",
            verificationCode = "code123",
            phone = "phoneNumber123",
            createdOn=datetime.now(),
            isVerified=False,
            isDeleted=False
        )
        db.session.add(new_user)
        db.session.commit()

        # Redirect the user to the home page
        flash('Veiksmīga reģistrācija!', 'success')
        return redirect(url_for("home.index"))