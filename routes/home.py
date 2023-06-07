from flask import Blueprint, render_template
from flask_login import current_user
from models import Listing, pytz
import math
home = Blueprint("home", __name__, static_folder="static", template_folder="templates")




@home.route("/home")
@home.route("/")
@home.route("/izsoles/<int:page>")
def index(page=1):
    page -= 1
    return render_template('home.html', 
                           listings=Listing.query.filter(Listing.auctionStatus.notin_([3])).order_by(Listing.auctionTime.asc()).offset(page*6).limit(6).all(),
                           page=page,
                           pageAmount=math.ceil(Listing.query.filter(Listing.auctionStatus.notin_([3])).count()/6)+1,
                           )

@home.route("/noteikumi")
def rules():
    return render_template('rules.html')