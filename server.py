from flask import Flask, send_from_directory
from Spotify import Spotify
from json import loads


# Flask config
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# global spotify object for api calls
spotify = Spotify()

miller = {}
with open('results.json') as file:
    data = file.read()
    miller = loads(data)

@app.route('/api/<artist>')
def api(artist):
    """
    API route - fetches and sends artist data
    as JSON response
    """
    if artist == 'mac-miller':
        return miller
    artist = artist.replace('-', ' ')
    return spotify.get_artist(artist)


@app.route('/js/<path:path>')
@app.route('/css/<path:path>')
def send_from_static(path):
    """
    Static file route for sending JS and CSS files
    """
    return send_from_directory('static', path)


@app.route('/<artist>')
@app.route('/')
def home(artist=None):
    """
    Main routing - sends to artist page if artist is
    in the request URL, defaults to home page
    """
    file = 'artist.html' if artist else 'index.html'
    return send_from_directory('static', file)


# when run as main
if __name__ == '__main__':
    app.run(debug=True)
