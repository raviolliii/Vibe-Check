from bs4 import BeautifulSoup
import requests
from threading import Thread
from time import time


session = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=40, pool_maxsize=40)
session.mount('https://', adapter)

""" Global Genius url formats for artists/songs """
artist_url = "https://genius.com/artists/{}"
song_url = "https://genius.com/{}-{}-lyrics"


# decorator to easily multithread functions
def threaded(func):
	def wrapper(*args, **kwargs):
		thread = Thread(target=func, args=args)
		thread.start()
		return thread
	return wrapper


def scrape(url, tag, class_name):
	""" Scrapes the given url for the target elements """
	res = session.get(url, timeout=20)
	if not res.ok:
		return []
	html = BeautifulSoup(res.content, "html.parser")
	elements = html.find_all(tag, {"class": class_name})
	return elements

def make_friendly(phrase):
	""" Converts the given name to a "Genius URL friendly" verison """
	# TODO: sanitize using regex
	res = phrase.lower() \
		.replace(u"\u2018", "") \
		.replace(u"\u2019", "") \
		.replace(u"\u201c","") \
		.replace(u"\u201d", "") \
		.replace("$", "s") \
		.replace("&", "and") \
		.replace(".", "") \
		.replace("\'", "") \
		.replace(",", "") \
		.replace(".", "") \
		.replace("?", "") \
		.replace("/", "") \
		.replace("!", "") \
		.replace(" ", "-")
	if "(" in res:
		res = res[:res.find("(") - 1].strip()
	return res.replace("--", "-")

@threaded
def get_song_lyrics(song, artist_name, song_name):
	""" Gets the lyrics of the given artist and song name """
	a_name = make_friendly(artist_name)
	s_name = make_friendly(song_name)
	if len(s_name) == 0:
		return ""
	url = song_url.format(a_name, s_name)
	s = time()
	content = scrape(url, "div", "song_body-lyrics")
	lyrics = content[0].text.strip().split() if len(content) else ""
	e = time()
	print(f'{song_name}: {round(e - s, 4)}')
	song['name'] = song_name
	song['lyrics'] = ' '.join(lyrics)
	return
	# return " ".join(lyrics)

