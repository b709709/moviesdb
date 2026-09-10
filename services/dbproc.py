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

def get_mymovies(session,request):
    rows = []
    userrow = None
    json = jsonify("")
    isok:bool = True
    smsg:str = ""
    searchvalue:str = ""
    username = session.get("username")
    user_id:int = 0
    
     
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"SELECT * FROM users WHERE username = %s",(username,))

    #sql = cur.mogrify(f"SELECT * FROM user_movie WHERE user_id = %s",(user_id,))

    print("DEBUG SQL QUERY FOR USER MOVIE",sql)

    try:
        cur.execute(sql)
        userrow = cur.fetchone()
        user_id = userrow["id"]
        try:
            """SELECT movie.title , movie.year 
            FROM user_movie 
            JOIN movie 
                    ON id = user_movie.movie_id 
            WHERE user_movie.user_id = 1"""

            sql = cur.mogrify(f"SELECT movie.id, movie.title, movie.year, user_movie.user_id, user_movie.movie_id FROM user_movie JOIN movie ON movie.id = user_movie.movie_id WHERE user_movie.user_id = %s",(user_id,))
            cur.execute(sql)
            rows = cur.fetchall()
        except:
            conn.rollback()
            isok = False
            smsg = "Error Ocurred while getting user collection of movies."
    except:
        conn.rollback()
        print("DEBUG: ERROR OCURRED DURING GETTING USER.")
        smsg = "Error occurred during verification of User Record"
        isok = False
    finally:
        cur.close()
        conn.close()


    return {
        "status":isok,
        "msg":smsg,
        "template":"dashboard.html",
        "data":rows
    }

def get_movies(session,request):
    
    rows = []
    json = jsonify("")
    isok:bool = True
    smsg:str = ""
    searchvalue:str = ""
    username:str = session.get("username")
    user_id:int = session.get("userid")

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
      searchvalue = request.args.get("searchInput")
    except:
      #print("No SearchInput argument was found in the list.")   
      searchvalue = ""
        
    if searchvalue == "" or not searchvalue:
       #sql = cur.mogrify(f"SELECT * from movie ORDER BY title")
        sql = cur.mogrify(f"SELECT *, EXISTS(SELECT 1 FROM user_movie um WHERE um.movie_id = movie.id AND um.user_id = %s) as user_has FROM movie",(user_id,))
    else:
       searchvalue = searchvalue.replace("*","%")
       #sql = cur.mogrify(f"SELECT * from movie WHERE title ILIKE %s ORDER BY title",(searchvalue,))
       sql = cur.mogrify(f"SELECT *, EXISTS(SELECT 1 FROM user_movie um WHERE um.movie_id = movie.id AND um.user_id = %s) as user_has FROM movie WHERE title ILIKE %s ORDER BY title",(user_id,searchvalue))

    print("DEBUG GET_MOVIES DATA",searchvalue,user_id)

    #THIS IS THE TEST QUERY TO MAKE SURE IT WILL BUILD THE HAS_USER FIELD NEED TO MERGE THIS INTO
    #THE ABOVE 2 SQL POSSIBILITIES
    sql = cur.mogrify(f"SELECT *, EXISTS(SELECT 1 FROM user_movie um WHERE um.movie_id = movie.id AND um.user_id = %s) as user_has FROM movie",(user_id,))
    print("DEBUG: TEST SQL QUERY FOR LINKED MOVIES:",sql)

    try:
        cur.execute(sql)
        rows = cur.fetchall()
        isok = True
        smsg = "Records retrieved for movie"
    except:
        isok = False
        smsg = "Error occured during retrieval of movie list."
    finally:
        cur.close()
        conn.close()

    return {
        "status":isok,
        "msg":smsg,
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


