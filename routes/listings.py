from flask import jsonify, Blueprint, render_template, request, redirect, flash, url_for, make_response
from datetime import timedelta, datetime
from models import Listing, db, current_user, ListingTransaction, pytz, User
import os
import uuid
from reportlab.pdfgen import canvas
import random

listing = Blueprint("listing", __name__, static_folder="static", template_folder="templates")

@listing.route("/jauna", methods=["GET","POST"])
def new():
    if not current_user.is_authenticated:
        flash('Lai ievietotu preci vajag reģistrēties!','error')
        return redirect(url_for("auth.register"))
    if not current_user.isVerified:
        flash("Lai ievietotu preci vajag apstiprināt verifikācijas kodu telefonā!",'error')
        return redirect(url_for("user.profile"))
    if request.method == "GET":
        return render_template("listings/new.html")
        
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    priceIncrease = request.form['priceIncrease']
    auctionTime = request.form['auctionTime']
    image = request.files['image']
    errors = 0
    if image:
        image = request.files['image']
        # generate a unique ID for the image filename
        image_id = str(uuid.uuid4())

        # get the file extension from the original filename
        ext = os.path.splitext(image.filename)[1]

        # construct the new filename using the image ID and extension
        new_filename = image_id + ext
        extension = new_filename.split(".")[1]
        if not extension in ["png","jpeg","jpg",""]:
            flash("bildei jābūt png vai jpeg formātā",'error')
            print(extension)
            errors += 1
        # save the image in the static folder with the new filename
        image.save(os.path.join('static', 'images', new_filename))
        imageLocation = "/static/images/" + new_filename
    else:
        imageLocation = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/No-Image-Placeholder.svg/1665px-No-Image-Placeholder.svg.png"

    if not isinstance(price, str):
        flash("Nemaini datu tipus, dauni!",'error')
        errors += 1
    if not isinstance(priceIncrease, str):
        flash("Nemaini datu tipus, dauni!",'error')
        errors += 1
    if len(name) < 5 or len(name) > 48:
        errors += 1
        flash('Nosaukumam jābūt starp 5 un 48 simboliem!','error')
    if float(price) < 0.01 or float(price) > 100000:
        errors += 1
        flash('Cenai jābūt starp 0.01 EUR un 100,000 EUR','error')
    if float(price) < 0.01 or float(priceIncrease) > 100:
        errors += 1
        flash('Cenas jābūt starp 0.01 EUR un 100 EUR','error')
    if len(description) > 1024:
        errors += 1
        flash('Apraksts nedrīkst pārsniegt 1024 simbolus!', 'error') 
    latvia_timezone = pytz.timezone('Europe/Riga')
    current_time = datetime.now(latvia_timezone)

    try:
        auctionTime = datetime.strptime(request.form['auctionTime'], '%Y-%m-%dT%H:%M')
        if auctionTime.replace(tzinfo=None) - current_time.replace(tzinfo=None) < timedelta(days=0):
            flash('Izsole nedrīkst notikt ātrāk par 24 stundām nākotnē!','error')
            errors += 1
    except ValueError:
        flash("Tu nedrīksti vienkārši rakstīt ko tu gribi datetime. ip grabbed.",'error')
        errors += 1
        

        
    if errors > 0:
        return redirect(url_for('listing.new'))
    new_listing = Listing(
        name = name,
        description = description,
        startPrice = price,
        priceIncrease = priceIncrease,
        price = price,
        auctionTime = auctionTime,
        image=imageLocation,
        auctionStatus = 0,
        userID = current_user.id,
        creationDate = current_time,
    )
    db.session.add(new_listing)
    db.session.commit()
    flash('veiksmīgi ievietota prece!','success')
    return redirect(url_for('home.index'))

@listing.route("/rediget/<id>", methods=["GET","POST"])
def edit(id):
    listing = Listing.query.filter_by(id=id).first()
    if not current_user != listing.userID and current_user.isAdmin == False:
        return redirect(url_for("home.index")) 
    if request.method == "GET":
        return render_template("listings/edit.html", listing=listing)

    name = request.form['name']
    description = request.form['description']
    image = request.files['image']
    if image:
        image = request.files['image']
        image_id = str(uuid.uuid4())
        ext = os.path.splitext(image.filename)[1]
        new_filename = image_id + ext
        image.save(os.path.join('static', 'images', new_filename))
        imageLocation = "static/images/" + new_filename
        listing.image = imageLocation
    errors = 0
    if 5 > len(name) < 64:
        errors += 1
        flash('Nosaukumam jābūt starp 8 un 64 simboliem!','error')

    if len(description) > 1024:
        errors += 1
        flash('apraksts nedrīkst pārsniegt 1024 simbolus!', 'error') 

    if errors > 0:
        return redirect(url_for('listing.new'))

    listing.name = name
    listing.description = description
    db.session.commit()
    flash('veiksmīgi nomainīta preces informācija','success')
    return redirect(url_for("home.index"))
    



