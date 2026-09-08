import psycopg2.extras
from psycopg2 import errors
from services.db import get_connection  #single entry point for processing db connections

#actor.py
#PURPOSE: to perform CRUD operations on the actor table
#FUTURE: could send in the request.json directly instead of as a parameter more independent
#        could send in the username instead of the session itself
#        problem with request not coming in is verify the request.args are no longer needed
#        past this point, only username is needed from session and loggedin in order to
#        proceed further, need to check username against security to be able to add/edit/delete 
#        whatever the current record is, so sec_tables table that has the username and the
#        CRUD operations that they are allowed to manipulate or should it be from the database server
#        side? but that would be at the OS user level so probably not a good idea there unless
#        you can pass it through to the server in the connection.

def addActor(session,request):
    data = request.json
    smsg = ""
    isok = True
    sactorname = data["name"]
    ibirthyear = int(data["birthyear"])
    newid = 0
    thisrow = None

    print("DEBUG IN THE addActor FUNCTION:",sactorname,ibirthyear)

    #VERIFY DATA
    if sactorname == "" or not ibirthyear:
        isok = False
        smsg = "Actor and/or birthyear must be set."
        return {
            "msg":smsg,
            "status":isok
        }
    
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    sql = cur.mogrify(f"INSERT INTO actor (name,birthyear) VALUES(%s, %s) RETURNING *",(sactorname,ibirthyear))

    #smsg += "EARLY FALLOUT FOR DEBUG"
    #print("DEBUG: INSIDE THE API.ACTOR.ADDACTOR ROUTINE",sactorname,ibirthyear,smsg)
    #return {
    #    "status":True,
    #    "msg":smsg
    #}

    #CHECK FOR UNIQUE ERROR, OTHER DB ERRORS, FINALLY PYTHON ERRORS ROLLBACK AND ERROR MSG 
    try: 
       cur.execute(sql)
       thisrow = cur.fetchone()
       newid = thisrow["id"]
       smsg = "Actor Added Successfully."
       if conn: conn.commit()
    except psycopg2.errors.UniqueViolation as e:
        isok = False
        if conn: conn.rollback()
        smsg = f"Database Error UV: {e.pgerror}"
    except psycopg2.Error as e:
        isok = False
        if conn: conn.rollback()
        smsg = f"Database Error Default: {e}"
    except Exception as e2:
       isok = False
       smsg = f"Error during addition happened, please refresh and retry.{e2}"
       if conn: conn.rollback()
    finally:
        if cur: cur.close()
        if conn: conn.close()

    #The record was added ok
    if thisrow:
        return {
            "status":isok,
            "msg": smsg,
            "id" : newid,
            "data":thisrow
        }    
    else:
        return {
                    "status":isok,
                    "msg": smsg,
                    "id" : newid
                }    

def editActor(session,request):
    print("DEBUG: INSIDE THE API.ACTOR.EDITACTOR ROUTINE")

    data = request.json
    smsg = ""
    isok = True

    sname = data["actorname"]
    iyear = data["actoryear"]
    id = data["actorid"]

    conn = get_connection();
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    sql = cur.mogrify(f"UPDATE actor set name='{sname}', birthyear={iyear} WHERE id={id}")

    print("DEBUG SQL QUERY TO SAVE ACTOR EDIT:",sql)
    try:
       cur.execute(sql)
       conn.commit()
       smsg = "Update Successful."
       isok = True
    except psycopg2.Error as e:
        conn.rollback()
        smsg = "Error DB:" + e.pgerror
        isok = False
    except:
        conn.rollback()
        smsg = "Error happened during save."
        isok = False
    finally:
        cur.close()
        conn.close()


    return {
        "status":isok,
        "msg":smsg
    }

def deleteActor(session,request):
    print("DEBUG: INSIDE THE API.ACTOR.DELETEACTOR ROUTINE")

    data = request.json
    smsg = "" #return message
    isok = True #return did it work
    conn = get_connection();
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"DELETE FROM actor WHERE id=%s",(data["actorid"],))

    try:
        cur.execute(sql)
        conn.commit()
        print("do nothing test but return a positive to test MESSAGE")
    except:
        isok = False
        smsg = "Error During Delete"
        print("Error during delete")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    
    smsg += data["actorid"] + " was deleted. "

    #only a status and message no return data record or datarows
    return {
            "status":isok,
            "msg":smsg
        }
    