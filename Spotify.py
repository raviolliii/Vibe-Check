import utils
from threading import Thread
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from json import loads, dumps
from textblob import TextBlob

# load in spotify credentials from environment
import os
from dotenv import load_dotenv
load_dotenv()


class Spotify:
    """
    Class that handles Spotify API and provides functions
    to get artist and song data
    """

    def __init__(self):
        # initialize spotify API with credentials
        self.__init_spotify()

    def __init_spotify(self):
        """ Creates credentials/token for spotipy """
        credentials = SpotifyClientCredentials(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET')
        )
        self._token = credentials.get_access_token()
        self.spotify = spotipy.Spotify(self._token)

    def get_artist(self, artist_name):
        """
        Searches the Spotify api for the given artist name,
        and returns an Artist with their Albums populated
        """
        try:
            results = self.spotify.search(
                q="artist:" + artist_name,
                limit=1,
                type="artist"
            )["artists"]["items"][0]
        except Exception as e:
            # TODO: catch token expired exception
            # re-initialize spotify api in case token expired
            print('Error in get_artist:', e)
            self.__init_spotify()

        artist = {
            'name': results['name'],
            'albums': [],
            'imageURL': results['images'][0]['url'],
            'URL': results['external_urls']['spotify']
        }
        albums = self.get_artist_albums(results['id'])

        for album in albums:
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
        counter, LIMIT = 0, 5
        for item in results:
            name, album_id = item["name"], item["id"]
            # filter out redundant albums (delux, remixes, etc.)
            if name in seen or "(" in name:
                continue
            # TODO: fix this limit value of 10
            counter += 1
            if counter > LIMIT:
                break
            seen.add(name)
            thread = self.create_album(albums, name, album_id)
            threads.append(thread)

        # wait for all threads to finish before returning albums
        for thread in threads:
            thread.join()
        return albums

    @utils.threaded
    def create_album(self, albums, name, album_id):
        """
        Creates an Album, populated with its Songs, and
        adds it to the list of Albums
        """
        songs = self.get_album_songs(album_id)
        if not songs:
            return
        total = sum([s['polarity'] for s in songs])
        album = {'name': name, 'songs': songs}
        album['sentiment'] = total / len(songs)
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
            name, track_id = item["name"], item["id"]
            artist = item["artists"][0]["name"]
            values[track_id] = {}
            thread = utils.get_song_lyrics(values[track_id], artist, name)
            threads.append(thread)
        for thread in threads:
            thread.join()
        
        songs = []
        self.get_song_features(values)
        for track_id in values:
            result = values[track_id] or {}
            if not result.get('lyrics'):
                continue
            polarity = TextBlob(result['lyrics']).sentiment.polarity
            song = {
                'name': result['name'],
                'valence': result['valence'],
                'polarity': polarity
            }
            songs.append(song)

        return songs

    def get_song_features(self, songs):
        """
        Gets audio features of each song in songs (list). Sets
        the valence value of the song, discards other data points.
        """
        song_ids = list(songs.keys())
        feature_set = self.spotify.audio_features(song_ids)
        for song_id, features in zip(song_ids, feature_set):
            songs[song_id]['valence'] =  features['valence']
        return
