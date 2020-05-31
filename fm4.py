import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
import sys
import re
import json

#Script expects one argument. If criteria is not met, help message is displayed
if(len(sys.argv) == 2):
    fm4url = sys.argv[1]
else:
    print("Usage:")
    print("  python3 fm4.py <URL>")
    print(" ")
    print("Example:")
    print("  python3 fm4.py https://fm4.orf.at/player/20200529/4MO")
    quit()

#Extract substring of interest. The parts separated by '/' are then flipped to be usable by the api
fm4 = re.search('[0-9]+/[a-zA-Z0-9]+',fm4url).group(0)
fm4 = fm4.split('/')[::-1]
fm4 = '/'.join(fm4)

#Fetch and parse response from JSON API
with urllib.request.urlopen('https://audioapi.orf.at/fm4/json/4.0/broadcast/' + fm4 + '?_o=fm4.orf.at') as response:
   html = response.read()
fm4dict = json.loads(html)['items']

#Extract interpreter and title fields from all items of type M (music)
songs = [i.get('interpreter', '') + ' - ' + i.get('title', '') for i in fm4dict if i.get('type', '') == 'M']

#For each item, fetch YouTube results
for song in songs:
    song_formatted = urllib.parse.quote(song)
    with urllib.request.urlopen('https://www.youtube.com/results?search_query=' + song_formatted) as response:
       html = response.read()
    soup = BeautifulSoup(html, features="lxml")
    items = soup.findAll("div", class_='yt-lockup-content')[:10]

    #Extract relevant information
    titles = [item.find('a').text[:50].ljust(50) + item.find('span', class_='accessible-description').text for item in items]
    metas = [item.find('ul', class_='yt-lockup-meta-info') for item in items]
    metas = [[li.text for li in meta.findAll('li')[::-1]] if meta is not None else [] for meta in metas]
    assert len(titles) == len(metas) == len(items)
    max_title = max([len(title) for title in titles])

    print(song)
    for i in range(len(items)):
        print('  ' + titles[i], end='  ')
        print(', '.join(metas[i]))
