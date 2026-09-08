import psycopg2.extras
from psycopg2 import errors
from services.db import get_connection  #single entry point for processing db connections

def deleteMovie(session,request):
    isok = False
    smsgs = ""
    data = request.json
    irowid = data["movieid"]
    print("DEBUG IN movie.py deleteMovie FUNCTION",irowid)
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"DELETE FROM movie WHERE id = {irowid} ")

    try:
        cur.execute(sql)
        conn.commit()
        isok = True
        smsgs = "Movie successfully deleted from the database"
    except psycopg2.Error as e:
        isok = False
        smsgs = e.pgerror
        conn.rollback()
    finally:
        cur.close()
        conn.close()
        
    return {
        "success":isok,
        "msg":smsgs
    }

def addMovie(session,request):
    isok = False
    smsg = "Test Response"
    data = request.json
    stitle = data["title"]
    iyear = int(data["year"])
    istudio = 1
    irowid = 0
    newrow = None

    conn = get_connection();
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"INSERT INTO movie (title,year,studio_id) VALUES(%s,%s,%s) RETURNING *",(stitle,iyear,istudio))
    #execute it
    #fetchone
    #obtain rowid
    #commit it
    #return new rowid
    try:
        cur.execute(sql)
        newrow = cur.fetchone()
        irowid = int(newrow["id"])
        conn.commit()
        isok = True
        smsg = "New Movie added Successfully."
    except psycopg2.Error as e:
        isok = False
        smsg = e.pgerror
    except:
        conn.rollback()
        isok = False
        smsg = "Error Occurred during the addition of this movie."
    finally:
        cur.close()
        conn.close()

    print("DEBUG: IN THE API.MOVIE addMovie FUNCTION",stitle,iyear)

    return {
        "status":isok,
        "msg":smsg,
        "rowid":irowid,
        "newrow":newrow
    }