# main entry point and contains server-side code
from flask import Flask, render_template, request, session, jsonify
import urllib.request 
from pusher import Pusher
from datetime import datetime
import httpagentparser
import json
import os
import hashlib

from dbsetup import newConnection, newSession, updateCreateTable, allSessions, allUserVisits, allPages

#import required modules and objects

app = Flask(__name__) #initialize a new flask application
app.secret_key = os.urandom(24) #generates a secret key automatically

#configure pusher object
#value of sensitive data is stored in local .bashrc file
pusher = Pusher(
app_id = os.environ.get('PUSHER_APP_ID'),
key = os.environ.get('PUSHER_APP_KEY'),
secret = os.environ.get('PUSHER_APP_SECRET'),
cluster = os.environ.get('PUSHER_APP_CLUSTER'),
ssl = True)

#define routers and their handler functions:

database = "./pythonsqlite.db"
conn = newConnection(database)
c = conn.cursor()

userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
sessionID = None

def main():
    global conn, c

def parseVisitor(data):
    updateCreateTable(c,data)
    pusher.trigger(u'pageview', u'new', { #since pusher object is instantiated, we can trigger events on whatever channels we define
        u'page' : data[0],
        u'session' : sessionID,
        u'ip' : userIP
    })

@app.before_request
def getAnalyticsData(): #this function gets visitor's IP address and retreieves data using urlib module
    global userOS, userBrowser, userIP, userContinent, userCity, userCountry, sessionID
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
    userOS = userInfo['platform']['name']
    userIP = "72.229.28.185" if request.remote_addr == '127.0.0.1' else request.remote_addr
    api = "https://www.iplocate.io/api/lookup/" + userIP

    try:
        resp = urllib.request.urlopen(api)
        result = resp.read()
        result = json.loads(result.decode("utf-8"))
        userCountry = result["country"]
        userContinent = result["continent"]
        userCity = result["city"]
    except:
        print("Could not find: ", userIP)
    getSession()

def getSession():
    global sessionID
    time = datetime.now().replace(microsecond=0)
    if 'user' not in session:
        lines = (str(time)+userIP).encode('utf-8')
        session['user'] = hashlib.md5(lines).hexdigest()
        sessionID = session['user']
        pusher.trigger(u'session', u'new', {
            u'ip': userIP,
            u'continent': userContinent,
            u'country' : userCountry,
            u'city' : userCity,
            u'os' : userOS,
            u'browser' : userBrowser,
            u'session' : sessionID,
            u'time' : str(time),
        })
        data = [userIP, userContinent, userCountry, userCity, userOS, userBrowser, sessionID, time]
        newSession(c,data)
    else:
        sessionID = session['user']

#below defined are four routes that will render web pages when visited

@app.route('/about')
def about():
    data = ['about',sessionID, str(datetime.now().replace(microsecond=0))]
    parseVisitor(data)
    return render_template('about.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/dashboard/<session_id>', methods=['GET'])
def sessionPages(session_id):
    result = allUserVisits(c,session_id)
    return render_template("dashboard-single.html",data=result)

@app.route('/get-all-sessions')
def get_all_sessions():
    data = []
    dbRows = allSessions(c)
    for row in dbRows:
        data.append({
            'ip' : row['ip'],
            'continent' : row['continent'],
            'country' : row['country'], 
            'city' : row['city'], 
            'os' : row['os'], 
            'browser' : row['browser'], 
            'session' : row['session'],
            'time' : row['created_at']
        })
    return jsonify(data)


    if __name__ == '__main__':
        main()
        app.run(debug=True)   