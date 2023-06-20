from flask import Blueprint, render_template, request, redirect, flash, url_for
from models import db, User, LoginManager, Bcrypt, Listing, ListingTransaction, pytz, current_user

admin = Blueprint("admin", __name__, static_folder="static", template_folder="templates")


@admin.route("/panel")
def adminPanel():
    if not current_user.is_authenticated:
        flash("kur lien?",'error')
        return redirect(url_for("home.index"))
    if not current_user.isAdmin:
        flash("kur mēģini ielīst mazais? :D",'error')
        return redirect(url_for('home.index'))
    return render_template("/admin/selection.html")


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
    if User.query.filter_by(username=username).first():
        flash("Nevar 2 lietotājiem būt 1 lietotājvārds! :D","error")
        errors += 1
    
    if errors > 0:
        return redirect(url_for("admin.view_users"))
    user.username = username
    user.name = name
    db.session.commit()
    flash("veiksmīgi rediģēts lietotājs!",'success')
    return redirect(url_for("admin.view_users"))

@admin.route("/user/give_admin/<int:id>", methods=['POST'])
def giveAdmin(id):
    if not current_user.isAdmin:
        flash('parastajam mirstīgajam nav šādas tiesības..','error')
        return redirect(url_for("home.index"))
    if current_user.id == id:
        flash('nevar pats sev iedot adminu :D!','error')
        return redirect(url_for("admin.view_user",id=id))
    
    user = User.query.filter_by(id=id).first()
    user.isAdmin = True
    db.session.commit()
    message = 'veiksmīgi iedevi admina tiesības lietotājam ar id',str(id)
    flash(message,'success')
    return redirect(url_for("admin.view_user",id=id))

@admin.route("/user/take_admin/<int:id>",methods=['POST'])
def takeAdmin(id):
    if not current_user.isAdmin:
        flash('parastajam mirstīgajam nav šādas tiesības..','error')
        return redirect(url_for("home.index"))
    if current_user.id == id:
        flash('nevar pats sev noņemt adminu :D!','error')
        return redirect(url_for("admin.view_user",id=id))

    user = User.query.filter_by(id=id).first()
    user.isAdmin = False
    db.session.commit()
    message = 'veiksmīgi noņēmi admina tiesības lietotājam ar id',str(id)
    flash(message,'success')
    return redirect(url_for("admin.view_user",id=id))

@admin.route("/prece/<int:id>")
def preceAdmin(id):
    if not current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if not current_user.isAdmin:
        flash('Tikai daži izredzētie var šeit iet','error')
        return redirect(url_for('home.index'))
    
    return render_template("admin/view_listing.html")

@admin.route("/preces")
def precesAdmin():
    if not current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if not current_user.isAdmin:
        flash('Tikai daži izredzētie var šeit iet','error')
        return redirect(url_for('home.index'))
    
    return render_template("admin/view_listings.html", listings=Listing.query.filter(Listing.auctionStatus.notin_([2,3])).all())


@admin.route("/transakcijas")
def transakcijas():
    if not current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if not current_user.isAdmin:
        flash('TU NEESI DAĻA NO DIEVIEM!', 'error')
        return redirect(url_for('home.index'))
    transactions = ListingTransaction.query.filter_by(winner=True).all()
    listings = []
    for transaction in transactions:
        listings.append(Listing.query.filter_by(id=transaction.listingID).first())
    return render_template("admin/view_transactions.html", transactions = transactions, listings=listings)


@admin.route("/set_paid_statuss/<int:id>")
def transaction_paid_statuss(id):
    if not current_user.is_authenticated:
        return redirect(url_for('home.index'))
    if not current_user.isAdmin:
        flash("TEV NAV VARA ŠEIT", 'error')
        return redirect(url_for("home.index"))
    
    transaction = ListingTransaction.query.filter_by(id=id).first()
    if transaction.paid:
        transaction.paid = False
    else:
        transaction.paid = True
    db.session.commit()
    return redirect(url_for('admin.transakcijas'))