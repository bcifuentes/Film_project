import xml.etree.ElementTree as ET
import sqlite3
import re
import itertools


conn = sqlite3.connect('movies.sql')
cur = conn.cursor()
cur.executescript('''

CREATE TABLE IF NOT EXISTS Genres (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    Genre   TEXT UNIQUE 
);


CREATE TABLE IF NOT EXISTS Film (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    imdb_id TEXT UNIQUE,
    len INTEGER, year INTEGER, rating DECIMAL, numVotes INTEGER
);


CREATE TABLE IF NOT EXISTS Clasification (
    genre_id  INTEGER ,
    film_id   INTEGER ,
    PRIMARY KEY(genre_id,film_id)
);

''')

ftitle = open("title.basics.tsv","r")
frating = open("title.ratings.tsv","r")

rate=dict()

update=True
car=dict()
id=1
for line1,line2 in itertools.zip_longest(ftitle,frating):
    
    try:
        data1=line1.split("\t")
    except:
        data1=None
    try:
        data2=line2.split("\t")
    except:
        data2=None
        
    try:
        tt1_i=data1.index("tconst")
        tt2_i=data2.index("tconst")
        T_i=data1.index("titleType")
        t_i=data1.index("primaryTitle")
        y_i=data1.index("startYear")
        l_i=data1.index("runtimeMinutes")
        g_i=data1.index("genres\n")
        r_i=data2.index("averageRating")
        nv_i=data2.index("numVotes\n")

        continue
    
    except:
        pass
    

    
    if data2 is not None:
        rating_C=data2[r_i].strip()
        numVotes_C=data2[nv_i].strip()
        key2=data2[tt2_i].strip()
        rate[key2]=(rating_C,numVotes_C)

    if data1 is not None:

        
        if data1[T_i]!="movie" and data1[T_i]!="tvMovie":  
            continue
        key1=data1[tt1_i].strip()

        
        if key1 in rate.keys():
            rating=rate[key1][0]
            numVotes=rate[key1][1]
            if int(numVotes)<=200:
                continue
            
        else:
            rating=None
            numVotes=None
            continue
    
        title=data1[t_i]
        title=title.strip()
        
        year=data1[y_i]
        if year[-1]=="N":
            continue

        
        cur.execute('SELECT title FROM Film WHERE title= ?',(title,))
        ver=cur.fetchone()
        if ver is not None:
            title=title+" "+year
            
        
        ln =data1[l_i]
        if ln[-1]=="N":
            ln=None
    
        genres=data1[g_i].split(",")

        print(title, year, ln,rating,numVotes)
        
        genres_id=list()
        for genre in genres:
            Genre=genre.strip()
            if Genre[-1]=="N":
                Genre="Unclassified" 
            
            cur.execute('''INSERT OR IGNORE INTO Genres (Genre) 
            VALUES ( ? )''', ( Genre, ) )
            cur.execute('SELECT id FROM Genres WHERE Genre= ? ', (Genre, ))
            genres_id.append(cur.fetchone()[0])

 

        cur.execute('''INSERT OR REPLACE INTO Film
        (title, len ,year,rating,numVotes,imdb_id ) 
        VALUES ( ?, ?, ?,?,?,?)''', 
                (title , ln , year,rating,numVotes,key1 ) )
    
        cur.execute('SELECT id FROM Film WHERE title = ? ', (title,))
        film_id=cur.fetchone()[0]

        for genre_id in genres_id:
            cur.execute('''INSERT OR IGNORE INTO Clasification 
            (genre_id,film_id) VALUES (?,?)''',(genre_id,film_id))

    try:
        conn.commit()
    except KeyboardInterrupt:
    	print("interrumpido por el usuario")
    	break
        
    
    
    
