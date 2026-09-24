import psycopg2.extras
import bcrypt

from flask import Flask, redirect, url_for, flash, session

def get_connection():
    return psycopg2.connect(
        dbname="mymovies",
        user="postgres",
        password="covert",
        host="127.0.0.1",
        port="5432"
    )
def get_user(username,password,action):
    print(username,password,action)

    sessionid:int = 0 #session user_id
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if action == "login":
    

        #verify that the user and password match.
        sql = cur.mogrify(f"select * from users where username = %s",(username,))
        cur.execute(sql)
        rows = cur.fetchall()
        
        cur.close()
        conn.close()

        entered = password.encode("utf-8")
        if len(rows) == 1:
           dbhashed = rows[0].get("password").encode("utf-8")
        

        print("HOW MANY ROWS RETURNED FROM THE LOGIN CHECK:", len(rows),rows[0].get("username"))
        if len(rows) == 1 and bcrypt.checkpw(entered, dbhashed): #rows[0].get("password") == password:
            sessionid = rows[0].get("id")
            return sessionid,True,"User found goto dashboard."
        elif len(rows) == 1 and not bcrypt.checkpw(entered, dbhashed): #rows[0].get("password") != password:
            return sessionid,False,"Invalid password entered for this user."
        else: #no record 
            return sessionid,False,"User was not found, please retry or signup."

        
    if action == "signup":
        sql = cur.mogrify(f"select * from users where username = %s",(username,))
        cur.execute(sql)
        rows = cur.fetchall()

        #START THE STORING OF THE PWD ENCRYPTED
        sencryptpwd = password.encode("utf-8") #encrypted password
        hashed = bcrypt.hashpw(sencryptpwd,bcrypt.gensalt()) #hashed password to store
        strhash = hashed.decode("utf-8")
        #print(strhash)

        bok = False
        returnmsg = ""

        if len(rows) == 1:
            cur.close()
            conn.close()
            bok = False
            returnmsg = "User already exists, please retry."
        else:
            #create record in db
            print("create new user")
            conn = get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = cur.mogrify(f"INSERT INTO users (username,password) VALUES(%s,%s) RETURNING id",(username,strhash))

            print("THE SQL CHECK IN SIGNUP",sql)
            try:
                cur.execute(sql)
                newrow = cur.fetchone()
                new_id = newrow["id"]
                conn.commit()
                bok = True
                returnmsg = "User Created."
            except:
                bok = False
                returnmsg = "Error occurred during creation of record, please retry."
                print("Error creating new row")
            finally:
                cur.close()
                conn.close()

    return sessionid,bok,returnmsg
    