import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import json
import sqlite3
import ssl

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def json_imdb(title):
    url="https://www.imdb.com/title/{:}/".format(title)
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html,"html.parser")
    tags = soup("script")
    for tag in tags:
        if tag.get("type",None)=="application/ld+json":
            text=tag.contents[0]
    js=json.loads(text)
    return js

conn = sqlite3.connect('movies.sql')
cur = conn.cursor()


cur.execute("SELECT MAX(id) FROM Film")
ID=int(cur.fetchone()[0])

try:
    Mfile= open("temp.txt~","r")
    M=int(Mfile.read())
    
except:
    M=0
    
for id in range(ID):
    if id < M: continue
    cur.execute("SELECT numVotes FROM Film WHERE id=?",(id,))
    N=cur.fetchone()
    if N is None:continue
    if int(N[0])<50000:continue
    cur.execute("SELECT imdb_id FROM Film WHERE id=?",(id,))
    ids=cur.fetchone()
    if ids is None: continue
    tt=ids[0]
    try:
        js=json_imdb(tt)
    except:
        mfile=open("temp.txt~","w")
        mfile.write(str(id))
        mfile.close()
        break
    try:
        imageurl=js["image"]
    except:
        imageurl=None
    try:
        director=js["director"][0]["name"]
    except:
        continue
    
    actors=list()
    try:
        for actor in js["actor"]:
            actors.append(actor["name"])
    except:
        continue
        
    print(director,"&",actors[0])
    cur.execute('''INSERT OR IGNORE INTO Directors (Director)
    VALUES (?)''',(director,))
    cur.execute("SELECT id FROM Directors WHERE Director=?",(director,))
    director_id=cur.fetchone()[0]
    
    cur.execute('''UPDATE OR IGNORE Film SET director_id=?,image=? 
    WHERE id=?''',(director_id,imageurl,id))

    actors_id=list()
    
    for actor in actors:
        cur.execute('''INSERT OR IGNORE INTO Actors (Actor)
        VALUES (?)''',(actor,))
        cur.execute("SELECT id FROM Actors WHERE Actor=?",(actor,))
        actors_id.append(cur.fetchone()[0])

    
    for name_id in actors_id:
        cur.execute('''INSERT OR IGNORE INTO Principals 
        (name_id,film_id) VALUES (?,?)''',(name_id,id))
    conn.commit()
