import sqlite3
import re
from gjson import get_json

conn = sqlite3.connect('letter.sql')
cur = conn.cursor()

cur.executescript('''

CREATE TABLE IF NOT EXISTS Directors (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    director   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Actors (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    actor   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Genres (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    genre   TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS Film (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    director_id  INTEGER, 
    date DATE, year INTEGER, rate DECIMAL,numVotes INTEGER,
     image TEXT,country_id
);

CREATE TABLE IF NOT EXISTS Classification(
    genre_id INTEGER,
    film_id INTEGER,
    PRIMARY KEY(genre_id,film_id)
);

CREATE TABLE IF NOT EXISTS Principals(
    actor_id INTEGER,
    film_id INTEGER,
    PRIMARY KEY(actor_id,film_id)
);

CREATE TABLE IF NOT EXISTS Countries (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    Country   TEXT UNIQUE
);

''')


fname = input('Enter file name: ')
if ( len(fname) < 1 ) : fname = './data/watched.csv'

datafile=open(fname,"r")
#Date,Name,Year,Letterboxd URI
#2020-10-22,The Accidental Tourist,1988,https://boxd.it/1jYg

for line in datafile:
    data=line.split(",")

    #data of csv
    date = data[0]
    year=data[-2]
    
    if date=="Date": 
        continue
    
    #url of film (important for get the json)
    
    url=data[-1]

    title = re.findall("{:},(.*),{:},{:}".format(date,year,url),line)[0].strip()
    cur.execute("SELECT id FROM Film WHERE title= ?",(title,))
    try:
        data=cur.fetchone()[0]
        continue
    except:
        pass
    
    js=get_json(url)
    actors=list()
    genres=list()
    try:
        director=js["director"][0]["name"]
 
        for actor in js["actors"]:
            actors.append(actor["name"])

        for genre in js["genre"]:
            genres.append(genre)
    except:
        continue
    
    rate=js["aggregateRating"]["ratingValue"]
    numVotes=js["aggregateRating"]["ratingCount"]

    try:
        image=js["image"]
    except:
        image=None
    
    #title
    


    print(date, title, year, director,actors[0],genres[0],rate,numVotes)

    cur.execute('''INSERT OR IGNORE INTO Directors (director) 
        VALUES ( ? )''', ( director, ) )
    cur.execute('SELECT id FROM Directors WHERE director = ? ', (director, ))
    director_id = cur.fetchone()[0]

    genres_id=list()
    for genre in genres:
        cur.execute('''INSERT OR IGNORE INTO Genres (genre) 
        VALUES ( ? )''', ( genre, ) )
        cur.execute('SELECT id FROM Genres WHERE genre = ? ', (genre, ))
        genres_id.append( cur.fetchone()[0])

        actors_id=list()
    for actor in actors:
        cur.execute('''INSERT OR IGNORE INTO Actors (actor) 
        VALUES ( ? )''', ( actor, ) )
        cur.execute('SELECT id FROM Actors WHERE actor = ? ', (actor, ))
        actors_id.append(cur.fetchone()[0])
        
    try:
        country=js["countryOfOrigin"][0]["name"]
    except:
        country="Unspecified"
    cur.execute('''INSERT OR IGNORE INTO Countries (Country) 
    VALUES ( ? )''', ( country, ) )
    cur.execute('SELECT id FROM Countries WHERE Country = ? ', (country, ))
        
    country_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR REPLACE INTO Film
        (title, director_id, year,date,rate,numVotes,image,country_id) 
        VALUES ( ?, ?, ?, ?, ?, ?,?,?)''', 
        ( title, director_id,year, date,rate,numVotes,image,country_id) )
    
    cur.execute('''SELECT id FROM Film WHERE title=?''',(title,) )
    film_id=cur.fetchone()[0]

    for genre_id in genres_id:
        cur.execute('''INSERT OR IGNORE INTO Classification
        (genre_id,film_id) VALUES (?,?)''',(genre_id,film_id))

    for actor_id in actors_id:
        cur.execute('''INSERT OR IGNORE INTO Principals
        (actor_id,film_id) VALUES (?,?)''',(actor_id,film_id))
        
    conn.commit()
