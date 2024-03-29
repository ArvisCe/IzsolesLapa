from flask import Blueprint, render_template, request, redirect, flash, url_for
from datetime import datetime
from models import User, db, current_user, UserMixin, login_user, LoginManager, login_required, logout_user, current_user, bcrypt, session, pytz
import random

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":   
        return render_template("authentication/login.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            user = User.query.filter_by(username=username).first()
        else:
            user = User.query.filter_by(phone=username).first()
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
        if len(name) < 2 or len(name) > 32:
            flash('Vārdam jābūt starp 2 un 32 simboliem garam!','error')
            Errors += 1
        if len(surname) > 32:
            flash('Uzvārds var būt tikai īsāks pr 32 simboliem!','error')
            Errors += 1    
        if len(password) < 8 or len(password) > 64:
            flash('Parolei jābūt starp 8 un 64 simboliem garai', 'error')
            Errors += 1
        if rPassword != password:
            flash('Paroles nesakrīt!', 'error')
            Errors += 1
        if User.query.filter_by(username=username).first():
            flash('Lietotājs ar šādu lietotājvārdu jau eksistē!','error')
            Errors += 1
        if User.query.filter_by(phone=phone[-8:]).first():
            flash('Lietotājs ar šādu telefona numuru jau ir reģistrēts! '+phone[-8:], 'error')
            Errors += 1
        if not phone.isnumeric():
            flash('Telefona numurs nedrīkst saturēt simbolus, burtus!','error')
            Errors += 1
        if not check_phone_number(phone):
            flash('Nav ievadīts derīgs telefona numurs!','error')
            Errors += 1
        if Errors > 0:
            return redirect(url_for("auth.register"))

        # Create a new user instance and add it to the database
        latvia_timezone = pytz.timezone('Europe/Riga')
        current_time = datetime.now(latvia_timezone)
        new_user = User(
            username = username,
            password = bcrypt.generate_password_hash(password),
            name = name,
            surname = surname,
            verificationCode = generatePhoneVerification(),
            phone = phone[-8:],
            createdOn = current_time,
            isVerified = False,
            isDeleted = False,
            isAdmin = False,
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


@auth.route("/verify",methods=["POST"])
def verify():
    code = request.form['code']
    if code == current_user.verificationCode:
        current_user.isVerified = True
        db.session.commit()
        flash('veiksmīgi esi verificējies!','success')
    else:
        flash('verifikācija neizdevusies, pārbaudi verifikācijas koda pareizību','error')
    return redirect(url_for("user.profile"))


def generatePhoneVerification():
  code = ""
  for i in range(3):
      for j in range(4):
          if random.randint(0,1) == 1:
              randomSymbol = random.randint(65,90)
              code += chr(randomSymbol)
          else:
              randomSymbol = random.randint(97, 122)
              code += chr(randomSymbol)            
  CodeAlreadyExists = User.query.filter_by(verificationCode=code).first()
  if CodeAlreadyExists:
    code = generatePhoneVerification()
  return code    

def check_phone_number(number):
    if len(number) == 12 or len(number) == 11:
        number = number[-8:]
    if len(number) == 8:
        return True
    else:
        return False
