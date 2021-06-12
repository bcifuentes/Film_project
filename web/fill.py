import sqlite3
import os


def image(link,title,director,rate,year):
    if rate is not None:
        rate=round(rate)
    else:
        rate=0
    l=["","","","",""]
    for ii in range(5):
        if ii==rate-1:
            l[ii]="CHECKED"  
    schema='''
    <article class='image'>	
    <img class="image__img" src='{l}' alt='{tt}'>
    <div class="image__overlay image__overlay--primary">
    <div class="image__title">{tt}</div>
    <p class="image__description">
    {d}<br>
    {y}
    </p>
    <div class="rate">
    <input type="radio" id="{tt}5" name="{tt}" value="5" {l4} />
    <label for="{tt}5" title="text">5 stars</label>
    <input type="radio" id="{tt}4" name="{tt}" value="4" {l3}/>
    <label for="{tt}4" title="text">4 stars</label>
    <input type="radio" id="{tt}3" name="{tt}" value="3" {l2}/>
    <label for="{tt}3" title="text">3 stars</label>
    <input type="radio" id="{tt}2" name="{tt}" value="2" {l1}/>
    <label for="{tt}2" title="text">2 stars</label>
    <input type="radio" id="{tt}1" name="{tt}" value="1" {l0}/>
    <label for="{tt}1" title="text">1 star</label>
    </div>
    </div>
    </article>
    '''.format(l=link,y=year,d=director,l0=l[0],l1=l[1],l2=l[2],l3=l[3],l4=l[4],tt=title)
    return schema


def gen_tabs(number):
    schema='''  <div id='{:}' class="tabcontent">
    <section id='galeria3'> 
    %REEMPLACE({:})
    </section>   
    </div>'''.format(number,number)
    schema2='''<button class="tablinks" onclick="openCity(event, '{:}')">{:}</button>'''.format(number,number)
    return schema,schema2

def your(conn,cur,order="",sens=""):
    html=open("plantilla","r")
    text=html.read()
    html.close()

    ranger=60
    films=900

    n_films=0

    for id in range(0,films):
        cur.execute('''SELECT Film.image FROM Film WHERE id=?''',(id,))
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

  
    if order=="quit":return None
    if len(order)<1:order="NULL"
    if order!="NULL":
        text=text.replace("%ORG","<h2>Sort by {:}</h2>".format(order))
    text=text.replace("%ORG","")
    if order=="date":order="Film.id"

    if len(sens)<1:sens="DESC"
    try:
        cur.execute('''SELECT Film.image,Film.title,Directors.director,Film.rate,Film.year 
        FROM Film JOIN Directors 
        ON Film.director_id=Directors.id ORDER BY {:} {:}'''.format(order,sens))
    except:
        return None

    data=cur.fetchall()
    tt=1
    for row in data:

        tab=(tt/ranger)
        if tab==int(tab):
            tab=int(tab)-1
        else:
            tab=int(tab)
        tt+=1
        
        im=image(row[0],row[1],row[2],row[3],row[4])
        
        if tt%6==2:
            sep="</section><section id='galeria3'>"
        else:
            sep=""
        images[tab]+=sep+im+"\n"

    
    for tab in range(1,tabs+1):
        text=text.replace("%REEMPLACE({:})".format(tab),images[tab-1])
    
    html=open("your_films.html","w")
    html.write(text)
    html.close()
    try:
        os.system("firefox index.html")
    except:
        os.system("chrome index.html")

def stats(conn,cur):
    html=open("stats","r")
    text=html.read()
    html.close()
    cur.execute("SELECT User.username, User.name,COUNT(Film.id),User.Date FROM User, Film")
    user_data=cur.fetchone()
    username=user_data[0]
    name=user_data[1]
    count=user_data[2]
    date=user_data[3]
    
    welcome="Welcome <b>{U}</b>, because you are special to us, we want you to know that to date, you have seen a total of <b>{C}</b> movies, we invite you to explore even more! below you have a count of your activity.".format(U=username,D=date,C=count)

    
    text=text.replace("%WELCOME",welcome)
    try:
        cur.execute('''SELECT image,title,director,rate,year 
        FROM Favorites''')
    except:
        return None
    data=cur.fetchall()
    images=""
    for row in data:
        im=image(row[0],row[1],row[2],row[3],row[4])
        images+=im+"\n"
        
    text=text.replace("%FAVORITES",images)
    html=open("stats.html","w")
    html.write(text)
    html.close()


conn = sqlite3.connect('letter.sql')
cur = conn.cursor()
order=input("Order by: ")
sens=input("ASC or DESC: ")
your(conn,cur,order,sens)
stats(conn,cur)
