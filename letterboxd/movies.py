import xml.etree.ElementTree as ET
import sqlite3
import re
from gjson import get_json

conn = sqlite3.connect('movies.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Directors;
DROP TABLE IF EXISTS Genres;
DROP TABLE IF EXISTS Actors;
DROP TABLE IF EXISTS Film;
DROP TABLE IF EXISTS Classification;
DROP TABLE IF EXISTS Principals;


CREATE TABLE Directors (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    director   TEXT UNIQUE
);

CREATE TABLE Actors (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    actor   TEXT UNIQUE
);

CREATE TABLE Genres (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    genre   TEXT UNIQUE
);


CREATE TABLE Film (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    director_id  INTEGER, 
    date DATE, year INTEGER, rate DECIMAL,numVotes INTEGER,
     image TEXT
);

CREATE TABLE Classification(
    genre_id INTEGER,
    film_id INTEGER,
    PRIMARY KEY(genre_id,film_id)
);

CREATE TABLE Principals(
    actor_id INTEGER,
    film_id INTEGER,
    PRIMARY KEY(actor_id,film_id)
)

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
    
    title = re.findall("{:},(.*),{:},{:}".format(date,year,url),line)[0].strip()

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
    
    cur.execute('''INSERT OR REPLACE INTO Film
        (title, director_id, year,date,rate,numVotes,image) 
        VALUES ( ?, ?, ?, ?, ?, ?,?)''', 
        ( title, director_id,year, date,rate,numVotes,image) )
    
    cur.execute('''SELECT id FROM Film WHERE title=?''',(title,) )
    film_id=cur.fetchone()[0]

    for genre_id in genres_id:
        cur.execute('''INSERT OR IGNORE INTO Classification
        (genre_id,film_id) VALUES (?,?)''',(genre_id,film_id))

    for actor_id in actors_id:
        cur.execute('''INSERT OR IGNORE INTO Principals
        (actor_id,film_id) VALUES (?,?)''',(actor_id,film_id))
        
    conn.commit()
