#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, make_response
from markupsafe import escape
import pymongo
import datetime
from bson.objectid import ObjectId
import os
import subprocess

# instantiate the app
app = Flask(__name__)

# load credentials and configuration options from .env file
# if you do not yet have a file named .env, make one based on the template in env.example
import credentials
config = credentials.get()

# turn on debugging if in development mode
if config['FLASK_ENV'] == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mnode

# make one persistent connection to the database
connection = pymongo.MongoClient(config['MONGO_HOST'], 27017, 
                                username=config['MONGO_USER'],
                                password=config['MONGO_PASSWORD'],
                                authSource=config['MONGO_DBNAME'])
db = connection[config['MONGO_DBNAME']] # store a reference to the database

# set up the routes

@app.route('/')
def home():
    """
    Route for the home page
    """
    return render_template('index.html')


@app.route('/bulls')
def readBulls():
    """
    Route for GET requests to the read page.
    Displays some information for the user with links to other pages.
    """
    docs = db.bulls.find({}).sort("_id", 1) # sort in ascending order of id
    return render_template('bulls.html', docs=docs) # render the read template

@app.route("/inquiryGenerate/<bullID>")
def inquiryCollect(bullID):
    doc = db.bulls.find_one({"_id": int(bullID)})
    # docAny = db.bulls.find_one({})
    # return str(doc["_id"])
    return render_template("inquiryGenerate.html", doc=doc)

@app.route("/inquiryGenerate", methods=["POST"])
def inquiryPost():
    selectedBull = request.form["userBullID"]
    bullPrice = request.form["userBullPrice"]
    name = request.form["userName"]
    email = request.form["userEmail"]
    phoneNumber = request.form["userPhoneNumber"]
    addressL1 = request.form["userAddressL1"]
    addressL2 = request.form["userAddressL2"]
    city = request.form["userCity"]
    province = request.form["userProvince"]
    country = request.form["userCountry"]
    
    doc = {
        "selectedBull": selectedBull,
        "bullPrice": bullPrice,
        "name": name,
        "email": email,
        "phoneNumber": phoneNumber,
        "addressL1": addressL1,
        "addressL2": addressL2,
        "city": city,
        "province": province,
        "country": country,
        "created_at": datetime.datetime.utcnow()
    }

    db.inquiries.insert_one(doc)

    return redirect(url_for("readBulls"))

@app.route("/inquiries")
def inquiryRead():
    docs = db.inquiries.find({}).sort("created_at", 1) # sort in ascending order of id
    return render_template('inquiryRead.html', docs=docs) # render the read template

@app.route("/inquiryEdit/<inquiryMongoID>")
def inquiryEdit(inquiryMongoID):
    doc = db.inquiries.find_one({"_id": ObjectId(inquiryMongoID)})
    return render_template('inquiryEdit.html', inquiryMongoID=inquiryMongoID, doc=doc) # render the read template

@app.route("/inquiryDelete/<inquiryMongoID>")
def inquiryDelete(inquiryMongoID):
    doc = db.inquiries.delete_one({"_id": ObjectId(inquiryMongoID)})
    return redirect(url_for("inquiryRead"))

@app.route("/inquiryEdit/<inquiryMongoID>", methods=["POST"])
def inquiryEditPost(inquiryMongoID):
    selectedBull    = request.form["userBullID"]
    bullPrice       = request.form["userBullPrice"]
    name            = request.form["userName"]
    email           = request.form["userEmail"]
    phoneNumber     = request.form["userPhoneNumber"]
    addressL1       = request.form["userAddressL1"]
    addressL2       = request.form["userAddressL2"]
    city            = request.form["userCity"]
    province        = request.form["userProvince"]
    country         = request.form["userCountry"]
    
    newVals = {
        "selectedBull": selectedBull,
        "bullPrice": bullPrice,
        "name": name,
        "email": email,
        "phoneNumber": phoneNumber,
        "addressL1": addressL1,
        "addressL2": addressL2,
        "city": city,
        "province": province,
        "country": country,
        "created_at": datetime.datetime.utcnow()
    }

    db.inquiries.update_one(
        {"_id": ObjectId(inquiryMongoID)}, # match criteria
        { "$set": newVals}
    )

    return redirect(url_for("inquiryRead"))

@app.route("/listingsManagement")
def managementPrompt():
    return render_template('management.html') # render the management template

@app.route("/newListing")
def newListing():
    return render_template("listingNew.html")

@app.route("/newListing", methods=["POST"])
def newListingPost():
    bullID = request.form["newBullID"]
    bullImageURL = request.form["newBullImageURL"]
    bullBreed = request.form["newBullBreed"]
    bullAge = request.form["newBullAge"]
    bullWeight = request.form["newBullWeight"]
    bullPrice = request.form["newBullPrice"]

    
    doc = {
        "_id": bullID,
        "imageURL": bullImageURL,
        "breed": bullBreed,
        "age": bullAge,
        "weight": bullWeight,
        "price": bullPrice,
        "created_at": datetime.datetime.utcnow()
    }

    db.bulls.insert_one(doc)

    return redirect(url_for("readBulls"))

