import xml.etree.ElementTree as ET
import sqlite3
import re
from gjson import get_json

conn = sqlite3.connect('movies.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Director;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Actor;
DROP TABLE IF EXISTS Film;


CREATE TABLE Director (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE
);

CREATE TABLE Actor (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE
);


CREATE TABLE Film (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    director_id  INTEGER, 
    genre_id INTEGER,
    actor_id INTEGER,
    date DATE, year INTEGER, rating INTEGER
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
    js=get_json(url)
    try:
        director=js["director"][0]["name"]
    except:
        continue
    try: #no todas las peliculas tienen actores
        actor=js["actors"][0]["name"]
    except:
        continue
    try:
        genre=js["genre"][0]
    
        if len(js["genre"])>1:
            genre=genre+"/"+js["genre"][1]
    except:
        continue
    rating=js["aggregateRating"]["ratingValue"]
    
    #title
    
    name = re.findall("{:},(.*),{:},{:}".format(date,year,url),line)[0]


    print(date, name, year, director,actor,genre,rating)

    cur.execute('''INSERT OR IGNORE INTO Director (name) 
        VALUES ( ? )''', ( director, ) )
    cur.execute('SELECT id FROM Director WHERE name = ? ', (director, ))
    director_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Genre (name) 
        VALUES ( ? )''', ( genre, ) )
    cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre, ))
    genre_id = cur.fetchone()[0]

    cur.execute('''INSERT OR IGNORE INTO Actor (name) 
        VALUES ( ? )''', ( actor, ) )
    cur.execute('SELECT id FROM Actor WHERE name = ? ', (actor, ))
    actor_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR REPLACE INTO Film
        (title, director_id,genre_id,actor_id, year,date,rating) 
        VALUES ( ?, ?, ?, ?, ?, ?, ?)''', 
        ( name, director_id,genre_id,actor_id, year, date,rating ) )

    conn.commit()
