import sqlite3
html=open("plantilla","r")
text=html.read()
html.close()

def image(link,title,director,rate):
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
    Dir: {d}
    </p>
    <div class="rate">
    <input type="radio" id="{tt}5" name="{tt}" value="5" {l4} />
    <label for="star5" title="text">5 stars</label>
    <input type="radio" id="{tt}4" name="{tt}" value="4" {l3}/>
    <label for="star4" title="text">4 stars</label>
    <input type="radio" id="{tt}3" name="{tt}" value="3" {l2}/>
    <label for="star3" title="text">3 stars</label>
    <input type="radio" id="{tt}2" name="{tt}" value="2" {l1}/>
    <label for="star2" title="text">2 stars</label>
    <input type="radio" id="{tt}1" name="{tt}" value="1" {l0}/>
    <label for="star1" title="text">1 star</label>
    </div>
    </div>
    </article>
    '''.format(l=link,d=director,l0=l[0],l1=l[1],l2=l[2],l3=l[3],l4=l[4],tt=title)
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

tt=1
for id in range(0,films):
    cur.execute('''SELECT Film.image,Film.title,Directors.director,Film.rate 
    FROM Film JOIN Directors 
    ON Film.director_id=Directors.id AND Film.id=?''',(id,))
    
    data=cur.fetchone()
    if data==None:
        continue
    
    tab=(tt/ranger)
    if tab==int(tab):
        tab=int(tab)-1
    else:
        tab=int(tab)
    tt+=1
    
    im=image(data[0],data[1],data[2],data[3])
    images[tab]+=im+"\n"

for tab in range(1,tabs+1):
    text=text.replace("%REEMPLACE({:})".format(tab),images[tab-1])

html=open("your_films.html","w")
html.write(text)
html.close()
            
