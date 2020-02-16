from bs4 import BeautifulSoup
import requests
from threading import Thread
from time import time


# custom Session for requests
# increased pool connections and size so many requests 
# can be stacked and handled
session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=40, pool_maxsize=40)
session.mount('https://', adapter)

# global Genius url formats for artists/songs
song_url = 'https://genius.com/{}-{}-lyrics'


def threaded(func):
    """
    Function decorator that multithreads given target
    function with parameters
    """
    def wrapper(*args, **kwargs):
        thread = Thread(target=func, args=args)
        thread.start()
        return thread
    return wrapper


def scrape(url, tag, class_name):
    """ 
    Scrapes site for the target elements using BeautifulSoup.
    Returns a list of all elements matched by given tag and classname.
    """
    res = session.get(url, timeout=20)
    if not res.ok:
        return []
    html = BeautifulSoup(res.content, 'html.parser')
    elements = html.find_all(tag, {'class': class_name})
    return elements


def genius_url_friendly(phrase):
    """ 
    Converts the given name to a "Genius URL friendly" verison.
    Returns a sanitized url where punctuation is removed, and 
    characters are replaced with couterparts.
    """
    # TODO: sanitize using regex
    res = phrase.lower() \
        .replace(u'\u2018', '') \
        .replace(u'\u2019', '') \
        .replace(u'\u201c', '') \
        .replace(u'\u201d', '') \
        .replace('$', 's') \
        .replace('&', 'and') \
        .replace('.', '') \
        .replace('\'', '') \
        .replace(',', '') \
        .replace('.', '') \
        .replace('?', '') \
        .replace('/', '') \
        .replace('!', '') \
        .replace(' ', '-')
    # remove "()" section (ex. "(feat. J Cole)")
    if '(' in res:
        res = res[:res.find('(') - 1].strip()
    return res.replace('--', '-')


@threaded
def get_song_lyrics(song, artist_name, song_name):
    """
    Scrapes Genius in a separate thread for song lyrics.
    Updates song dictionary fields with the song name and lyrics.
    """
    a_name = genius_url_friendly(artist_name)
    s_name = genius_url_friendly(song_name)
    if len(s_name) == 0:
        return
    url = song_url.format(a_name, s_name)
    s = time()
    content = scrape(url, 'div', 'song_body-lyrics')
    lyrics = content[0].text.strip().split() if len(content) else ""
    e = time()
    print(f'{song_name}: {round(e - s, 4)}')
    song['name'] = song_name
    song['lyrics'] = ' '.join(lyrics)
    return

