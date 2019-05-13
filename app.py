import os

from flask import Flask, render_template, request, redirect, jsonify
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_URI'] = "mongodb://127.0.0.1:27017/canary"
mongo = PyMongo(app)

@app.route('/', methods=["GET"])
@app.route('/<client>', methods=["GET"])
def home(client=None):
    return render_template("index.html", client=client)

@app.route("/", methods=["POST"])
def display_subscriber():
    client = request.form["chooseClient"]
    return render_template("index.html", client=client)

@app.route("/subscriber/<subscriber>", methods=["GET", "POST"]) 
def subscriber(subscriber):
    if request.method == 'GET':
        user =  mongo.db.users.find_one({"id":subscriber})
        print(user)
        if user == None:
            return render_template("subscriber.html")
        else:
            return render_template("subscriber.html", subscriber=user)


@app.route("/subscriber/add_subscription", methods=["POST"]) 
def add_subscription():
    client = request.form["chooseClient"]
    subscriber =  request.form["chooseSubscriber"]
    mongo.db.users.update(
        { "id": subscriber },
        { "$addToSet": { "subscriptions": client } }
    )
    return jsonify({})






@app.route("/", methods=["POST"])
def run_checks():
    return render_template("index.html")



@app.route("/", methods=["POST"])
def update_subscriber():
    return render_template("index.html")


if __name__ == "__main__":
    print("Do not run this script, directly. Use the start script, start.sh, instead.")

