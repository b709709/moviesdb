import psycopg2.extras
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

    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if action == "login":
        #verify that the user and password match.
        sql = cur.mogrify(f"select * from users where username = %s",(username,))
        cur.execute(sql)
        rows = cur.fetchall()
        print("ROW COUNT FROM CURSOR",cur.rowcount)
        cur.close()
        conn.close()

        print("HOW MANY ROWS RETURNED FROM THE LOGIN CHECK:", len(rows))
        if len(rows) == 1 and rows[0].get("password") == password:
            return True,"User found goto dashboard."
        elif len(rows) == 1 and rows[0].get("password") != password:
            return False,"Invalid password entered for this user."
        else: #no record 
            return False,"User was not found, please retry or signup."

        
    if action == "signup":
        sql = cur.mogrify(f"select * from users where username = %s",(username,))
        cur.execute(sql)
        rows = cur.fetchall()

        bok = False
        returnmsg = ""

        if rows.count == 1:
            cur.close()
            conn.close()
            bok = False
            returnmsg = "User already exists, please retry."
        else:
            #create record in db
            print("create new user")
            conn = get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = cur.mogrify(f"INSERT INTO users (username,password) VALUES(%s,%s) RETURNING id",(username,password))

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

    return bok,returnmsg
    