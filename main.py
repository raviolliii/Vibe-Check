from Spotify import Spotify
from Graph import *
from time import time  # DEV: remove later
from pprint import pprint  # DEV: remove later
from json import dumps

# Create the spotify instance, and get the artist
spotify = Spotify()
s = time()
person = spotify.get_artist('the weeknd')
with open('test.json', 'w+') as file:
    file.write(dumps(person, indent=2))

# track "performance"
print("\nTime: ", (time() - s))

"""
text sentiment: 	sentiment value
danceability:		how danceable it is based on:
energy:				activity/intensity based on:
valence: 			musical positiveness/negativeness
tempo: 				tempo of song (bpm)
"""
# -0.5340
