import sqlite3
html=open("plantilla.html","r")
text=html.read()
html.close()

def image(link):
    schema="<article><img src='{:}'/></a></article>".format(link)
    return schema

def gen_tabs(number):
    schema='''  <div id='{:}' class="tabcontent">
    <section id='galeria3'> 
    %REEMPLACE({:})
    </section>   
    </div>'''.format(number,number)
    schema2='''<button class="tablinks" onclick="openCity(event, '{:}')">{:}</button>'''.format(number,number)
    return schema,schema2

conn = sqlite3.connect('letter.sql')
cur = conn.cursor()

ranger=60
films=900

n_films=0
for id in range(0,films):
    cur.execute("SELECT image FROM Film WHERE id=?",(id,))
    link=cur.fetchone()
    if link==None:
        continue
    n_films+=1

if (n_films/ranger)==int(n_films/ranger):
    tabs=int(n_films/ranger)
else: tabs=int(n_films/ranger)+1


t,b="",""
images,counter=list(),list()
for tab in range(1,tabs+1):
   t+=gen_tabs(tab)[0]+"\n"
   b+=gen_tabs(tab)[1]+"\n"
   images.append("")
   counter.append(1)


text=text.replace("%BOTONES",b)
text=text.replace("%TABS",t)
html=open("your_films.html","w")
html.write(text)
html.close()

html=open("your_films.html","r")
text=html.read()

tt=1
for id in range(0,films):
    cur.execute("SELECT image FROM Film WHERE id=? ",(id,))
    link=cur.fetchone()
    if link==None:
        continue
    tab=(tt/ranger)
    if tab==int(tab):
        tab=int(tab)-1
    else:
        tab=int(tab)
    tt+=1
    im=image(link[0])
    images[tab]+=im+"\n"

for tab in range(1,tabs+1):
    text=text.replace("%REEMPLACE({:})".format(tab),images[tab-1])

html=open("your_films.html","w")
html.write(text)
html.close()
            
