from flask import Blueprint, render_template,flash, url_for, redirect, request
from models import Listing, pytz, current_user, db
user = Blueprint("user", __name__, static_folder="static", template_folder="templates")

@user.route("/profils")
def profile():
    if not current_user.is_authenticated:
        flash("Tikai pieslēgti lietotāji var apskatīt savu profilu!",'error')
        return redirect(url_for("home.index"))
    ongoing = []
    for listing in Listing.query.filter_by(userID=current_user.id, auctionStatus=2).all():
        ongoing.append(listing)
    for listing in Listing.query.filter_by(userID=current_user.id, auctionStatus=1).all():
        ongoing.append(listing)
    return render_template("user/profile.html", 
                           waitingListings = Listing.query.filter_by(userID=current_user.id, auctionStatus=0).all(),
                           ongoingListings = ongoing,
                           endedListings = Listing.query.filter_by(userID=current_user.id, auctionStatus=3).all()
                           )


@user.route("/add-bank",methods=['POST'])
def addBank():
    if not current_user.is_authenticated:
        flash('pieslēdzies lai darītu šo darbību!','error')
        return redirect(url_for("auth.login"))
    
    current_user.bankAccount = request.form['bankAccount']
    current_user.bankName= request.form['bankName']
    current_user.bankSurname = request.form['bankSurname']
    db.session.commit()
    return redirect(url_for('user.profile'))