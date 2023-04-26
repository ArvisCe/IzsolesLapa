from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from models import User, db, current_user, UserMixin, login_user, LoginManager, login_required, logout_user, current_user, bcrypt, session
import random

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":   
        return render_template("authentication/login.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if "@" in username:
            user = User.query.filter_by(email=username).first()
        else:
            user = User.query.filter_by(username=username).first()
        if not user:
            flash('Nepareizi ievadīts lietotājvārds vai parole!','error')
            return redirect(url_for("auth.login"))
        if not bcrypt.check_password_hash(user.password, password):
            flash('Nepareizi ievadīta parole!', 'error')
            return redirect(url_for("auth.login"))
        else:
            flash('Veiksmīgi esi ticis kontā!','success')
            session.permanent = True
            session["user"] = user.username
            login_user(user)  
            return redirect(url_for("home.index"))           

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template("authentication/register.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        rPassword = request.form['repeatPassword']
        name = request.form['name']
        surname = request.form['surname']
        phone = request.form['phone']
        
        # Check if password meets the requirements
        Errors = 0
        if len(password) < 8 or len(password) > 64:
            flash('Parolei jābūt starp 8 un 64 simboliem garai', 'error')
            return redirect(url_for("auth.register"))
        elif rPassword != password:
            flash('Paroles nesakrīt!', 'error')
            Errors += 1
        elif User.query.filter_by(username=username).first():
            flash('Lietotājs ar šādu lietotājvārdu jau eksistē!','error')
            Errors += 1
        elif User.query.filter_by(phone=phone).first():
            flash('Lietotājs ar šādu telefona numuru jau ir reģistrēts! '+phone, 'error')
            Errors += 1
        if Errors > 0:
            return redirect(url_for("auth.register"))

        # Create a new user instance and add it to the database
        new_user = User(
            username = username,
            password = bcrypt.generate_password_hash(password),
            name = name,
            surname = surname,
            verificationCode = generatePhoneVerification(),
            phone = phone,
            createdOn = datetime.now(),
            isVerified = False,
            isDeleted = False,
            isAdmin = False,
            balance=0.00,
        )
        db.session.add(new_user)
        db.session.commit()
        session.permanent = True
        session["user"] = new_user.username
        login_user(new_user)

        # Redirect the user to the home page
        flash('Veiksmīga reģistrācija!', 'success')
        return redirect(url_for("home.index"))

@auth.route("/logout")
def logout():
    logout_user()
    flash('Veiksmīgi esi izgājis!','success')
    return redirect(url_for("auth.login"))

@auth.route("/code")
def checkCode():
    return "<h1>"+generatePhoneVerification()+"</h1>"

def generatePhoneVerification():
  code = ""
  for i in range(4):
      for j in range(5):
          if random.randint(0,1) == 1:
              randomSymbol = random.randint(65,90)
              code += chr(randomSymbol)
          else:
              randomSymbol = random.randint(97, 122)
              code += chr(randomSymbol)            
      if not i == 3:
          code += "-"
  CodeAlreadyExists = User.query.filter_by(verificationCode=code).first()
  if CodeAlreadyExists:
    code = generatePhoneVerification()
  return code    
