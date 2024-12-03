document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('song-search');
    const searchButton = document.getElementById('search-btn');
    const songTitle = document.getElementById('song-title');
    const artistName = document.getElementById('artist-name');
    const albumArt = document.getElementById('album-art');
    const lyricsDisplay = document.getElementById('lyrics-display');
    const emotionChart = document.getElementById('emotion-chart');
    let emotionChartInstance = null;

    // Add keyboard event listener for search
    searchInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            performSearch();
        }
    });

    searchButton.addEventListener('click', performSearch);

    function performSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            showErrorMessage('Please enter a song name');
            return;
        }

        // Add loading state
        searchButton.innerHTML = `
        Analyzing... 
        <span class="spinner">🎵</span>
    `;
        searchButton.disabled = true;

        fetchSongData(query)
            .then(data => {
                updateTrackInfo(data);
                displayLyrics(data.lyrics);
                createEmotionChart(data.nlp_results.emotions);
                resetSearchState();
            })
            .catch(error => {
                handleError(error);
                resetSearchState();
            });
    }

    function resetSearchState() {
        searchButton.textContent = 'Analyze';
        searchButton.disabled = false;
    }

    function showErrorMessage(message) {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'error-message';
        errorContainer.innerHTML = `
            <div class="error-icon">⚠️</div>
            <p>${message}</p>
        `;
        document.querySelector('.search-container').appendChild(errorContainer);
        
        // Automatically remove error after 3 seconds
        setTimeout(() => {
            errorContainer.remove();
        }, 3000);
    }

    async function fetchSongData(query) {
        const response = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });

        if (!response.ok) {
            throw new Error('Song not found. Please try another search.');
        }

        return response.json();
    }

    function updateTrackInfo(data) {
        const { track, nlp_results } = data;
        
        songTitle.textContent = track.name || 'Unknown Title';
        artistName.textContent = track.artist || 'Unknown Artist';
        
        albumArt.src = track.album_image || '';
        albumArt.style.display = track.album_image ? 'block' : 'none';
        albumArt.alt = `Album art for ${track.name}`;

        // Enhance detail displays with more context
        document.getElementById('summary-display').innerHTML = 
            `<strong>Summary:</strong> ${nlp_results.summary || 'No summary available.'}`;
        
        document.getElementById('sentiment-display').innerHTML = 
            `<strong>Sentiment:</strong> ${formatSentiment(nlp_results.sentiment) || 'No sentiment analysis available.'}`;
    }

    function formatSentiment(sentimentData) {
        if (!sentimentData || !sentimentData.length) return null;
        
        const sentiments = {
            'LABEL_0': 'Negative',
            'LABEL_1': 'Neutral',
            'LABEL_2': 'Positive'
        };

        const topSentiment = sentimentData.reduce((prev, current) => 
            (prev.score > current.score) ? prev : current
        );

        return `${sentiments[topSentiment.label]} (${(topSentiment.score * 100).toFixed(2)}%)`;
    }

    function displayLyrics(lyrics) {
        lyricsDisplay.innerHTML = `<strong>Lyrics:</strong> ${lyrics || 'Lyrics not found.'}`;
    }

    function handleError(error) {
        console.error('Error searching song:', error);
        showErrorMessage(error.message);
        songTitle.textContent = 'Error Finding Song';
        artistName.textContent = 'Please Try Again';
    }

    function createEmotionChart(emotions) {
            if (!emotions || emotions.length === 0) {
        emotionChart.innerHTML = `
            <div class="empty-state">
                <p>🎭 No emotional insights found</p>
                <small>Try another song or check lyrics availability</small>
            </div>
        `;
        return;
    }
        // Clear previous chart
        if (emotionChartInstance) {
            emotionChartInstance.destroy();
        }

        // Check if emotions data is valid
        if (!emotions || !Array.isArray(emotions) || emotions.length === 0) {
            console.warn('No emotions data available.');
            emotionChart.innerHTML = '<p>Unable to generate emotion chart</p>';
            return;
        }

        // Sort emotions by score in descending order
        const emotionData = emotions.sort((a, b) => b.score - a.score);
        const emotionLabels = emotionData.map(emotion => 
            emotion.label.charAt(0).toUpperCase() + emotion.label.slice(1)
        );
        const emotionScores = emotionData.map(emotion => emotion.score);

        // Create canvas element
        const canvas = document.createElement('canvas');
        canvas.width = 400;
        canvas.height = 300;
        emotionChart.innerHTML = '';
        emotionChart.appendChild(canvas);

        // Create chart
        emotionChartInstance = new Chart(canvas, {
            type: 'bar',
            data: {
                labels: emotionLabels,
                datasets: [{
                    label: 'Emotional Intensity',
                    data: emotionScores,
                    backgroundColor: [
                        'rgba(233, 69, 96, 0.6)',
                        'rgba(15, 52, 96, 0.6)',
                        'rgba(22, 33, 62, 0.6)',
                        'rgba(100, 200, 100, 0.6)',
                        'rgba(255, 215, 0, 0.6)'
                    ],
                    borderColor: [
                        'rgba(233, 69, 96, 1)',
                        'rgba(15, 52, 96, 1)',
                        'rgba(22, 33, 62, 1)',
                        'rgba(100, 200, 100, 1)',
                        'rgba(255, 215, 0, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        title: { 
                            display: true, 
                            text: 'Emotion Intensity',
                            color: 'white'
                        },
                        ticks: {
                            color: 'white'
                        }
                    },
                    x: {
                        ticks: {
                            color: 'white'
                        }
                    }
                },
                plugins: {
                    title: { 
                        display: true, 
                        text: 'Emotional Landscape of the Song',
                        color: 'white'
                    },
                    legend: {
                        labels: {
                            color: 'white'
                        }
                    }
                }
            }
        });
    }
});