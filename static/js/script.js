let charts = {}; // Store all active charts

async function analyzeAudio() {
    const fileInput = document.getElementById('audioFile');
    const customerIDInput = document.getElementById('customerID');
    const agentIDInput = document.getElementById('agentID');
    const loading = document.getElementById('loading');
    const file = fileInput.files[0];
    const customerID = customerIDInput.value;
    const agentID = agentIDInput.value;

    if (!file) {
        showError('Please select an audio file');
        return;
    }

    if (!customerID || !agentID) {
        showError('Customer ID and Agent ID are required');
        return;
    }

    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('customer_id', customerID);
        formData.append('agent_id', agentID);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        updateDashboard(data);
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function updateDashboard(data) {
    clearCharts(); // Destroy all existing charts before creating new ones

    // Display text analysis
    const textAnalysisElement = document.getElementById('textAnalysis');
    textAnalysisElement.innerHTML = data.text_analysis ? `<pre>${data.text_analysis}</pre>` : 'No text analysis available';

    // Theme Analysis
    document.getElementById('theme').textContent = data.data.theme || 'No theme detected';

    // Speakers Chart
    if (data.data.number_of_speakers) {
        createChart('speakersChart', 'bar', {
            labels: ['Speakers Detected'],
            datasets: [{
                label: 'Number of Speakers',
                data: [data.data.number_of_speakers],
                backgroundColor: ['#4e73df']
            }]
        });
    }

    // Mood Chart
    if (data.data.mood_analysis) {
        createChart('moodChart', 'bar', {
            labels: ['Happy', 'Sad', 'Angry', 'Neutral'],
            datasets: [
                {
                    label: 'Agent',
                    data: Object.values(data.data.mood_analysis.agent),
                    backgroundColor: '#4e73df'
                },
                {
                    label: 'Customer',
                    data: Object.values(data.data.mood_analysis.customer),
                    backgroundColor: '#1cc88a'
                }
            ]
        });
    }

    // Key Topics
    const topicsList = document.getElementById('topics');
    topicsList.innerHTML = data.data.key_topics.length
        ? data.data.key_topics.map(topic => `<li>${topic}</li>`).join('')
        : '<li>No topics detected</li>';

    // Background Noise
    document.getElementById('backgroundNoise').textContent = `Background Noise: ${data.data.background_noise}%`;

    // Transcription
    document.getElementById('transcription').innerHTML = `<pre>${data.data.transcription || 'No transcription available'}</pre>`;

    // Speaker Diarization
    const speakerDiarizationElement = document.getElementById('speakerDiarization');
    speakerDiarizationElement.innerHTML = data.data.speaker_diarization.length
        ? data.data.speaker_diarization.map(entry =>
            `<p><strong>${entry.speaker} (${entry.time}):</strong> ${entry.text}</p>`
        ).join('')
        : 'No speaker diarization available';

    // Sentiment Analysis Chart
    if (data.data.sentiment_analysis) {
        createChart('sentimentChart', 'bar', {
            labels: ['Positive', 'Neutral', 'Negative'],
            datasets: [
                {
                    label: 'Agent',
                    data: Object.values(data.data.sentiment_analysis.agent),
                    backgroundColor: '#4e73df'
                },
                {
                    label: 'Customer',
                    data: Object.values(data.data.sentiment_analysis.customer),
                    backgroundColor: '#1cc88a'
                }
            ]
        });
    }

    // Rate of Interest
    if (data.data.rate_of_interest) {
        createChart('interestChart', 'pie', {
            labels: ['Agent', 'Customer'],
            datasets: [{
                data: [data.data.rate_of_interest.agent, data.data.rate_of_interest.customer],
                backgroundColor: ['#4e73df', '#1cc88a']
            }]
        });
    }

    // Persuasion Analysis
    if (data.data.persuasion_analysis) {
        createChart('persuasionChart', 'pie', {
            labels: ['Agent', 'Customer'],
            datasets: [{
                data: [data.data.persuasion_analysis.agent, data.data.persuasion_analysis.customer],
                backgroundColor: ['#4e73df', '#1cc88a']
            }]
        });
    }

    // Sales Conversion Probability
    document.getElementById('salesConversionProbability').textContent = `Sales Conversion Probability: ${data.data.sales_conversion_probability}%`;

    // Call Duration
    document.getElementById('callDuration').textContent = `Call Duration: ${data.data.call_duration} seconds`;

    // Resolution Time
    document.getElementById('resolutionTime').textContent = `Resolution Time: ${data.data.resolution_time} seconds`;

    // Follow-Up Required
    const followUpRequiredElement = document.getElementById('followUpRequired');
    followUpRequiredElement.textContent = data.data.follow_up_required ? 'Yes' : 'No';
    if (data.data.follow_up_required) {
        followUpRequiredElement.insertAdjacentHTML('afterend', `<p>Reason: ${data.data.follow_up_summary}</p>`);
    }

    // Churn Prediction
    createChart('churnChart', 'pie', {
        labels: ['Churn Probability', 'Retention Probability'],
        datasets: [{
            data: [data.data.churn_prediction, 100 - data.data.churn_prediction],
            backgroundColor: ['#ff6b6b', '#4e73df']
        }]
    });
}

// Function to create a new chart (and destroy old one if exists)
function createChart(chartId, type, data) {
    let ctx = document.getElementById(chartId).getContext('2d');

    if (charts[chartId]) {
        charts[chartId].destroy(); // Destroy old chart if exists
    }

    charts[chartId] = new Chart(ctx, {
        type: type,
        data: data,
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

// Function to destroy all existing charts
function clearCharts() {
    Object.keys(charts).forEach(chartKey => {
        if (charts[chartKey]) {
            charts[chartKey].destroy();
        }
    });
    charts = {}; // Reset chart storage
}

// Show loading animation
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

// Hide loading animation
function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error';
    errorDiv.textContent = message;
    document.body.prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}
