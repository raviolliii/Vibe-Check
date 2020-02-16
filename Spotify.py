import utils
from Artists import *
from threading import Thread
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from json import loads, dumps
from textblob import TextBlob


# load spotify app config
CONFIG = {}
with open('.config.json') as file:
	data = file.read()
	CONFIG = loads(data)


class Spotify:

	def __init__(self):
		""" Creates credentials/token for spotipy """
		self.config = CONFIG
		credentials = SpotifyClientCredentials(**self.config)
		self.token = credentials.get_access_token()
		self.spotify = spotipy.Spotify(self.token)

	def get_artist(self, artist_name):
		"""
		Searches the Spotify api for the given artist name,
		and returns an Artist with their Albums populated
		"""
		results = self.spotify.search(
			q="artist:" + artist_name,
			limit=1,
			type="artist"
		)["artists"]["items"][0]

		artist = {
			'name': results['name'],
			'albums': [],
			'imageURL': results['images'][0]['url'],
			'URL': results['external_urls']['spotify']
		}
		albums = self.get_artist_albums(results['id'])
		for album in albums[:10]:
			# artist.add_album(album)
			artist['albums'].append(album)
		return artist

	def get_artist_albums(self, artist_id):
		"""
		Searches the Spotify api for an artist's list of
		Albums, and returns a list of those Albums populated
		with their songs
		"""
		results = self.spotify.artist_albums(
			artist_id,
			album_type="album",
			limit=20
		)["items"]

		threads, albums = [], []
		seen = set()
		for item in results:
			name, spotify_id = item["name"], item["id"]
			# filter out redundant albums (delux, remixes, etc.)
			if name in seen or "(" in name:
				continue
			seen.add(name)
			# multithread the album creation process for runtime performance
			target, args = self.create_album, (albums, name, spotify_id)
			# thread = Thread(target=target, args=args)
			thread = self.create_album(albums, name, spotify_id)
			threads.append(thread)

		# wait for all threads to finish before returning albums
		for thread in threads:
			thread.join()
		return albums

	@utils.threaded
	def create_album(self, albums, name, spotify_id):
		"""
		Creates an Album, populated with its Songs, and
		adds it to the list of Albums
		"""
		# album = Album(name, spotify_id)
		album = {
			'name': name,
			'songs': self.get_album_songs(spotify_id)
		}
		# Don't add the album if the song list is empty
		if not album['songs']:
			return
		# album.calc_sentiment()
		total = sum([s['polarity'] for s in album['songs']])
		album['sentiment'] = total / len(album['songs'])
		albums.append(album)
		return

	def get_album_songs(self, album_id):
		"""
		Searches the Spotify api for the list of songs in
		the given album, and returns a list of Songs with
		their lyrics and sentiment value set
		"""
		results = self.spotify.album_tracks(
			album_id=album_id
		)["items"]

		values, threads = {}, []
		for item in results:
			name, spotify_id = item["name"], item["id"]
			artist = item["artists"][0]["name"]
			values[spotify_id] = {}
			thread = utils.get_song_lyrics(values[spotify_id], artist, name)
			threads.append(thread)
			# Don't add the song if the lyrics weren't found
		
		for thread in threads:
			thread.join()
		
		songs = []
		self.get_song_features(values)
		for spotify_id in values:
			result = values[spotify_id]
			if not result or not result['lyrics']:
				continue
			song = {
				'name': result['name'],
				'valence': result['valence'],
				'polarity': TextBlob(result['lyrics']).sentiment.polarity
			}
			songs.append(song)

		return songs

	def get_song_features(self, songs):
		song_ids = list(songs.keys())
		feature_set = self.spotify.audio_features(song_ids)
		for song_id, features in zip(song_ids, feature_set):
			songs[song_id]['valence'] =  features['valence']
		# features["danceability"] = (features["danceability"] * 2) - 1 # 0.625
		# features["danceability"] -= 0.35
		# features["valence"] = (features["valence"] * 2) - 1
		# return {'valence': features['valence']}
