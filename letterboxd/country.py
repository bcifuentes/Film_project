import sqlite3
import re
from gjson import get_json

conn = sqlite3.connect('letter.sql')
cur = conn.cursor()
fname = input('Enter file name: ')
if ( len(fname) < 1 ) : fname = './data/watched.csv'

datafile=open(fname,"r")
for line in datafile:
    data=line.split(",")
    date = data[0]
    year=data[-2]
    if date=="Date": 
        continue
    
    url=data[-1]
    js=get_json(url)
  
    
    title = re.findall("{:},(.*),{:},{:}".format(date,year,url),line)[0].strip()
    try:
        country=js["countryOfOrigin"][0]["name"]
    except:
        country="Unspecified"
    cur.execute('''INSERT OR IGNORE INTO Countries (Country) 
        VALUES ( ? )''', ( country, ) )
    cur.execute('SELECT id FROM Countries WHERE Country = ? ', (country, ))
    country_id = cur.fetchone()[0]

    cur.execute('''UPDATE Film SET country_id=? WHERE title=?''', 
                (country_id,title) )
    print(title,country)

    conn.commit()
