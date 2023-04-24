from flask import Blueprint, render_template, request, redirect, flash, url_for

auth = Blueprint("auth", __name__, static_folder="static", template_folder="templates")

@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == "GET":   
        return render_template("authentication/login.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        return redirect(render_template("authentication/login.html"))
        

@auth.route("/register", methods=['GET','POST'])
def register():
    if request.method == "GET":   
        return render_template("authentication/register.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        rPassword = request.form['repeatPassword']
        if rPassword !=  password:
            flash('Paroles nesakrīt!', 'error')
            return redirect(url_for("auth.register"))
        elif len(password) < 8 or len(password) > 64:
            flash('Parolei jābūt starp 8 un 64 simboliem garai', 'error')
            return redirect(url_for("auth.register"))
        else:
            flash('Veiksmīga reģistrācija!', 'success')
            return redirect(url_for("home.index"))