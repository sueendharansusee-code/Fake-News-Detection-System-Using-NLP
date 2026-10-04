// Main Application Logic for Fake News Detector
document.addEventListener('DOMContentLoaded', () => {
    // DOM Element References
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    const newsInput = document.getElementById('news-input');
    const charCountBadge = document.getElementById('char-count');
    const wordCountBadge = document.getElementById('word-count');
    const sampleChips = document.querySelectorAll('.sample-chip');

    const analyzeBtn = document.getElementById('analyze-btn');
    const resetBtn = document.getElementById('reset-btn');
    const retrainBtn = document.getElementById('retrain-btn');

    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const predictionOutput = document.getElementById('prediction-output');

    const verdictBox = document.getElementById('verdict-box');
    const verdictIcon = document.getElementById('verdict-icon');
    const verdictTitle = document.getElementById('verdict-title');
    const verdictSub = document.getElementById('verdict-sub');

    const confidencePercentage = document.getElementById('confidence-percentage');
    const confidenceBar = document.getElementById('confidence-bar');
    const realProbText = document.getElementById('real-prob');
    const fakeProbText = document.getElementById('fake-prob');

    const statWords = document.getElementById('stat-words');
    const statChars = document.getElementById('stat-chars');
    const statStopwords = document.getElementById('stat-stopwords');
    const statUnique = document.getElementById('stat-unique');
    const statDiversity = document.getElementById('stat-diversity');
    const tokensBox = document.getElementById('tokens-box');
    const resultTimestamp = document.getElementById('result-timestamp');

    let cachedSamples = null;

    // 1. Navigation Tab Switching
    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            navButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.add('hidden'));

            btn.classList.add('active');
            const activePane = document.getElementById(targetTab);
            if (activePane) {
                activePane.classList.remove('hidden');
            }

            // Trigger dashboard refresh when switching to dashboard tab
            if (targetTab === 'dashboard-tab' && window.loadDashboardData) {
                window.loadDashboardData();
            }
        });
    });

    // 2. Real-time Text Counter
    function updateCounters() {
        const text = newsInput.value || '';
        const charCount = text.length;
        const words = text.trim().split(/\s+/).filter(w => w.length > 0);
        const wordCount = text.trim() ? words.length : 0;

        charCountBadge.textContent = `${charCount.toLocaleString()} characters`;
        wordCountBadge.textContent = `${wordCount.toLocaleString()} words`;
    }

    newsInput.addEventListener('input', updateCounters);

    // 3. Load Sample Articles from Backend API
    async function fetchSamples() {
        try {
            const response = await fetch('/api/samples');
            const data = await response.json();
            if (data.status === 'success') {
                cachedSamples = data.samples;
            }
        } catch (err) {
            console.warn('Could not fetch online samples:', err);
        }
    }

    fetchSamples();

    // Sample chip click handler
    sampleChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const type = chip.getAttribute('data-type');
            const index = parseInt(chip.getAttribute('data-index'), 10);

            if (cachedSamples) {
                const filtered = cachedSamples.filter(s => s.label.toLowerCase() === type.toLowerCase());
                if (filtered[index]) {
                    newsInput.value = filtered[index].text;
                    updateCounters();
                    return;
                }
            }

            // Fallback hardcoded samples if fetch fails
            const fallbacks = {
                real: [
                    "NASA launches James Webb Space Telescope to observe early universe galaxies and study distant exoplanets in unprecedented detail.",
                    "The Federal Reserve announced an adjustment to interest rates following the latest consumer price index report showing moderation in inflation data."
                ],
                fake: [
                    "SHOCKING SECRET: Whistleblower reveals secret alien base inside Earth's core controlled by underground Illuminati elites!",
                    "MIRACLE CURE: Doctors are stunned! Drinking boiled lemon water with baking soda cures all known diseases overnight! Big Pharma tried to ban this video!"
                ]
            };

            if (fallbacks[type] && fallbacks[type][index]) {
                newsInput.value = fallbacks[type][index];
                updateCounters();
            }
        });
    });

    // 4. Analyze News Request
    analyzeBtn.addEventListener('click', async () => {
        const text = newsInput.value.trim();

        if (!text) {
            alert('Please enter a news headline or article text before analyzing.');
            newsInput.focus();
            return;
        }

        if (text.length < 5) {
            alert('Text is too short. Please enter a complete headline or article.');
            return;
        }

        // UI Loading state
        emptyState.classList.add('hidden');
        predictionOutput.classList.add('hidden');
        loadingState.classList.remove('hidden');
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });

            const data = await response.json();

            if (response.ok && data.status === 'success') {
                renderPredictionResults(data);
            } else {
                alert(data.message || 'An error occurred during analysis.');
                emptyState.classList.remove('hidden');
            }
        } catch (err) {
            console.error('API Error:', err);
            alert('Failed to connect to the backend server. Please make sure Flask is running.');
            emptyState.classList.remove('hidden');
        } finally {
            loadingState.classList.add('hidden');
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fa-solid fa-robot"></i> Analyze News';
        }
    });

    // Render Prediction Output UI
    function renderPredictionResults(data) {
        const isReal = data.prediction.toUpperCase() === 'REAL';
        const confidence = data.confidence;
        const probs = data.probabilities || {};

        const realProb = probs['REAL'] !== undefined ? probs['REAL'] : (isReal ? confidence : (100 - confidence));
        const fakeProb = probs['FAKE'] !== undefined ? probs['FAKE'] : (!isReal ? confidence : (100 - confidence));

        // Update Verdict Box
        verdictBox.className = 'verdict-box ' + (isReal ? 'verdict-real' : 'verdict-fake');
        verdictIcon.innerHTML = isReal ? '<i class="fa-solid fa-shield-check"></i>' : '<i class="fa-solid fa-triangle-exclamation"></i>';
        verdictTitle.textContent = isReal ? 'LIKELY REAL' : 'LIKELY FAKE';
        verdictSub.textContent = isReal
            ? 'High linguistic probability of standard journalistic patterns.'
            : 'Contains linguistic markers commonly associated with fake or deceptive news.';

        // Confidence & Progress Bar
        confidencePercentage.textContent = `${confidence.toFixed(1)}%`;
        confidenceBar.style.width = `${confidence}%`;
        confidenceBar.className = 'meter-bar-fill ' + (isReal ? 'meter-fill-real' : 'meter-fill-fake');

        realProbText.textContent = `${realProb.toFixed(1)}%`;
        fakeProbText.textContent = `${fakeProb.toFixed(1)}%`;

        // Text Statistics
        const stats = data.stats || {};
        statWords.textContent = (stats.word_count || 0).toLocaleString();
        statChars.textContent = (stats.char_count || 0).toLocaleString();
        statStopwords.textContent = (stats.stopword_count || 0).toLocaleString();
        statUnique.textContent = (stats.unique_words || 0).toLocaleString();
        statDiversity.textContent = `${stats.lexical_diversity_pct || 0}%`;

        // Processed Tokens
        tokensBox.textContent = data.processed_text || '(No tokens extracted)';

        // Timestamp
        const now = new Date();
        resultTimestamp.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });

        // Show result box
        predictionOutput.classList.remove('hidden');

        // Refresh dashboard if analytics are active
        if (window.loadDashboardData) {
            window.loadDashboardData(false);
        }
    }

    // 5. Reset / Clear Button
    resetBtn.addEventListener('click', () => {
        newsInput.value = '';
        updateCounters();
        predictionOutput.classList.add('hidden');
        loadingState.classList.add('hidden');
        emptyState.classList.remove('hidden');
    });

    // 6. Retrain Model Button
    if (retrainBtn) {
        retrainBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to retrain the ML model on the current dataset?')) return;
            retrainBtn.disabled = true;
            retrainBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Retraining Model...';

            try {
                const response = await fetch('/api/retrain', { method: 'POST' });
                const data = await response.json();
                if (data.status === 'success') {
                    alert(data.message);
                } else {
                    alert('Retraining failed: ' + data.message);
                }
            } catch (e) {
                alert('Server error during model retraining.');
            } finally {
                retrainBtn.disabled = false;
                retrainBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate"></i> Retrain Model Now';
            }
        });
    }
});
