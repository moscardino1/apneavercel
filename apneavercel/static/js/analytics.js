function showLoading() {
    console.log('Loading started'); // Debugging log
    document.getElementById('loadingOverlay').style.display = 'block';
    document.getElementById('loadingIndicator').style.display = 'block';
}

function hideLoading() {
    console.log('Loading ended'); // Debugging log
    document.getElementById('loadingOverlay').style.display = 'none';
    document.getElementById('loadingIndicator').style.display = 'none';
}


async function searchSong() {
    showLoading();
    try {
        const query = document.getElementById('searchInput').value;
        if (!query.trim()) {
            hideLoading();
            return;
        }

        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        });

        const data = await response.json();
        if (response.ok) {
            displayResults(data);
        } else {
            console.error('Error:', data.error);
            displayError(data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        displayError('An error occurred while searching for the song');
    } finally {
        hideLoading();
    }
}

function displayError(message) {
    const resultsContainer = document.getElementById('results');
    if (!resultsContainer) {
        console.error('Results container not found');
        return;
    }

    resultsContainer.style.display = 'block';
    resultsContainer.innerHTML = `
        <div class="error-message">
            <p>${message}</p>
            <p>Please check the browser console for more details.</p>
        </div>
    `;
}

function displayResults(data) {
    // Clear previous results
    const resultsContainer = document.getElementById('results');
    if (!resultsContainer) {
        console.error('Results container not found');
        return;
    }

    // Show results container
    resultsContainer.style.display = 'block';

    // Create or update song info section
    let songHeader = resultsContainer.querySelector('.song-header');
    if (!songHeader) {
        songHeader = document.createElement('div');
        songHeader.className = 'song-header';
        resultsContainer.appendChild(songHeader);
    }

    songHeader.innerHTML = `
        <div class="album-art">
            <img id="albumArt" src="${data.album_art || ''}" alt="Album Art">
        </div>
        <div class="song-info">
            <h2 id="trackName">${data.track_name || ''}</h2>
            <p id="artistName">${data.artist || ''}</p>
            <p id="albumName">${data.album || ''}</p>
            <a id="spotifyLink" href="${data.spotify_url || '#'}" target="_blank" class="spotify-button">
                <i class="fab fa-spotify"></i> Listen on Spotify
            </a>
        </div>
    `;

    // Create or update analytics section
    let analyticsGrid = resultsContainer.querySelector('.analytics-grid');
    if (!analyticsGrid) {
        analyticsGrid = document.createElement('div');
        analyticsGrid.className = 'analytics-grid';
        resultsContainer.appendChild(analyticsGrid);
    }

    analyticsGrid.innerHTML = `
        <div class="analytics-card">
            <h3>Sentiment Analysis</h3>
            <canvas id="sentimentChart"></canvas>
        </div>
        <div class="analytics-card">
            <h3>Emotional Analysis</h3>
            <canvas id="emotionsChart"></canvas>
        </div>
        <div class="analytics-card">
            <h3>Topic Analysis</h3>
            <canvas id="topicsChart"></canvas>
        </div>
        <div class="analytics-card">
            <h3>Word Frequency</h3>
            <div id="wordCloud"></div>
        </div>
    `;

    // Create or update lyrics section
    let lyricsSection = resultsContainer.querySelector('.lyrics-section');
    if (!lyricsSection) {
        lyricsSection = document.createElement('div');
        lyricsSection.className = 'lyrics-section';
        resultsContainer.appendChild(lyricsSection);
    }

    lyricsSection.innerHTML = `
        <h3>Lyrics</h3>
        <div id="lyrics" class="lyrics-content">${data.lyrics.replace(/\n/g, '<br>')}</div>
    `;

    // Initialize charts after DOM elements are created
    initializeCharts(data);
}

function initializeCharts(data) {
    // Clear previous charts
    const chartIds = ['sentimentChart', 'emotionsChart', 'topicsChart'];
    chartIds.forEach(id => {
        const canvas = document.getElementById(id);
        if (canvas) {
            canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
        }
    });

    createSentimentChart(data.sentiment);
    createEmotionsChart(data.emotions);
    createTopicsChart(data.topics);
    createWordCloud(data.word_frequency);
}

