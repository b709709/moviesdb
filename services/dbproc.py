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
   

    searchvalue = request.args.get("searchInput")

    if searchvalue:
       searchvalue = searchvalue.replace("*","%")
    else:
       searchvalue = "%"

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"SELECT * FROM users WHERE username = %s",(username,))

    #sql = cur.mogrify(f"SELECT * FROM user_movie WHERE user_id = %s",(user_id,))

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

            sql = cur.mogrify(f"SELECT movie.id, movie.title, movie.year, movie.posterimage, " + 
                                     f"user_movie.user_id, user_movie.movie_id, user_movie.dvd, user_movie.bluray, user_movie.digital, user_movie.vhs FROM user_movie " + 
                                     f" JOIN movie ON movie.id = user_movie.movie_id " + 
                                     f" WHERE user_movie.user_id = %s " + 
                                     f" AND movie.title ILIKE %s "
                                     f" ORDER BY movie.title",(user_id,searchvalue))
            print("DEBUG SQL QUERY FOR USER MOVIE",sql)
            cur.execute(sql)
            rows = cur.fetchall()
        except psycopg2.Error as e:
            conn.rollback()
            isok = False
            smsg = "Error During DB:" + e.pgerror
            print("DEBUG: DB DB DB ERROR",smsg)
        except:
            conn.rollback()
            isok = False
            smsg = "Error Ocurred while getting user collection of movies."
            print("DEBUG: ERROR OCCURED")
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
    bshow:bool = True #used to hide movies that you own

    shideOwned:str = ""
    shideOwned = request.args.get("hideOwned") 
    if shideOwned == None:
       bshow = True
    else:
       bshow = False

    print("DEBUG: services.dbproc.get_movies hide owned value:",shideOwned,bshow)

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
      searchvalue = request.args.get("searchInput")
    except:
      #print("No SearchInput argument was found in the list.")   
      searchvalue = ""

    #MERGE THIS INTO THE SELECT STATEMENT BELOW SO WE CAN PULL THE TYPES AS WELL DVD, BLURAY ETC.
    #ACTUALLY MAYBE JUST ADD AN ADDITIONAL TYPES COLUMN FOR THE MY MOVIES IN DAHSBOARD.HTML AND SHOW THE DIFFERENT ICONS FOR THE TYPES SO YOU CAN JUST CLICK THE TYPE AND
    #IT ADDS IT TO THE RIGHT HAND SIDE SO THIS WAY YOU WOULDN'T NEED THIS CHUNK IN HERE BUT THAT'S FINE NOW WE HAVE IT.
    #"""
    #SELECT
    #movie.*,
    #um.*,  -- any fields you want from user_movie
    #(um.movie_id IS NOT NULL) AS user_has
    #    FROM movie
    #    LEFT JOIN user_movie AS um
    #        ON um.movie_id = movie.id
    #    AND um.user_id = %s
    #    ORDER BY movie.title;
    #        """
        
    if searchvalue == "" or not searchvalue:
       #sql = cur.mogrify(f"SELECT * from movie ORDER BY title")
        sql = cur.mogrify(f"SELECT *, EXISTS(SELECT 1 FROM user_movie um WHERE um.movie_id = movie.id AND um.user_id = %s ) as user_has " +
                          f"FROM movie " + 
                          f" ORDER BY movie.title",(user_id,))
    else:
       searchvalue = searchvalue.replace("*","%")
       #sql = cur.mogrify(f"SELECT * from movie WHERE title ILIKE %s ORDER BY title",(searchvalue,))
       sql = cur.mogrify(f"SELECT *, EXISTS(SELECT 1 FROM user_movie um WHERE um.movie_id = movie.id AND um.user_id = %s) as user_has " + 
                         f" FROM movie WHERE title ILIKE %s ORDER BY title",(user_id,searchvalue))

    print("DEBUG GET_MOVIES DATA",searchvalue,user_id)

    #THIS IS THE TEST QUERY TO MAKE SURE IT WILL BUILD THE HAS_USER FIELD NEED TO MERGE THIS INTO
    #THE ABOVE 2 SQL POSSIBILITIES
    #sql = cur.mogrify(f"SELECT *, EXISTS(SELECT 1 FROM user_movie um WHERE um.movie_id = movie.id AND um.user_id = %s) as user_has FROM movie",(user_id,))
    #print("DEBUG: TEST SQL QUERY FOR LINKED MOVIES:",sql)

    try:
        cur.execute(sql)
        rows = cur.fetchall()

        #this will not include rows that the user has in their collection and the user doesn't want to show those
        rows = [row for row in rows if not row["user_has"] or (row["user_has"] and bshow)]
        
               
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

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"SELECT * FROM studio ORDER BY studio.name")
    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except psycopg2.Error as e:
        conn.rollback()
        smsg = "Error during fetch of studio records" + e.pgerror
    finally:
        cur.close()
        conn.close()
    
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
    searchvalue:str = ""

    try:
        searchvalue = request.args.get("searchInput")
    except:
        searchvalue = ""

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    if searchvalue == "" or not searchvalue:
        sql = cur.mogrify(f"SELECT * FROM actor ORDER BY name ")
    else:
        print("DEBUG GET ACTORS SQL:",searchvalue)
        searchvalue = searchvalue.replace("*","%")
        sql = cur.mogrify(f"SELECT * FROM actor WHERE actor.name ILIKE %s",(searchvalue,))

    
        
    try:
        #conn = get_connection()
        #cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        #sql = f"SELECT * FROM actor ORDER BY name "
        cur.execute(sql)
        rows = cur.fetchall()
    except:
        conn.rollback()
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


