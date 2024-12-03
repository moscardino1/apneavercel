import os
import requests
import base64
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import lyricsgenius

load_dotenv()

# Configuration remains the same
@dataclass
class Config:
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    GENIUS_CLIENT = os.getenv('GENIUS_CLIENT')
    GENIUS_SECRET = os.getenv('GENIUS_SECRET')
    GENIUS_TOKEN = os.getenv('GENIUS_TOKEN')
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')


class APIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def post_request(self, url: str, payload: Dict) -> Dict:
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json() if response.ok else {}

class SpotifyClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()

    def get_access_token(self) -> str:
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth_bytes}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"}
        )
        return response.json()['access_token']

    def search_track(self, query: str) -> Optional[Dict]:
        response = requests.get(
            "https://api.spotify.com/v1/search",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"q": query, "type": "track", "limit": 1}
        )
        return response.json()['tracks']['items'][0] if response.json()['tracks']['items'] else None


class LyricsClient:
    def __init__(self, access_token: str):
        self.genius = lyricsgenius.Genius(access_token)

    def get_lyrics(self, artist: str, title: str) -> dict:
        """Fetch lyrics for a given artist and song title."""
        song = self.genius.search_song(title, artist)
        if song:
            return {"lyrics": song.lyrics}
        else:
            return {"lyrics": "Lyrics not found"}

class NLPAnalyzer(APIClient):
    EMOTION_API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
    SUMMARIZATION_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    SENTIMENT_API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment"

    def analyze_emotion(self, text: str) -> Dict:
        result = self.post_request(self.EMOTION_API_URL, {"inputs": text})
        return result[0] if result else {}

    def summarize_text(self, text: str) -> str:
        result = self.post_request(self.SUMMARIZATION_API_URL, {
            "inputs": text,
            "parameters": {
                "max_length": 100,
                "min_length": 30,
                "do_sample": False
            }
        })
        return result[0]['summary_text'] if result else "Error in summarization"

    def analyze_sentiment(self, text: str) -> Dict:
        return self.post_request(self.SENTIMENT_API_URL, {"inputs": text})

# Flask application setup
app = Flask(__name__)
CORS(app)

# Initialize configuration and clients
config = Config()
spotify_client = SpotifyClient(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET)
lyrics_client = LyricsClient(config.GENIUS_TOKEN) #config.GENIUS_CLIENT, config.GENIUS_SECRET, 
nlp_analyzer = NLPAnalyzer(config.HUGGINGFACE_API_KEY)

def clean_lyrics(lyrics: str) -> str:
    # Remove metadata and formatting
    lines = lyrics.split('\n')
    cleaned_lines = [line for line in lines if not line.startswith('[') and not 'Contributors' in line]
    return ' '.join(cleaned_lines)

@app.route('/search', methods=['POST'])
def search_song():
    query = request.json.get('query')
    
    # Search track
    track = spotify_client.search_track(query)
    if not track:
        return jsonify({"error": "Track not found"}), 404

    # Get lyrics
    try:
        lyrics_response = lyrics_client.get_lyrics(
            track['artists'][0]['name'], 
            track['name']
        )
        lyrics = lyrics_response.get('lyrics', "No lyrics available")
    except Exception:
        lyrics = "No lyrics available"

    cleaned_lyrics = clean_lyrics(lyrics)

    # Analyze text
    nlp_results = {
        "emotions": nlp_analyzer.analyze_emotion(cleaned_lyrics),
        "summary": nlp_analyzer.summarize_text(cleaned_lyrics),
        "sentiment": nlp_analyzer.analyze_sentiment(cleaned_lyrics)
    }
    print("artist and name:",track['artists'][0]['name'],  track['name'])
    print("lyrics:" ,lyrics)
    print("nlp_restul=",nlp_results)
    return jsonify({
        "track": {
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "album_image": track['album']['images'][0]['url'] if track['album']['images'] else None
        },
        "lyrics": lyrics,
        "nlp_results": nlp_results
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)