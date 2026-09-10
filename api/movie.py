import psycopg2.extras
from psycopg2 import errors
from services.db import get_connection  #single entry point for processing db connections

def deleteLink(session,request):
    isok = False
    smsg = ""
    data = request.json
    imovieid:int = data["movieid"]
    iuserid:int = data["userid"]

    print("DEBUG: in the deleteLink function",imovieid,iuserid)

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    sql = cur.mogrify(f"DELETE FROM user_movie WHERE user_movie.user_id = %s AND user_movie.movie_id = %s",(iuserid,imovieid))

    print("DEBUG: QUERY STATEMENT",sql)
    try:
        cur.execute(sql)
        conn.commit()
        isok = True
        smsg = "Movie Successfully removed from your collection."
    except:
        conn.rollback()
        isok = False
        smsg = "Error occurred during removal of movie from your collection, please refresh and retry."
    finally:
        cur.close()
        conn.close()


    return {
        "status":isok,
        "msg":smsg
    }

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

def saveEdit(session,request):
    isok = False
    smsgs = ""
    data = request.json
    updatedrow = None

    stitle = data["title"]
    iyear = data["year"]
    id = data["id"]

    conn =get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"UPDATE movie set title='{stitle}', year={iyear} WHERE id = {id} RETURNING *")

    print("DEBUG IN MOVIE.PY UPDATE MOVIE RECORD:",sql)

    try:
        cur.execute(sql)
        conn.commit()
        updatedrow = cur.fetchone()
        isok = True
        smsgs = "Movie record successfully updated."
    except psycopg2.Error as e:
        conn.rollback()
        isok = False
        smsgs = "Error occurred during record update:" + e.pgerror
    finally:
        cur.close()
        conn.close()

    return {
        "status":isok,
        "msg":smsgs,
        "data":updatedrow
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

def batchLoad(session,request):
    print("DOING A MASSIVE LOAD")
    isok:bool = False
    smsgs:str = ""
    #title:str, year:int, studio:int
    movies = [
               
               ("Step Brothers",2008,1)
              
              ]

    #isok = True
    #smsgs = "This was a fake batch load to get the async right."
    #return {
    #    "success":isok,
    #    "msg":smsgs
    #}

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    #use the %s the execute will take the ,movie as the data row of elements
    #make sure the order of the data in the file MATCH the order of the insert 
    #statement so in this case title, year and studio_id in that order.
    i:int = 0
    for movie in movies:

        try:
            sql = """
                 INSERT INTO movie (title,year,studio_id)
                 VALUES (%s,%s,%s)
                 """
            cur.execute(sql,movie)
            conn.commit() 
        except Exception as e:
            i = i + 1
            conn.rollback()
            print("Bad Row:",movie,e)

    cur.close()
    conn.close()
    isok = True
    smsgs = "Batch Load Complete: Error Count: " + str(i)

    return {
        "success":isok,
        "msg":smsgs
    }
    