@listing.route("/apskatit/<int:id>")
def view(id):
    listing = Listing.query.filter_by(id=id).first()
    if listing:
        return render_template("listings/view.html", listing = listing)
    else:
        return render_template("pages/404.html")

@listing.route("/apskatit")
def view_none():
    return redirect(url_for("home.index"))


@listing.route("/dzest/<int:id>")
def dzest(id):
    listing = Listing.query.filter_by(id=id).first()
    if not current_user.id == listing.userID and not current_user.isAdmin:
        flash('Tev nav peieja izdzēst šo preci!', 'error')
        return redirect(url_for("home.index"))
    db.session.delete(listing)
    db.session.commit()
    flash('veiksmīgi izdzēsta prece!','success')
    return redirect(url_for("home.index"))


@listing.route("/pievienoties/<int:id>")
def join(id):
    if not current_user.is_authenticated:
        flash('Lai pievienotos izsolei vajag reģistrēties!','error')
        return redirect(url_for("auth.register"))
    if not current_user.isVerified:
        flash("Lai pievienotos izsolei vajag apstiprināt verifikācijas kodu telefonā!",'error')
        return redirect(url_for("user.profile"))
    listing = Listing.query.filter_by(id=id).first()
    if listing.auctionStatus != 1:
        flash('Izsolei vairs nevar pievienoties!','error')
        return redirect("/prece/apskatit/"+str(listing.id))
    if listing.userID == current_user.id:
        flash('Savai izsolei nevar pievienoties!','error')
        return redirect("/prece/apskatit/"+str(listing.id))
    if ListingTransaction.query.filter_by(buyerID=current_user.id,listingID=listing.id).first():
        return redirect(url_for("listing.myHistory",id=id))
    if not current_user.is_authenticated:
        flash('lai pievienotos izsolei jābūt reģistrētam lietotājam!','error')
    else:
        latvia_timezone = pytz.timezone('Europe/Riga')
        current_time = datetime.now(latvia_timezone)
        newTransaction = ListingTransaction(
            price = listing.price,
            participating = True,
            buyerID = current_user.id,
            listingID = id,
            date = current_time,
            winner = False,
            paid = False,
            listingShaked = False,
            buyerShaked = False,
            cancelled = False,
        )
        db.session.add(newTransaction)
        db.session.commit()
        flash('veiksmīgi pievienojies izsolei!','success')
        return redirect(url_for("listing.myHistory",id=id))

@listing.route("/iziet/<int:id>")
def exit(id):
    userTransaction = ListingTransaction.query.filter_by(buyerID=current_user.id, listingID=id).first()
    if not userTransaction:
        return redirect(url_for("home.index"))
    db.session.delete(userTransaction)
    db.session.commit()
    flash("veiksmīgi esi izstājies no izsoles!","success")
    return redirect(url_for("listing.myHistory"))

@listing.route("/piesolit/<int:id>")
def bet(id):
    listing = Listing.query.filter_by(id=id).first()
    userTransaction = ListingTransaction.query.filter_by(buyerID=current_user.id, listingID=id).first()
    if not userTransaction:
        return redirect(url_for("home.index"))     
    else:
        latvia_timezone = pytz.timezone('Europe/Riga')
        current_time = datetime.now(latvia_timezone)

        userTransaction.participating = False
        userTransaction.price = listing.price
        userTransaction.date = current_time    
        db.session.commit()
    transaction = ListingTransaction.query.filter_by(listingID=listing.id, participating=True).first()
    if not transaction:
        userTransaction.winner  = True
        userTransaction.price = round(int(userTransaction.price), 2)
        db.session.commit()
    flash("veiksmīgi esi piesolījis izsolei!","success")
    return redirect(url_for("listing.myHistory"))
@listing.route("/izsole/<int:id>")
def auction(id):
    listing = Listing.query.filter_by(id=id).first()
    userTransactions = ListingTransaction.query.filter_by(buyerID=current_user.id).all()
    joinedAuction = False
    for userTransaction in userTransactions:
        if userTransaction.listingID == id:
            joinedAuction = True

    if not joinedAuction:
        if listing.auctionStatus == 1:
            return redirect("/prece/pievienoties/"+id)
        else:
            flash("izsolei vairs nevar pievienoties!","error")
            return redirect(url_for("home.index"))
    
    return redirect(url_for("listing.participatingIn"))


