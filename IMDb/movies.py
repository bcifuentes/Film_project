import xml.etree.ElementTree as ET
import sqlite3
import re
import itertools


conn = sqlite3.connect('movies.sql')
cur = conn.cursor()

cur.executescript('''


CREATE TABLE IF NOT EXISTS Professions (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    Profession   TEXT UNIQUE 
);

CREATE TABLE IF NOT EXISTS Genres (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    Genre   TEXT UNIQUE 
);

CREATE TABLE IF NOT EXISTS Names (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE,
    profession_id INTEGER 
);

CREATE TABLE IF NOT EXISTS Film (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    len INTEGER, year INTEGER, rating DECIMAL, numVotes INTEGER
);


CREATE TABLE IF NOT EXISTS Clasification (
    genre_id  INTEGER ,
    film_id   INTEGER ,
    PRIMARY KEY(genre_id,film_id)
);

CREATE TABLE IF NOT EXISTS  Principals (
    name_id  INTEGER ,
    film_id  INTEGER ,
    PRIMARY KEY(name_id,film_id)
);

''')

fname = open("name.basics.tsv","r")
ftitle = open("title.basics.tsv","r")
frating = open("title.ratings.tsv","r")
fprincipal = open("title.principals.tsv","r")

rate=dict()

update=True
car=dict()

for line1,line2,line3 in itertools.zip_longest(ftitle,frating,fname):
    try:
        data1=line1.split("\t")
    except:
        data1=None
    try:
        data2=line2.split("\t")
    except:
        data2=None
    try:
        data3=line3.split("\t")
    except:
        data3=None
        
    try:
        tt1_i=data1.index("tconst")
        tt2_i=data2.index("tconst")

        nm1_i=data3.index("nconst")
        
        T_i=data1.index("titleType")
        t_i=data1.index("primaryTitle")
        y_i=data1.index("startYear")
        l_i=data1.index("runtimeMinutes")
        g_i=data1.index("genres\n")
        r_i=data2.index("averageRating")
        nv_i=data2.index("numVotes\n")

        n_i=data3.index("primaryName")
        p_i=data3.index("primaryProfession")
        k_i=data3.index("knownForTitles\n")
        continue
    
    except:
        pass
    

        
    if data2 is not None:
        rating_C=data2[r_i].strip()
        numVotes_C=data2[nv_i].strip()
        key2=data2[tt2_i].strip()
        rate[key2]=(rating_C,numVotes_C)

        
    if data3 is not None:

        name=data3[n_i].strip()
        
        cur.execute('''SELECT id FROM Names WHERE name=?''',(name,))
        ret=cur.fetchone()
        if ret is not None: continue
        if update==True:
            print("UPDATE")
            print("Temporales recuperados")
            update=False	
        professions=data3[p_i].split(",")
        profession=professions[0].strip()
        profession=profession.replace("_"," ")
        
        if profession=="" and len(profession)>1:    
            profession=professions[1].strip()
        elif profession=="":
            profession="Unspecified"
            
        cur.execute('''INSERT OR IGNORE INTO Professions (Profession) 
        VALUES ( ? )''', ( profession, ) )
        cur.execute('SELECT id FROM Professions WHERE Profession= ? ', (profession, ))
        profession_id=cur.fetchone()[0]

        print(name)
        cur.execute('''INSERT OR REPLACE INTO Names (name,profession_id)
        VALUES (?,?)''',(name,profession_id))
        cur.execute('SELECT id FROM Names WHERE name= ? ', (name, ))
        name_id=cur.fetchone()[0]
        
        movies=data3[k_i].split(",")
        for movie in movies:
            movie=movie.strip()
            if movie[-1]=="N":
                movie=None
            try:
                cur.execute('''INSERT OR IGNORE INTO Principals(name_id,film_id)
                VALUES (?,?)''',(name_id,car[movie]))
            except:
                cur.execute('''INSERT OR IGNORE INTO Principals(name_id,film_id)
                VALUES (?,?)''',(name_id,movie))


    if data1 is not None:
        if data1[T_i]!="movie" and data1[T_i]!="tvMovie": continue
        key1=data1[tt1_i].strip()
        
        if key1=="tt0047478":
            print("Seven Samurai")
            print(rate)
            if key1 in rate.keys():
                print("rate=",rate[key1])
            
            
        if key1 in rate.keys():
            rating=rate[key1][0]
            numVotes=rate[key1][1]
        else:
            rating=None
            numVotes=None
    
        title=data1[t_i]
        title=title.strip()
        year=data1[y_i]
        if year[-1]=="N":
            year=None
        ln =data1[l_i]
        if ln[-1]=="N":
            ln=None
    
        genres=data1[g_i].split(",")

        #print(title, year, ln,rating,numVotes)
        
        genres_id=list()
        for genre in genres:
            Genre=genre.strip()
            if Genre[-1]=="N":
                Genre="Unclassified" 
            
            cur.execute('''INSERT OR IGNORE INTO Genres (Genre) 
            VALUES ( ? )''', ( Genre, ) )
            cur.execute('SELECT id FROM Genres WHERE Genre= ? ', (Genre, ))
            genres_id.append(cur.fetchone()[0])

        cur.execute('SELECT title FROM Film WHERE title= ?',(title,))
        ver=cur.fetchone()
        if ver is not None:
            try:
                title=title+" "+year
            except:
                title=title+" "+str(data1[tt1_i])
        cur.execute('''INSERT OR REPLACE INTO Film
        (title, len ,year,rating,numVotes ) 
        VALUES ( ?, ?, ?,?,?)''', 
                (title , ln , year,rating,numVotes ) )
    
        cur.execute('SELECT id FROM Film WHERE title = ? ', (title,))
        film_id=cur.fetchone()[0]
        car[key1]=film_id

        for genre_id in genres_id:
            cur.execute('''INSERT OR IGNORE INTO Clasification 
            (genre_id,film_id) VALUES (?,?)''',(genre_id,film_id))

        cur.execute('''UPDATE Principals SET film_id= ? 
        WHERE film_id=?''',(film_id,key1))

    try:
    	conn.commit()
    except KeyboardInterrupt:
    	print("interrumpido por el usuario")
    	break
        
    
    
    
