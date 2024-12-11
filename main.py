import requests
from bs4 import BeautifulSoup
import random
import json
import re
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory ='static'), name='static')
base_url = 'https://letterboxd.com'

#username =input()

def get_watchlist(base_url,username):
    data=[]
    n=1
    while True:
        url = f'{base_url}/{username}/watchlist/page/{n}/'
        r = requests.get(url)
        soup =  BeautifulSoup(r.content, 'html.parser')
        if r.status_code == 200:
            all_items = soup.find_all('div', {'data-target-link': True})
            if all_items:
                for item in all_items:
                    data.append(item['data-target-link'])
            else: break
        else: 
            print(f'Failed to retrieve the data {r.status_code}')
        n+=1

    return data 

def pick_film(base_url, watchlist):
    url = f'{base_url}{random.choice(watchlist)}'
    r = requests.get(url)
    soup =  BeautifulSoup(r.content, 'html.parser')
    all_items = soup.find_all('script', type='application/ld+json')
    for item in all_items:
        raw_content = item.string

        # Clean up JSON-LD string
        if raw_content:
            # Remove comments (/* ... */)
            cleaned_content = re.sub(r'/\*.*?\*/', '', raw_content, flags=re.DOTALL)

            
            json_data = json.loads(cleaned_content)
            return json_data['name'], json_data['genre'], json_data['image'], url

#watchlist = get_watchlist(base_url, username)
#name, genre, poster, link = pick_film(base_url, watchlist)

@app.get('/', response_class=HTMLResponse)
def get_basic_form(request: Request):
    return templates.TemplateResponse("home.html", {'request': request})

@app.post("/", response_class=HTMLResponse)
def post_basic_form(request: Request, username: str= Form(...)):
    watchlist = get_watchlist(base_url, username)
    name, genre, poster, link = pick_film(base_url, watchlist)
    return templates.TemplateResponse("home.html", {'request': request, 'name': name, 'link': link, 'poster': poster, 'genre':genre})


if __name__ == "__main__":
    uvicorn.run(app)

            