from flask import Flask, render_template, request, jsonify
from flask import Flask, redirect, url_for, flash, session
from services.db import get_user 
import os
import importlib
##################################################################

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY","3fas35sjklaf359a0f0dsfds0f0")

#CHECK EACH REQUEST TO MAKE SURE YOU'RE LOGGED IN
@app.before_request
def require_login():
    print("Client Request endpoint",request.endpoint)

    if request.endpoint and request.endpoint.startswith("static"):
        return
    
    allowed_routes = ["index","login", "static"]
    if "loggedin" not in session:
        if request.endpoint not in allowed_routes:
            return redirect(url_for("index"))

    #CONTRACT WITH CLIENT SVC = PATH TO CODE services.dbproc
    # func = the name of the function inside services.dbproc ie get_movies
    # args = any specific request args that were additional to the func and svc names
    # standardized input params are session and request
    # standardized output params are status(bool), msg(str), template(str), data(dictRows)
    # IMPORTANT look into data being multiple datasets potentially ie data["table1"][rownum]
    svc = request.args.get("svc")
    func = request.args.get("func")

    if svc and func:
        module = importlib.import_module(f"{svc}")
        procresult = getattr(module,func)(session,request)
        print("results from module",procresult["status"],
          procresult["msg"],
          procresult["template"],
          type(procresult["data"])
          )
        
        if procresult["template"]:
            print("DEBUG: NAVIGATE TO:",procresult["template"])
            return render_template(procresult["template"],data=procresult["data"])

    #the endpoint will be services/dbjob (which is the path to the code)
    #the query params or form post data will then be sent as well as a standard format
    #the return will be the endpoint to render and the data to render in it as either json or rows not sure yet
    #the idea here is get the endpoint that will be the return render_template(endpoint)    
    #this would make the server.py program only have app.before_request and everything else in subsequent paths



#MAIN LOGIN PAGE NO PROCESSING
@app.route("/")
def index():
    return render_template("index.html")

#LOGOUT OF APPLICATION
@app.route("/logout")
def logout():
    print("logging out")
    session.clear()
    return redirect("/?loggedout=1")

#GOTO THE ACTORS DASHBOARD
#@app.route("/actors")
#def actors():
#    return render_template("actors.html")

#GOTO THE MOVIES DASHBOARD
#@app.route("/movies")
#def movies():
#    return render_template("movies.html")

#GOTO THE STUDIOS DASHBOARD
#@app.route("/studios")
#def studios():
#    return render_template("studios.html")

#ATTEMPT TO LOGIN OR SIGNUP A USER
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

#LOAD THE MAIN DASHBOARD FOR MY COLLECTION OF MOVIES
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

#SETUP THE PYTHON SERVER FOR LISTENING FOR WEB REQUEST ON 5001
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001,debug=True)
