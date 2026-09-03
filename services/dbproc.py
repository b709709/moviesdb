from flask import Flask, render_template, request, jsonify
import psycopg2.extras

def get_connection():
    return psycopg2.connect(
        dbname="mymovies",
        user="postgres",
        password="covert",
        host="127.0.0.1",
        port="5432"
    )

def get_movies(session,request):
    print("in the dbproc.py get_movies method",session["username"],request.args)
    rows = []
    json = jsonify("")

    return {
        "status":True,
        "msg":"did get_movies in dbproc.py",
        "template":"movies.html",
        "data":rows,
        "JSON":json
    }

def get_studios(session,request):
    print("in the dbproc.py get_studios method",session["username"],request.args)
    rows = []
    json = jsonify("")

    return {
        "status":True,
        "msg":"did the get_studios in dbproc.py",
        "template":"studios.html",
        "data":rows,
        "JSON":json
    }

def get_actors(session,request):
    print ("in the dbproc.py get_actors method",session["username"], request.args)
    rows = []
    json = jsonify("")

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = f"SELECT * FROM actor ORDER BY name "
        cur.execute(sql)
        rows = cur.fetchall()
    except:
        print("Error during get actors.")
    finally:
        cur.close()
        conn.close()

    return {
        "status":True,
        "msg":"did get_actors in dbproc.py",
        "template":"actors.html",
        "data":rows,
        "JSON":json
    }


def dosomething():
    print("in the dbproc.py program")
    conn = get_connection()
    conn.close()
    return {
        "status":True,
        "msg" : "did dbproc.py",
        "template":"dashboard.html"
    }


