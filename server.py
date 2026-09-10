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
    print("DEBUG BEFORE REQUEST: Client Request endpoint",request.endpoint)

    if request.path == "/testing":
       return render_template("testing.html") 

    if request.endpoint and request.endpoint.startswith("static"):
        return
    
    allowed_routes = ["index","login", "static"]
    if "loggedin" not in session:
        if request.endpoint not in allowed_routes:
            return redirect(url_for("index"))

    #GATHER CLIENT INFORMATION:
    clientinfo = {
        "path" : request.path,
        "fullURL" : request.url,
        "endpoint" : request.endpoint,
        "method" : request.method,
        "args" : request.args,
        "form": request.form,
        "json" : request.get_json(silent=True),
        "cookies" : request.cookies,
        #"sessiondata" : dict(session),
        "headers": dict(request.headers),
        "clientip": request.remote_addr
    }
    print(clientinfo)

    print(type(clientinfo))

    is_rest = False
    is_rest = (
        request.is_json or
        request.headers.get("X-Requested-With") == "XMLHttpRequest" or
        request.accept_mimetypes['application/json'] > request.accept_mimetypes['text/html']
    )
    if is_rest:
        print("This was a rest request.")

    #CONTRACT WITH CLIENT SVC = PATH TO CODE services.dbproc
    # func = the name of the function inside services.dbproc ie get_movies
    # args = any specific request args that were additional to the func and svc names
    # standardized input params are session and request
    # standardized output params are status(bool), msg(str), template(str), data(dictRows)
    # IMPORTANT look into data being multiple datasets potentially ie data["table1"][rownum]
    svc = request.args.get("svc")
    func = request.args.get("func")

    if svc and func and not is_rest:
        module = importlib.import_module(f"{svc}")
        procresult = getattr(module,func)(session,request)
        print("results from module",procresult["status"],
          procresult["msg"],
          procresult["template"],
          type(procresult["data"])
          )
        
        if procresult["template"] or not is_rest:
            print("DEBUG: NAVIGATE TO:",procresult["template"])
            return render_template(procresult["template"],data=procresult["data"],username=session.get("username"))
        
    elif is_rest and svc and func:
        #jsondata = request.get_json()
        module = importlib.import_module(f"{svc}")
        #SESSION INFO AND REQUEST OBJECT request.json HAS THE CLIENT JSON POST INFO 
        procresult = getattr(module,func)(session,request)
        #JUST A JSON RESPONSE PERFECT
        print(procresult)
        return (procresult)
    
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
    userid:int = 0

    print("CLIENT DATA:",username,password,action)

    userid,isok,returnmessage = get_user(username,password,action)
    print("RETURN DATA FROM GET_USER",isok,returnmessage)

    if isok:
       session["userid"] = userid
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

    print("DEBUG: IN THE /DASHBOARD ROUTINE")
    url:str = "/dashboard?svc=services.dbproc&func=get_mymovies"
    return redirect(url)
    #return render_template("dashboard.html",username=username)
##################################################################

#SETUP THE PYTHON SERVER FOR LISTENING FOR WEB REQUEST ON 5001
if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001,debug=True)