@app.route("/listingsModify")
def listingsModify():
    docs = db.bulls.find({}).sort("_id", 1) # sort in ascending order of id
    return render_template('listingReadAndEdit.html', docs=docs) # render the read template

@app.route("/listingEdit/<int:listingMongoID>")
def listingEdit(listingMongoID):

    doc = db.bulls.find_one({"_id": int(listingMongoID)})

    return render_template('listingEdit.html', listingMongoID=listingMongoID, doc=doc) # render the edit template

@app.route("/listingEdit/<int:listingMongoID>", methods=["POST"])
def listingEditPost(listingMongoID):

    bullImageURL = request.form["newBullImageURL"]
    bullBreed = request.form["newBullBreed"]
    bullAge = request.form["newBullAge"]
    bullWeight = request.form["newBullWeight"]
    bullPrice = request.form["newBullPrice"]
    
    newVals = {
        "imageURL": bullImageURL,
        "breed": bullBreed,
        "age": bullAge,
        "weight": bullWeight,
        "price": bullPrice,
        "created_at": datetime.datetime.utcnow()
    }

    db.bulls.update_one(
        {"_id": int(listingMongoID)}, # match criteria
        { "$set": newVals}
    )

    return redirect(url_for("listingsModify"))

@app.route("/listingDelete/<int:listingMongoID>")
def listingDelete(listingMongoID):
    doc = db.bulls.delete_one({"_id": listingMongoID})
    return redirect(url_for("listingsModify"))


# @app.route('/create')
# def create():
#     """
#     Route for GET requests to the create page.
#     Displays a form users can fill out to create a new document.
#     """
#     return render_template('create.html') # render the create template


# @app.route('/create', methods=['POST'])
# def create_post():
#     """
#     Route for POST requests to the create page.
#     Accepts the form submission data for a new document and saves the document to the database.
#     """
#     name = request.form['fname']
#     message = request.form['fmessage']


#     # create a new document with the data the user entered
#     doc = {
#         "name": name,
#         "message": message, 
#         "created_at": datetime.datetime.utcnow()
#     }
#     db.exampleapp.insert_one(doc) # insert a new document

#     return redirect(url_for('read')) # tell the browser to make a request for the /read route


# @app.route('/edit/<mongoid>')
# def edit(mongoid):
#     """
#     Route for GET requests to the edit page.
#     Displays a form users can fill out to edit an existing record.
#     """
#     doc = db.exampleapp.find_one({"_id": ObjectId(mongoid)})
#     return render_template('edit.html', mongoid=mongoid, doc=doc) # render the edit template


# @app.route('/edit/<mongoid>', methods=['POST'])
# def edit_post(mongoid):
#     """
#     Route for POST requests to the edit page.
#     Accepts the form submission data for the specified document and updates the document in the database.
#     """
#     name = request.form['fname']
#     message = request.form['fmessage']

#     doc = {
#         # "_id": ObjectId(mongoid), 
#         "name": name, 
#         "message": message, 
#         "created_at": datetime.datetime.utcnow()
#     }

#     db.exampleapp.update_one(
#         {"_id": ObjectId(mongoid)}, # match criteria
#         { "$set": doc }
#     )

#     return redirect(url_for('read')) # tell the browser to make a request for the /read route


# @app.route('/delete/<mongoid>')
# def delete(mongoid):
#     """
#     Route for GET requests to the delete page.
#     Deletes the specified record from the database, and then redirects the browser to the read page.
#     """
#     db.exampleapp.delete_one({"_id": ObjectId(mongoid)})
#     return redirect(url_for('read')) # tell the web browser to make a request for the /read route.

# @app.route('/webhook', methods=['POST'])
# def webhook():
#     """
#     GitHub can be configured such that each time a push is made to a repository, GitHub will make a request to a particular web URL... this is called a webhook.
#     This function is set up such that if the /webhook route is requested, Python will execute a git pull command from the command line to update this app's codebase.
#     You will need to configure your own repository to have a webhook that requests this route in GitHub's settings.
#     Note that this webhook does do any verification that the request is coming from GitHub... this should be added in a production environment.
#     """
#     # run a git pull command
#     process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
#     pull_output = process.communicate()[0]
#     # pull_output = str(pull_output).strip() # remove whitespace
#     process = subprocess.Popen(["chmod", "a+x", "flask.cgi"], stdout=subprocess.PIPE)
#     chmod_output = process.communicate()[0]
#     # send a success response
#     response = make_response('output: {}'.format(pull_output), 200)
#     response.mimetype = "text/plain"
#     return response

# @app.errorhandler(Exception)
# def handle_error(e):
#     """
#     Output any errors - good for debugging.
#     """
#     return render_template('error.html', error=e) # render the edit template


# if __name__ == "__main__":
#     #import logging
#     #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
#     app.run(debug = True)
