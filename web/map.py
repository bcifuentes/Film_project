import sqlite3
import pycountry
import plotly.express as px
import pandas as pd

conn = sqlite3.connect('letter.sql')
cur = conn.cursor()

def updater(location):
    if location=="USSR":location="Russian Federation"
    if location=="Czechoslovakia":location="Slovakia"
    return location
    
def get_alpha_3(location):

    try:
        return pycountry.countries.get(name=location).alpha_3
    except:
        if location=="USA":return "USA"
        elif location=="South Korea":return "KOR"
        elif location=="UK":return "GBR"
        elif location=="Taiwan":return "TWN"
        elif location=="Venezuela":return "VEN"
        else:return None




ct="Country,C,Films\n"
gt="Genre,Films\n"
c=list()
cur.execute("SELECT MAX(id) FROM Countries")
ID=cur.fetchone()[0]
for id in range(1,ID):
    cur.execute('''
    SELECT COUNT(Film.title),Countries.Country
    FROM Film JOIN Countries ON Film.country_id=Countries.id 
    WHERE Film.country_id=? ''',(id,))
    result=cur.fetchone()
    if result[1]==None:continue
    country=updater(result[1])
    country_id=get_alpha_3(country)
    if country_id==None:continue
    count=result[0]
    ct+=country+","+country_id+","+str(count)+"\n"
    
cur.execute("SELECT MAX(genre_id) FROM Classification")
ID=cur.fetchone()[0]
for id in range(1,ID):
    cur.execute('''
	SELECT COUNT(Film.title),Genres.genre 
	FROM Film JOIN Genres JOIN Classification ON Film.id=Classification.film_id AND Genres.id=Classification.genre_id
	WHERE Classification.genre_id=? ''',(id,))
    result=cur.fetchone()
    if result[1]==None:continue
    genre=result[1]
    count=result[0]
    gt+=genre+","+str(count)+"\n"

f=open("ct.csv","w")
f.write(ct)
f.close()
df=pd.read_csv("ct.csv")

fig = px.choropleth(df,locations="C",
                    color="Films",hover_name="Country",
                    color_continuous_scale="Viridis",width=450,
                    
                    )

fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)', lakecolor='Black',
                                                             landcolor='rgba(51,17,0,0.2)',
                                                             ),
                  font = {"size": 9, "color":"White"},
                  margin={"r":0,"t":10,"l":0,"b":10},
                  paper_bgcolor='Black',
                  plot_bgcolor='Black',width=450)

fig.update_geos(projection_type="orthographic")
#fig.show()
fig.write_html( "mapa.html" )
fig = px.bar(df, x='C', y='Films',color="Films", labels={'C':'Countries'},hover_name="Country")
fig.update_layout(font = {"size": 9, "color":"White"},
                  margin={"r":0,"t":10,"l":0,"b":10},
                  paper_bgcolor='Black',
                  plot_bgcolor='Black')
fig.write_html( "bargeo.html" )

f=open("gt.csv","w")
f.write(gt)
f.close()
df=pd.read_csv("gt.csv")
fig = px.bar(df, y='Genre', x='Films',color="Films",hover_name="Genre")
fig.update_layout(font = {"size": 10, "color":"White"},                  
                  paper_bgcolor='Black',
                  margin={"r":0,"t":10,"l":0,"b":10},
                  plot_bgcolor='Black',width=450)
fig.update_traces(marker_coloraxis=None)
fig.write_html( "bargnr.html" )
