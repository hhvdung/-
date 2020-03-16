from bs4 import BeautifulSoup
import requests
import re
from flask import Flask, render_template, url_for, redirect, request
app = Flask(__name__)

url = 'https://igg-games.com/'
searchurl = 'https://igg-games.com/?s='

def geturl(url):
    r = requests.get(url)
    return  BeautifulSoup(r.text, 'html.parser')

def crawldata(url):
    soup = geturl(url)
    games = soup.find_all('article')
    data = []
    for game in games:
        g = {'title' : '', 'genre' : '', 'description' : '', 'img': '', 'link' : ''}
        g['title'] = game.h2.a.text.replace(' Free Download','')
        g['genre'] = game.p.text[19:]
        g['img'] = game.img['src']
        g['link'] = game.h2.a['href']
        g['description'] = game.select_one('.uk-margin-medium-top').p.text.replace(' […]','...').replace(g['title'],'')[62:]
        data.append(g)
    return data

def crawlnavbar(url):
    soup = geturl(url+'1')
    games = soup.find_all('a', class_='menu-item-object-category')
    genre = []
    for game in games:
      if game not in genre:
        gen = {'link' : '', 'genre' : ''}
        gen['link'] = game['href']
        gen['genre'] = game.text
        genre.append(gen)
      if gen['genre'] == 'VR':
        break
    return genre

def searchcrawl(url):
    r = requests.get(url)
    soup =  BeautifulSoup(r.text.replace('h1', 'h2').replace('<p>','<p class="wtf"> '), 'html.parser')
    games = soup.find_all('article')
    data = []
    for game in games:
        try:
            g = {'title' : '', 'genre' : '', 'description' : '', 'img': '', 'link' : ''}
            g['title'] = game.h2.a.text.replace(' Free Download','')
            g['genre'] = game.p.text.replace('\nPosted by Admin | ','')
            g['img'] = game.img['src']
            g['link'] = game.h2.a['href']
            g['description'] = game.select_one('.wtf').text.replace(' Free Download PC Game Cracked in Direct Link and Torrent.',' -')
            data.append(g)
        except:
            pass
    return data

@app.route('/', defaults = {'page' : 1})
@app.route('/<int:page>', methods = ['POST', 'GET'])
@app.route('/', defaults = {'page' : 1})
def index(page):
    data = crawldata(url + 'page/'+str(page))
    genre = crawlnavbar(url)
    return render_template('index.html', data = data, genre = genre, page = page)

@app.route('/search', methods = ['POST', 'GET'])
def search(genre = crawlnavbar(url)):
    key = request.form['search']
    url = searchurl + key.replace(' ','+')
    data = searchcrawl(url)
    reply = 'Search result for "%s"' % key
    return render_template('search.html', data = data, reply = reply, genre = genre)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)