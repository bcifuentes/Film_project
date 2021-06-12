import sqlite3
import re
from gjson import get_json

conn = sqlite3.connect('letter.sql')
cur = conn.cursor()

cur.executescript('''

CREATE TABLE IF NOT EXISTS User (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    Name   TEXT UNIQUE,
    Username TEXT UNIQUE,
    Date DATE
);

CREATE TABLE IF NOT EXISTS Favorites (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    user_id INTEGER,
    title   TEXT UNIQUE,
    director TEXT,
    image TEXT,
    year INT,
    rate DEC,
    numVotes INT
);

''')


fname = input('Enter file name: ')
if ( len(fname) < 1 ) : fname = './data/profile.csv'

datafile=open(fname,"r")

for line in datafile:
    data=line.split(",")
    date = data[0]
    if date=="Date Joined": 
        continue
    
    favorites=re.findall('"(.*)"',line)[0].split(",")
 
    for url in favorites:
        url=url.strip()
        
    #url of film (important for get the json)
    
    name=data[2]+" "+data[3]
    username=data[1]

    cur.execute('''INSERT OR REPLACE INTO User
    (name, username, date) 
    VALUES ( ?, ?, ?)''', 
    (name,username,date) )

    cur.execute("SELECT id FROM User WHERE name=?",(name,))
    user_id=cur.fetchone()[0]

    
    for url in favorites:
        js=get_json(url)

        try:
            title=js["name"]
            year=js["releasedEvent"][0]["startDate"]
            director=js["director"][0]["name"]
          
 
        except:
            print("fallo aqui")
            continue
    
        rate=js["aggregateRating"]["ratingValue"]
        numVotes=js["aggregateRating"]["ratingCount"]

        try:
            image=js["image"]
        except:
            image=None
  
        print(username, title, year, director,rate,numVotes)

        cur.execute('''INSERT OR REPLACE INTO Favorites
        (title, director, year,rate,numVotes,image,user_id) 
        VALUES ( ?, ?, ?, ?, ?, ?,?)''', 
            ( title, director,year, rate,numVotes,image,user_id) )
    

        
    conn.commit()