@listing.route("/vesture")
def myHistory():
    if not current_user.is_authenticated:
        flash('Reģistrējies vai pieslēdzies, lai apskatītu savu vēsturi!', 'error')
        return redirect(url_for("home.index"))
    activeListings = []
    endedListings = []
    endedTransactions = []
    endedTransactionsSeller = []
    waitingListings = []
    ids = []
    transactions = ListingTransaction.query.filter_by(buyerID=current_user.id).all()
    for transaction in transactions:
        listing = Listing.query.filter_by(id=transaction.listingID).first()
        if listing.auctionStatus == 0:
            waitingListings.append(listing)
        elif listing.auctionStatus == 1 or listing.auctionStatus == 2 and transaction.participating: 
            activeListings.append(listing)
        else:
            endedListings.append(listing)
            endedTransactionsSeller.append(User.query.filter_by(id=listing.userID).first())
            endedTransactions.append(transaction)
        for activeListing in activeListings:
            ids.append(activeListing.id)
        
    return render_template("listings/myHistory.html", 
                           activeListings = activeListings,
                           endedListings = endedListings,
                           waitingListings = waitingListings,
                           endedTransactions = endedTransactions,
                           ids = ids,
                           transSeller = endedTransactionsSeller)

@listing.route("/db/refresh/get/<int:page>", methods=["GET"])
def dbUpdate(page):
    listings = Listing.query.filter(Listing.auctionStatus.notin_([3])).order_by(Listing.auctionTime.asc()).offset(page*6).limit(10).all()
    data = []
    for listing in listings:
        data.append({
            "ident": listing.id,
            "name": listing.name,
            "description": listing.description,
            "image": listing.image,
            "auctionStatus": listing.auctionStatus,
            "price": listing.price,
            "user": listing.userID,
        })
    return jsonify(data)




@listing.route("/db/refresh/get/specific/<int:id>", methods=["GET"])
def dbUpdateSpecific(id):
    listing = Listing.query.filter_by(id=id).first()
    data = []
    data.append({
        "ident": listing.id,
        "name": listing.name,
        "description": listing.description,
        "image": listing.image,
        "auctionStatus": listing.auctionStatus,
        "price": listing.price,
        "user": listing.userID,
    })
    return jsonify(data)



@listing.route('/samaksa/<int:id>')
def generate_pdf(id):
    if not current_user.is_authenticated:
        flash('tev nav piekļuve šajai lapai!','error')
        redirect(url_for('auth.login'))
    transaction = ListingTransaction.query.filter_by(buyerID=current_user.id, listingID=id).first()
    print(transaction)
    if not transaction:
        flash('tu neesi piedalījies šādā izsolē!','error')
        return redirect(url_for('home.index'))
    if not transaction.winner:
        flash('tu šajā izsolē neuzvarēji...','error')
        return redirect(url_for('home.index'))
    random.seed(transaction.id)
    transaction.bankDescription = str(transaction.id)+"-"+str(transaction.buyerID)+"-"+str(transaction.listingID)+":"+str(random.randint(100, 99999))+"_apmaksa"
    db.session.commit()
    key_value_pairs = {
        'Cena': str(transaction.price)+" EUR",
        'Vards': current_user.name,
        'Uzvards': current_user.surname,
        'Parskaites konts': 'LV86HABA0551040037935',
        'Bankas parskaititaja vards' : 'Arvis Ceirulis',
        'Informacija detalas' : transaction.bankDescription,
    }
    item = Listing.query.filter_by(id=id).first()
    title = "Prece: "+item.name
    description = "Apraksts: "+item.description

    response = make_response(generate_pdf_document(key_value_pairs, title, description))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename='+title+'_apmaksa'+'.pdf'
    return response

def generate_pdf_document(key_value_pairs, title, description):
    pdf = canvas.Canvas('temp.pdf')



    pdf.setFont("Helvetica", 12)
    x = 50
    y = 650
    for key, value in key_value_pairs.items():
        pdf.drawString(x, y, f'{key}: {value}')
        y -= 20
    
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, title)
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 700, description)
    
    pdf.save()

    with open('temp.pdf', 'rb') as f:
        pdf_content = f.read()

    return pdf_content




@listing.route("/handshake/buyer/<int:id>")
def handshake_buyer(id):
    transaction = ListingTransaction.query.filter_by(listingID=id, buyerID = current_user.id, winner=True).first()
    if not transaction:
        flash("Tu neesi šajā izsolē piedalījies vai arī neuzvarēji..",'error')
        return redirect(url_for("home.index"))
    transaction.buyerShaked = True
    db.session.commit()
    return redirect(url_for("listing.myHistory"))
