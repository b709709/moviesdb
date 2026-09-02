from flask import Flask, render_template, request, jsonify
from flask import Flask, redirect, url_for, flash, session
from services.db import get_user 
import os

##################################################################

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY","3fas35sjklaf359a0f0dsfds0f0")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    action = request.form.get("action")

    print("CLIENT DATA:",username,password,action)

    isok,returnmessage = get_user(username,password,action)
    print("RETURN DATA FROM GET_USER",isok,returnmessage)

    if isok:
       session["username"] = username
       session["loggedin"] = True
       return redirect(url_for("dashboard"))
    else:
       flash(returnmessage,"error")
       return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect('/')
    if not session.get("loggedin"):
        return redirect('/')
    flash("ID:" + session.get("username"),"success")

    username = session.get("username")
    return render_template("dashboard.html",username=username)
##################################################################

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001,debug=True)
