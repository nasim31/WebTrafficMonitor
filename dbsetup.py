#store all interactive code in this file for modularity
import sqlite3
from sqlite3 import Error
 
def newConnection(database): #handle exceptions for creating new connection
    try:
        conn = sqlite3.connect(database, isolation_level=None, check_same_thread = False)
        conn.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        
        return conn
    except Error as e:
        print(e)
        
def newTable(c,sql): #create new sql table
    c.execute(sql)
    
def updateCreateTable(c,data): #query table for update.create using SQL commands
    sql = "SELECT * FROM pages where name=? and session=?"
    c.execute(sql,data[:-1])
    result = c.fetchone()
    if result == None:
        newPage(c,data)
    else:
        print(result)
        updatePages(c, result['id'])
 
def newPage(c, data): #input data in new page
    print(data)
    sql = ''' INSERT INTO pages(name,session,first_visited)
              VALUES (?,?,?) '''
    c.execute(sql, data)
    
def updatePages(c, pageId): #update existing pages
    print(pageId)
    sql = ''' UPDATE pages
              SET visits = visits+1 
              WHERE id = ?'''
    c.execute(sql, [pageId])
    
def newSession(c, data): # input data into new session
    sql = ''' INSERT INTO sessions(ip, continent, country, city, os, browser, session, created_at)
              VALUES (?,?,?,?,?,?,?,?) '''
    c.execute(sql, data)
    
def allSessions(c): #display all sessions
    sql = "SELECT * FROM sessions"
    c.execute(sql)
    rows = c.fetchall()
    return rows
    
def allPages(c): #all pages
    sql = "SELECT * FROM pages"
    c.execute(sql)
    rows = c.fetchall()
    return rows
    
def allUserVisits(c, session_id): #give all users
    sql = "SELECT * FROM pages where session =?"
    c.execute(sql,[session_id])
    rows = c.fetchall()
    return rows
 
def main(): #create tables using SQL commands
    database = "./pythonsqlite.db"
    sql_newPage = """ 
        CREATE TABLE IF NOT EXISTS pages (
            id integer PRIMARY KEY,
            name varchar(225) NOT NULL,
            session varchar(255) NOT NULL,
            first_visited datetime NOT NULL,
            visits integer NOT NULL Default 1
        ); 
    """
    sql_newSession = """ 
        CREATE TABLE IF NOT EXISTS sessions (
            id integer PRIMARY KEY,
            ip varchar(225) NOT NULL,
            continent varchar(225) NOT NULL, 
            country varchar(225) NOT NULL,
            city varchar(225) NOT NULL, 
            os varchar(225) NOT NULL, 
            browser varchar(225) NOT NULL, 
            session varchar(225) NOT NULL,
            created_at datetime NOT NULL,
        ); 
    """
    
    # create a database connection
    conn = newConnection(database)
    if conn is not None:
        # create tables
        newTable(conn, sql_newPage)
        newTable(conn, sql_newSession)
        print("Connection established!")
    else:
        print("Could not establish connection")
        
if __name__ == '__main__':
    main()