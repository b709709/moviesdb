import psycopg2.extras
from psycopg2 import errors
from services.db import get_connection  #single entry point for processing db connections

def delStudio(session,request):
    isok:bool = False
    smsg:str = ""
    data = None
    datarow = []
    data = request.json

    studioid:int = 0
    studioid = data["studioid"]
    print("DEBUG IN delStudio:",studioid)

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    sql = cur.mogrify(f"DELETE FROM studio WHERE studio.id = %s",(studioid,))

    try:
        cur.execute(sql)
        conn.commit()
        isok = True
        smsg = "Studio successfully deleted from database"
    except psycopg2.Error as e:
        conn.rollback()
        isok = False
        smsg = "Error deleting studio: " + e.pgerror
    except:
        conn.rollback()
        isok = False
        smsg = "Error deleting record, please refresh and retry."
    finally:
        cur.close()
        conn.close()


    #test true result
    isok = True
    smsg = "Testing the true status for delete"

    return {
        "status":isok,
        "data":datarow,
        "msg":smsg
        }

def saveEdit(session,request):
    isok:bool = False
    smsg:str = ""
    datarow = []
    data = request.json

    studioid = data["studioid"]
    studioname = data["studioname"]


    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"UPDATE studio SET name = %s WHERE studio.id = %s",(studioname,studioid))

    try:
        cur.execute(sql)
        conn.commit()
        isok = True
        smsg = "Studio successfully updated."
    except psycopg2.Error as e:
        conn.rollback()
        isok = False
        smsg = "Error occurred during the update of the studio record: " + e.pgerror
    except:
        conn.rollback()
        isok = False
        smsg = "Generic update error occurred, please refresh and retry."
    finally:
        cur.close()
        conn.close()

    #print("DEBUG saveEdit studio:",studioid,studioname)
    #isok = True
    #smsg = "Test saving the edit of a studio"

    return {
        "status":isok,
        "msg":smsg,
        "data":datarow
    }

def addNew(session,request):
    isok:bool = False
    smsg:str = ""
    data = None
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    datarow = []
    studioid:int = 0
    snewstudio:str = ""
    data = request.json
    print("CLIENT DATA SENT IN:",data)

    try:
        snewstudio = data["studioname"]
    except:
        snewstudio = ""

    print("DEBUG ADD NEW STUDIO:",snewstudio)
    if snewstudio == "" or not snewstudio:
        isok = False
        smsg = "Studio Name must not be blank, please retry."
    else:
        sql = cur.mogrify(f"SELECT * FROM studio where name = %s",(snewstudio,))
        cur.execute(sql)
        datarow = cur.fetchall()

        if len(datarow) > 0:
            isok = False
            smsg = "Studio already exists, please retry."
        
        
        if len(datarow) < 0 or len(datarow) == 0:            
            try:
                sql = cur.mogrify(f"INSERT INTO studio (name) VALUES (%s) RETURNING *",(snewstudio,))
                cur.execute(sql)
                datarow = cur.fetchone()
                conn.commit()
                studioid = datarow["id"]
                isok = True
                smsg = "New Studio Created"
            except psycopg2.Error as e:
                studioid = 0
                smsg = "Error during  creation of studio record:" + e.pgerror
                datarow = []
                conn.rollback()
        else:
            cur.close()
            conn.close()

    print("DEBUG RESULTS OF ADD NEW STUDIO:",studioid)            
        
    return {
        "status":isok,
        "msg":smsg,
        "studioid":studioid,
        "data":datarow
    }