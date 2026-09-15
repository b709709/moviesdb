import psycopg2.extras
from psycopg2 import errors
from services.db import get_connection  #single entry point for processing db connections

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