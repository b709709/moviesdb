import psycopg2.extras
from psycopg2 import errors
from services.db import get_connection  #single entry point for processing db connections

def linkUserMovie(session,request):
    isok = False
    smsg = ""
    data = request.json
    imovieid:int = data["movieid"]
    iuserid:int = session.get("userid")

    print("DEBUG IN: linkUserMovie",imovieid,iuserid)
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = cur.mogrify(f"INSERT INTO user_movie (user_id,movie_id) VALUES(%s,%s)",(iuserid,imovieid))

    try:
        cur.execute(sql)
        conn.commit()
        isok = True
        smsg = "Successfully Added the movie to your collection"
        print("DEBUG: PASS1")
    except psycopg2.Error as e:
        conn.rollback()
        isok = False
        smsg = "Database Error:" + e.pgerror
        print("DEBUG: FAIL1",e.pgerror)
    except:
        conn.rollback()
        isok = False
        smsg = "Error Occurred During the adding of the movie, please refresh and retry."
        print("DEBUG: FAIL2",smsg)
    finally:
        cur.close()
        conn.close()

    return {
        "status":isok,
        "msg": smsg,
        "data":data
    }

def deleteLinkNoUser(session,request):
    isok = False
    smsg = ""
    data = request.json
    imovieid:int = data["movieid"]
    iuserid:int = session.get("userid")

    print("DEBUG IN: deleteLinkNoUser",imovieid,iuserid)

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    sql = cur.mogrify(f"DELETE FROM user_movie WHERE user_movie.user_id = %s AND user_movie.movie_id = %s",(iuserid,imovieid))

    try:
        cur.execute(sql)
        conn.commit()
        isok = True
        smsg = "Movie Successfully removed from collection."
    except psycopg2.Error as e:
        isok = False
        conn.rollback()
        smsg = "Error occured:" + e.pgerror
    finally:
        cur.close()
        conn.close()

    return {
        "status":isok,
        "msg":smsg,
        "data":data
    }

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
               
               
               ("About A Boy",2002,1),
               ("Analyze That",2002,1),
               ("Maid in Manhattan",2002,1),
               ("The Master of Disguise",2002,1),
               ("Mr. Deeds",2002,1),
               ("My Big Fat Greek Wedding",2002,1),
               ("National Lampoon's Van Wilder",2002,1),
               ("The New Guy",2002,1),
               ("Orange County",2002,1),
               ("Punch-Drunk Love",2002,1),
               ("Two Weeks Notice",2002,1),
               ("Agent Cody Banks",2003,1),
               ("Anger Management",2003,1),
               ("Bad Boys II",2003,1),
               ("Beethoven's 5th",2003,1),
               ("Charlie's Angels: Full Throttle",2003,1),
               ("Cheaper by the Dozen",2003,1),
               ("Daddy Day Care",2003,1),
               ("Dickie Roberts:Former Child Star",2003,1),
               ("Dumber and Dumberer:When Harry Met Lloyd",2003,1),
               ("Fake ID",2003,1),
               ("Gigli",2003,1),
               ("How to Lose a Guy in 10 Days",2003,1),
               ("The In-Laws",2003,1),
               ("Inspector Gadget 2",2003,1),
               ("Johnny English",2003,1),
               ("Legally Blonde 2: Red, White & Blonde",2003,1),
               ("Lost in Translation",2003,1),
               ("Love Actually",2003,1),
               ("National Security",2003,1),
               ("Old School",2003,1),
               ("The Rundown",2003,1),
               ("School of Rock",2003,1),
               ("Something's Gotta Give",2003,1),
               ("Uptown Girls",2003,1),
               ("50 First Dates",2003,1),
               ("Anchorman: The Legend of Ron Burgundy",2004,1),
               ("Around The World in 80 Days",2004,1),
               ("Barbershop 2: Back in Business",2004,1),
               ("Along Came Polly",2004,1),
               ("Bridget Jones: The Edge of Reason",2004,1),
               ("Christmas With The Kranks",2004,1),
               ("DodgeBall:A True Underdog Story",2004,1),
               ("The Girl Next Door",2004,1),
               ("Harold & Kumar Go To White Castle",2004,1),
               ("I Heart Huckabees",2004,1),
               ("Jersey Girl",2004,1),
               ("The Ladykillers",2004,1),
               ("Mean Girls",2004,1),
               ("Meet the Fockers",2004,1),
               ("Napoleon Dynamite",2004,1),
               ("Ocean's Twelve",2004,1),
               ("Seed of Chucky",2004,1),
               ("Shaun of the Dead",2004,1),
               ("Sideways",2004,1),
               ("Spanglish",2004,1),
               ("Starsky & Hutch",2004,1),
               ("White Chicks",2004,1),
               ("The 40-Year-Old Virgin",2005,1),
               ("Adam & Steve",2005,1),
               ("American Pie Presents: Band Camp",2005,1),
               ("Bad News Bears",2005,1),
               ("Beauty Shop",2005,1),
               ("Bewitched",2005,1),
               ("Cheaper by the Dozen 2",2005,1),
               ("Deuce Bigalow: European Gigolo",2005,1),
               ("The Dukes of Hazzard",2005,1),
               ("Fun with Dick and Jane",2005,1),
               ("Hitch",2005,1),
               ("Monster-in-Law",2005,1),
               ("Mr. & Mrs. Smith",2005,1),
               ("Waiting...",2005,1),
               ("Wedding Crashers",2005,1),
               ("Yours, Mine and Ours",2005,1),
               ("Beerfest",2006,1),
               ("The Benchwarmers",2006,1),
               ("Borat",2006,1),
               ("Clerks II",2006,1),
               ("Date Movie",2006,1),
               ("The Devil Wears Prada",2006,1),
               ("Fido",2006,1),
               ("Grandma's Boy",2006,1),
               ("The Holiday",2006,1),
               ("Larry the Cable Guy:Health Inspector",2006,1),
               ("Nacho Libre",2006,1),
               ("You, Me and Dupree",2006,1),
               ("American Pie Presents:The Naked Mile",2007,1),
               ("Are We Done Yet?",2007,1),
               ("Balls of Fury",2007,1),
               ("Blades of Glory",2007,1),
               ("Epic Movie",2007,1),
               ("Hot Fuzz",2007,1),
               ("Juno",2007,1),
               ("Knocked Up",2007,1),
               ("Mr. Bean's Holiday",2007,1),
               ("Mr. Woodcock",2007,1),
               ("No Reservations",2007,1),
               ("Ocean's Thirteen",2007,1),
               ("Smokin' Aces",2007,1),
               ("Superbad",2007,1),
               ("Be Kind Rewind",2008,1),
               ("Bedtime Stories",2008,1),
               ("Beverly Hills Chihuahua",2008,1),
               ("Disaster Movie",2008,1),
               ("Extreme Movie",2008,1),
               ("Fools' Gold",2008,1),
               ("Forgetting Sarah Marshall",2008,1),
               ("Four Christmases",2008,1),
               ("Get Smart",2008,1),
               ("Harold & Kumar Escape From Guantanamo Bay",2008,1),
               ("How to Lose Friends and Alienate People",2008,1),
               ("The Love Gugu",2008,1),
               ("Mad Money",2008,1),
               ("Marley & Me",2008,1),
               ("Meet Dave",2008,1),
               ("Pineapple Express",2008,1),
               ("Role Models",2008,1),
               ("Run, Fatboy, Run",2008,1),
               ("Semi-Pro",2008,1),
               ("Sex Drive",2008,1),
               ("Step Brothers",2008,1),
               ("Strange Wilderness",2008,1),
               ("Superhero Movie",2008,1),
               ("Tropic Thunder",2008,1),
               ("War, Inc.",2008,1),
               ("All About Steve",2009,1),
               ("American Pie Presents:The Book of Live",2009,1),
               ("Balls Out: Gary the Tennis Coach",2009,1),
               ("Bruno",2009,1),
               ("Confessions of a Shopaholic",2009,1),
               ("Couples Retreat",2009,1),
               ("Fanboys",2009,1),
               ("Gentlemen Broncos",2009,1),
               ("The Hangover",2009,1),
               ("I Love You, Man",2009,1),
               ("Inglourious Basterds",2009,1),
               ("The Invention of Lying",2009,1),
               ("The Men Who Stare at Goats",2009,1),
               ("Observe and Report",2009,1),
               ("Paul Blart: Mall Cop",2009,1),
               ("The Pink Panther 2",2009,1),
               ("The Proposal",2009,1),
               ("Zombieland",2009,1),
               ("Get Carter",2000,1),
               ("Gone in 60 Seconds",2000,1),
               ("Mission Impossible 2",2000,1),
               ("The Patriot",2000,1),
               ("Shanghai Noon",2000,1),
               ("Behind Enemy Lines",2001,1),
               ("Double Take",2001,1),
               ("The Fast and the Furious",2001,1),
               ("A Knight's Tale",2001,1),
               ("The Musketeer",2001,1),
               ("The Adventures of Pluto Nash",2002,1),
               ("Blade 2",2002,1),
               ("The Bourne Identit",2002,1),
               ("The Transporter",2002,1),
               ("2 Fast 2 Furious",2003,1),
               ("House of the Dead",2003,1),
               ("Kill Bill: Volume 1",2003,1),
               ("Once Upon a Time in Mexico",2003,1),
               ("Anacondas: The Hunt for the Blood Orchid",2004,1),
               ("Appleseed",2004,1),
               ("The Bourne Supremacy",2004,1),
               ("Catwoman",2004,1),
               ("Kill Bill:Volume 2",2004,1),
               ("The Punisher",2004,1),
               ("Divergence",2005,1),
               ("Elektra",2005,1),
               ("Sin City",2005,1),
               ("Transporter 2",2005,1),
               ("Crank",2006,1),
               ("DOA: Dead or Alive",2006,1),
               ("End Game",2006,1),
               ("Miami Vice",2006,1),
               ("Mission Impossible III",2006,1),
               ("Running Scared",2006,1),
               ("Snakes on a Plane",2006,1),
               ("The Bourne Ultimatum",2007,1),
               ("Hitman",2007,1),
               ("Postal",2007,1),
               ("Rush Hour 3",2007,1),
               ("Shoot'Em Up",2007,1),
               ("Bangkok Dangerous",2008,1),
               ("Batman: Gotham Knight",2008,1),
               ("Indiana Jones and the Kingdom of the Crystal Skull",2008,1),
               ("Max Payne",2008,1),
               ("Quantum of Solace",2008,1),
               ("Rambo",2008,1),
               ("Taken",2008,1),
               ("Transporter 3",2008,1),
               ("Wanted",2008,1),
               ("Crank: High Voltage",2009,1),
               ("Dragonball Evolution",2009,1),
               ("Fast & Furious",2009,1),
               ("Sherlock Holmes",2009,1),
               ("Solomon Kane",2009,1),
               

                




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
    
