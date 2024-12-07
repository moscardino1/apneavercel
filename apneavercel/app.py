from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests
import base64
import json
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import re
from textblob import TextBlob
import lyricsgenius
from collections import Counter
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import desc, func

app = Flask(__name__)

# Load environment variables
load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
GENIUS_TOKEN = os.getenv('GENIUS_TOKEN')

# Initialize Genius
genius = lyricsgenius.Genius(GENIUS_TOKEN)

# Configure PostgreSQL database
DATABASE_URL = os.getenv('POSTGRES_URL_NON_POOLING')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define models
class Song(db.Model):
    __tablename__ = 'song'  # Explicitly set table name
    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    album = db.Column(db.String(200))
    spotify_url = db.Column(db.String(500))
    album_art = db.Column(db.String(500))
    search_count = db.Column(db.Integer, default=1)
    last_searched = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'track_name': self.track_name,
            'artist': self.artist,
            'album': self.album,
            'spotify_url': self.spotify_url,
            'album_art': self.album_art,
            'search_count': self.search_count
        }

def get_spotify_token():
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data)
    return response.json()["access_token"]

def analyze_sentiment(text):
    API_URL = "https://api-inference.huggingface.co/models/nlptown/bert-base-multilingual-uncased-sentiment"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    return response.json()

def analyze_emotions(text):
    API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(API_URL, headers=headers, json={"inputs": text})
    return response.json()

def get_combined_summary(lyrics, annotations):
    # Combine lyrics with annotations
    combined_text = lyrics + "\n\nSong Annotations:\n"
    if annotations and 'annotations' in annotations:
        for annotation in annotations['annotations']:
            if 'body' in annotation:
                combined_text += f"\n{annotation['body']['plain']}"
    
    # Truncate text if too long (BART model typically has a limit)
    max_chars = 1024
    if len(combined_text) > max_chars:
        combined_text = combined_text[:max_chars]
    
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    response = requests.post(API_URL, headers=headers, json={
        "inputs": combined_text,
        "parameters": {"max_length": 150, "min_length": 50}
    })
    return response.json()

def extract_song_stats(lyrics):
    words = lyrics.split()
    unique_words = set(words)
    lines = lyrics.split('\n')
    word_count = len(words)
    unique_word_count = len(unique_words)
    line_count = len([l for l in lines if l.strip()])
    
    return {
        "word_count": word_count,
        "unique_word_count": unique_word_count,
        "line_count": line_count,
        "vocabulary_density": round(unique_word_count / word_count * 100, 2) if word_count > 0 else 0
    }

def analyze_word_frequency(lyrics):
    # Remove special characters and convert to lowercase
    cleaned_text = re.sub(r'[^\w\s]', '', lyrics.lower())
    
    # Split into words
    words = cleaned_text.split()
    
    # Common English stop words to filter out
    stop_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 
        'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 
        'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 
        'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
        'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
        'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
        'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could',
        'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only',
        'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use',
        'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even',
        'new', 'want', 'because', 'any', 'these', 'give', 'day',
        'most', 'us', 'is', 'am', 'are', 'was', 'were', 'been'
    }
    
    # Filter out stop words and count frequencies
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    word_counts = Counter(filtered_words)
    
    # Return top 10 most common words
    return word_counts.most_common(10)

def analyze_topics(text):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    
    # Refined topics common in popular music
    candidate_topics = [
        "romantic love",
        "breakup and heartache",
        "party and dancing",
        "personal empowerment",
        "social commentary",
        "life struggles",
        "sex and desire",
        "nostalgia and memories",
        "fame and success",
        "rebellion and defiance"
    ]
    
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": candidate_topics,
            "multi_label": True,
            "hypothesis_template": "This text is about {}."  # This helps with better classification
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def clean_lyrics(lyrics):
    # Remove the contributors and translations section
    cleaned_lyrics = re.sub(r'\d+ Contributors.*?Lyrics', '', lyrics, flags=re.DOTALL)
    
    # Remove any remaining metadata at the start
    cleaned_lyrics = re.sub(r'^.*?\[', '[', cleaned_lyrics, flags=re.DOTALL)
    
    # If there's no section marker, keep the original lyrics
    if not cleaned_lyrics.strip():
        cleaned_lyrics = lyrics
    
    return cleaned_lyrics.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search_song():
    try:
        query = request.json.get('query')
        spotify_token = get_spotify_token()
        
        # Search on Spotify
        spotify_headers = {"Authorization": f"Bearer {spotify_token}"}
        spotify_response = requests.get(
            f"https://api.spotify.com/v1/search?q={query}&type=track&limit=1",
            headers=spotify_headers
        ).json()

        if not spotify_response['tracks']['items']:
            return jsonify({'error': 'Song not found on Spotify'}), 404

        track = spotify_response['tracks']['items'][0]
        
        song = genius.search_song(track['name'], track['artists'][0]['name'])
        if not song:
            return jsonify({'error': 'Lyrics not found'}), 404
        
        # Clean the lyrics before sending
        lyrics = clean_lyrics(song.lyrics)
        
        # Get annotations and create combined summary
        annotations = genius.song_annotations(song.id)
        combined_summary = get_combined_summary(lyrics, annotations)
        
        # Analyze lyrics
        stats = extract_song_stats(lyrics)
        sentiment = analyze_sentiment(lyrics[:512])
        emotions = analyze_emotions(lyrics[:512])
        word_frequency = analyze_word_frequency(lyrics)
        
        # Add topic analysis
        topics = analyze_topics(lyrics[:512])
        
        # Track the search in database
        try:
            existing_song = Song.query.filter_by(
                track_name=track['name'],
                artist=track['artists'][0]['name']
            ).first()

            if existing_song:
                existing_song.search_count += 1
                existing_song.last_searched = datetime.utcnow()
            else:
                new_song = Song(
                    track_name=track['name'],
                    artist=track['artists'][0]['name'],
                    album=track['album']['name'],
                    spotify_url=track['external_urls']['spotify'],
                    album_art=track['album']['images'][0]['url'] if track['album']['images'] else None
                )
                db.session.add(new_song)
            
            db.session.commit()
        except Exception as db_error:
            db.session.rollback()
            print(f"Database error: {str(db_error)}")
            # Continue with the response even if database operation fails
        
        response_data = {
            'track_name': track['name'],
            'artist': track['artists'][0]['name'],
            'album': track['album']['name'],
            'spotify_url': track['external_urls']['spotify'],
            'genius_url': song.url,
            'lyrics': lyrics,
            'summary': combined_summary[0]['summary_text'] if isinstance(combined_summary, list) else combined_summary['summary_text'],
            'stats': stats,
            'sentiment': sentiment,
            'emotions': emotions,
            'topics': topics,
            'word_frequency': word_frequency,
            'album_art': track['album']['images'][0]['url'] if track['album']['images'] else None
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trending')
def get_trending():
    # Get trending songs from the last 7 days
    week_ago = datetime.utcnow() - timedelta(days=7)
    trending_songs = Song.query\
        .filter(Song.last_searched >= week_ago)\
        .order_by(desc(Song.search_count))\
        .limit(10)\
        .all()
    
    return jsonify([song.to_dict() for song in trending_songs])

@app.route('/trending')
def trending_page():
    return render_template('trending.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

if __name__ == '__main__':
    app.run(debug=True)