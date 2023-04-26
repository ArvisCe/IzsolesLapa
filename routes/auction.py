from flask import Blueprint, jsonify, render_template, request, redirect, flash, url_for
from datetime import datetime
from models import Listing, db, current_user
import os
import uuid

auction = Blueprint("auction", __name__, static_folder="static", template_folder="templates")

@auction.route("/piesolit/<int:id>", methods=["POST"])
def bid(id):
    listing = Listing.query.filter_by(id=id).first()
    
        
 