function createSentimentChart(sentimentData) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    // Clear existing chart if it exists
    if (window.sentimentChart instanceof Chart) {
        window.sentimentChart.destroy();
    }
    
    // Extract scores and labels from the sentiment data
    const data = sentimentData[0];  // Get first array element
    const scores = data.map(item => item.score);
    const labels = data.map(item => {
        // Convert "X stars" to sentiment labels
        switch(item.label) {
            case '1 star': return 'Very Negative';
            case '2 stars': return 'Negative';
            case '3 stars': return 'Neutral';
            case '4 stars': return 'Positive';
            case '5 stars': return 'Very Positive';
            default: return item.label;
        }
    });
    
    window.sentimentChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: scores,
                backgroundColor: [
                    '#ff6b6b',  // Very Negative
                    '#ff9f89',  // Negative
                    '#ffe66d',  // Neutral
                    '#4ecdc4',  // Positive
                    '#2ecc71'   // Very Positive
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            return `${context.label}: ${(value * 100).toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

function createEmotionsChart(emotionsData) {
    const ctx = document.getElementById('emotionsChart').getContext('2d');
    
    // Clear existing chart if it exists
    if (window.emotionsChart instanceof Chart) {
        window.emotionsChart.destroy();
    }

    // Extract data from the emotions array
    const data = emotionsData[0];  // Get first array element
    const labels = data.map(item => item.label.charAt(0).toUpperCase() + item.label.slice(1));
    const values = data.map(item => item.score);

    window.emotionsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Emotion Intensity',
                data: values,
                backgroundColor: 'rgba(29, 185, 84, 0.2)',
                borderColor: 'rgba(29, 185, 84, 1)',
                pointBackgroundColor: 'rgba(29, 185, 84, 1)',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(29, 185, 84, 1)'
            }]
        },
        options: {
            responsive: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 0.2
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${(context.raw * 100).toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

function createTopicsChart(topicsData) {
    const ctx = document.getElementById('topicsChart').getContext('2d');
    
    // Clear existing chart if it exists
    if (window.topicsChart instanceof Chart) {
        window.topicsChart.destroy();
    }

    // Sort topics by score in descending order
    const scores = topicsData.scores;
    const labels = topicsData.labels;
    
    // Create array of objects for sorting
    const combined = labels.map((label, i) => ({
        label: label.replace(/_/g, ' '),
        score: scores[i]
    }));
    
    // Sort by score
    combined.sort((a, b) => b.score - a.score);
    
    // Take top 5 topics
    const topTopics = combined.slice(0, 5);

    window.topicsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topTopics.map(item => item.label.charAt(0).toUpperCase() + item.label.slice(1)),
            datasets: [{
                label: 'Topic Relevance',
                data: topTopics.map(item => item.score),
                backgroundColor: 'rgba(29, 185, 84, 0.7)',
                borderColor: 'rgba(29, 185, 84, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${(context.raw * 100).toFixed(1)}% relevance`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return (value * 100) + '%';
                        }
                    }
                },
                y: {
                    ticks: {
                        callback: function(value) {
                            const label = this.getLabelForValue(value);
                            // Truncate long labels
                            return label.length > 20 ? label.substr(0, 17) + '...' : label;
                        }
                    }
                }
            }
        }
    });
}

function createWordCloud(wordFrequency) {
    const width = document.getElementById('wordCloud').offsetWidth;
    const height = 300;

    // Clear previous word cloud
    d3.select("#wordCloud").html("");

    const svg = d3.select("#wordCloud")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    const layout = d3.layout.cloud()
        .size([width, height])
        .words(wordFrequency.map(d => ({
            text: d[0],
            size: 10 + d[1] * 5
        })))
        .padding(5)
        .rotate(() => ~~(Math.random() * 2) * 90)
        .fontSize(d => d.size)
        .on("end", draw);

    layout.start();

    function draw(words) {
        svg.append("g")
            .attr("transform", `translate(${width/2},${height/2})`)
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", d => `${d.size}px`)
            .style("font-family", "Montserrat")
            .style("fill", () => d3.schemeCategory10[~~(Math.random() * 10)])
            .attr("text-anchor", "middle")
            .attr("transform", d => `translate(${d.x},${d.y})rotate(${d.rotate})`)
            .text(d => d.text);
    }
}
