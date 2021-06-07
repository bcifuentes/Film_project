import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup,CData
import json
import re

def get_json(url):
    html = urllib.request.urlopen(url).read()

    soup = BeautifulSoup(html,"html.parser")
    tags = soup("script")
    for tag in tags:
        if tag.get("type",None)=="application/ld+json":
            text=tag.contents[0]
    soup=BeautifulSoup(text,"html.parser")
    for cd in soup.findAll(text=True): 
        if isinstance(cd, CData):
            js=json.loads(re.findall("{.*}",cd.string)[0])
    return js

#js=get_json("https://letterboxd.com/film/cruella/")
#print(json.dumps(js,indent=4))


