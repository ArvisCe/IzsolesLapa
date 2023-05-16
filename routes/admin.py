from flask import Blueprint, render_template, request, redirect, flash, url_for
from models import db, User, LoginManager, Bcrypt, Listing, ListingTransaction, pytz, current_user

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")

@admin.route("/view/users")
def view_users():
    if not current_user.isAdmin:
        flash("kur mēģini ielīst mazais? :D",'error')
        return redirect(url_for('home.index'))
    
    return render_template("/admin/view_users.html", users = User.query.all())


@admin.route("/user/delete/<int:id>",methods=["POST"])
def delete_users(id):
    if not current_user.isAdmin:
        flash("Oi oi oi... tu uzmanīgāk",'error')
        return redirect(url_for("home.index"))
    user = User.query.filter_by(id=id).first()
    if current_user == user:
        flash("Tu nevari dzēst pats sevi.. wtf vecīt? :D viss kārtībā?",'error')
        return redirect(url_for("admin.view_users"))
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for("admin.view_users"))
    
@admin.route("/view/user/<int:id>")
def view_user(id):
    if not current_user.isAdmin:
        flash("PARASTIE MIRSTĪGIE NEDRĪKST APSKATĪT",'error')
        return redirect(url_for("home.index"))
    return render_template("/admin/view_user.html", user = User.query.filter_by(id=id).first())


@admin.route("/update_user/<int:id>", methods=["POST"])
def update_user(id):
    if not current_user.isAdmin:
        flash("Tev nebūs mainīt lietotājus!",'error')
        return redirect(url_for("home.index"))
    user = User.query.filter_by(id=id).first()
    errors = 0
    username = request.form["username"]
    name = request.form["name"]
    balance = request.form["balance"]
    if User.query.filter_by(username=username).first():
        flash("Nevar 2 lietotājiem būt 1 lietotājvārds! :D","error")
        errors += 1
    
    if errors > 0:
        return redirect(url_for("admin.view_users"))
    user.username = username
    user.name = name
    user.balance = balance
    db.session.commit()
    flash("veiksmīgi rediģēts lietotājs!",'success')
    return redirect(url_for("admin.view_users"))