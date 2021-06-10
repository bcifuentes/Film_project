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

#df["Code"] = df["Paises"].apply(lambda x:get_alpha_3(x))

cur.execute("SELECT MAX(id) FROM Countries")
ID=cur.fetchone()[0]

ct="Country,C,Films\n"
c=list()
for id in range(1,ID):
    cur.execute('''
    SELECT COUNT(Film.title),Countries.Country  
    FROM Film JOIN Countries ON Film.country_id=Countries.id 
    WHERE Film.country_id=? ''',(id,))
    result=cur.fetchone()
    if result[1]==None:continue
    country=updater(result[1])
    if country=="USSR":country="Russian Federation"

    country_id=get_alpha_3(country)
    if country_id==None:continue
    count=result[0]
    ct+=country+","+country_id+","+str(count)+"\n"

f=open("ct.csv","w")
f.write(ct)
f.close()
df=pd.read_csv("ct.csv")
print(df)
fig = px.choropleth(df,locations="C",
                    color="Films",hover_name="Country",
                    color_continuous_scale="Viridis",width=450,
                    
                    )

fig.update_layout(geo=dict(bgcolor= 'rgba(0,0,0,0)', lakecolor='Black',
                                                             landcolor='rgba(51,17,0,0.2)',
                                                             ),
                  font = {"size": 9, "color":"White"},
                  titlefont = {"size": 15, "color":"White"},
                  margin={"r":0,"t":10,"l":0,"b":10},
                  paper_bgcolor='Black',
                  plot_bgcolor='Black',width=450)

fig.update_geos(projection_type="orthographic")
#fig.show()
fig.write_html( "mapa.html" )
