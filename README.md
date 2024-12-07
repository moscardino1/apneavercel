# ApneaMusic - Song Analytics

ApneaMusic is a web application that provides advanced analytics for songs, including sentiment analysis, emotional analysis, topic analysis, and more. Users can search for songs, view their lyrics, and explore various insights related to the music.

## Features

- **Search for Songs**: Users can search for songs by title or artist.
- **Lyrics Display**: View the lyrics of the searched song.
- **Song Analytics**: Get insights on sentiment, emotions, word frequency, and topics related to the song.
- **Trending Songs**: View a list of trending songs based on user searches.
- **Responsive Design**: The application is designed to work on both desktop and mobile devices.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript (with libraries like Chart.js and D3.js)
- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **APIs**: 
  - Spotify API for song data
  - Genius API for lyrics
  - Hugging Face API for sentiment and emotion analysis

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL
- Node.js (for managing frontend dependencies)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/apneamusic.git
   cd apneamusic
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**:
   - Create a PostgreSQL database and update the `POSTGRES_URL_NON_POOLING` environment variable in a `.env` file.
   - Run the following command to create the database tables:
   ```bash
   flask db upgrade
   ```

5. **Set up environment variables**:
   Create a `.env` file in the root directory and add the following variables:
   ```plaintext
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   GENIUS_TOKEN=your_genius_token
   POSTGRES_URL_NON_POOLING=your_postgres_url
   ```

6. **Run the application**:
   ```bash
   flask run
   ```

7. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- **Search for a Song**: Use the search bar on the homepage to find a song by title or artist.
- **View Analytics**: After searching, you will see the song's lyrics along with various analytics.
- **Explore Trending Songs**: Navigate to the trending page to see which songs are currently popular.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Spotify API](https://developer.spotify.com/documentation/web-api/) for song data.
- [Genius API](https://docs.genius.com/) for lyrics.
- [Hugging Face](https://huggingface.co/) for sentiment and emotion analysis models.