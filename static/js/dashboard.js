// Dashboard & Chart.js Integration for Fake News Detector
document.addEventListener('DOMContentLoaded', () => {
    let ratioChart = null;
    let metricsChart = null;

    const kpiTotal = document.getElementById('kpi-total');
    const kpiReal = document.getElementById('kpi-real');
    const kpiRealPct = document.getElementById('kpi-real-pct');
    const kpiFake = document.getElementById('kpi-fake');
    const kpiFakePct = document.getElementById('kpi-fake-pct');
    const kpiAvgConf = document.getElementById('kpi-avg-conf');

    const historyTableBody = document.getElementById('history-table-body');
    const historySearch = document.getElementById('history-search');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const refreshStatsBtn = document.getElementById('refresh-stats-btn');

    // Make loadDashboardData globally accessible for app.js tab switching
    window.loadDashboardData = async function(shouldScroll = false) {
        await Promise.all([fetchAnalytics(), fetchHistory()]);
    };

    // 1. Fetch KPI Analytics and Update Charts
    async function fetchAnalytics() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();

            if (data.status === 'success') {
                const stats = data.analytics;

                // Update KPI Cards
                kpiTotal.textContent = (stats.total_analyzed || 0).toLocaleString();
                kpiReal.textContent = (stats.real_count || 0).toLocaleString();
                kpiRealPct.textContent = `${stats.real_percentage || 0}%`;

                kpiFake.textContent = (stats.fake_count || 0).toLocaleString();
                kpiFakePct.textContent = `${stats.fake_percentage || 0}%`;

                kpiAvgConf.textContent = `${stats.avg_confidence || 0}%`;

                // Update Charts
                renderRatioChart(stats.real_count || 0, stats.fake_count || 0);
                renderMetricsChart(stats);
            }
        } catch (err) {
            console.error('Failed to load analytics statistics:', err);
        }
    }

    // Render Real vs Fake Doughnut Chart
    function renderRatioChart(realCount, fakeCount) {
        const ctx = document.getElementById('ratioChart').getContext('2d');

        if (ratioChart) {
            ratioChart.destroy();
        }

        const hasData = (realCount + fakeCount) > 0;

        ratioChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Real News', 'Fake News'],
                datasets: [{
                    data: hasData ? [realCount, fakeCount] : [1, 1],
                    backgroundColor: hasData ? ['#10b981', '#f43f5e'] : ['#334155', '#475569'],
                    borderColor: '#1e293b',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#94a3b8',
                            font: { family: 'Inter', size: 12 }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                if (!hasData) return ' No data analyzed yet';
                                const total = realCount + fakeCount;
                                const val = context.raw;
                                const pct = ((val / total) * 100).toFixed(1);
                                return ` ${context.label}: ${val} (${pct}%)`;
                            }
                        }
                    }
                },
                cutout: '70%'
            }
        });
    }

    // Render Metrics Bar Chart
    function renderMetricsChart(stats) {
        const ctx = document.getElementById('metricsChart').getContext('2d');

        if (metricsChart) {
            metricsChart.destroy();
        }

        metricsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Total', 'Real', 'Fake', 'Avg Conf %'],
                datasets: [{
                    label: 'Count / Percentage',
                    data: [
                        stats.total_analyzed || 0,
                        stats.real_count || 0,
                        stats.fake_count || 0,
                        stats.avg_confidence || 0
                    ],
                    backgroundColor: [
                        'rgba(99, 102, 241, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(244, 63, 94, 0.7)',
                        'rgba(168, 85, 247, 0.7)'
                    ],
                    borderColor: [
                        '#6366f1',
                        '#10b981',
                        '#f43f5e',
                        '#a855f7'
                    ],
                    borderWidth: 1,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    },
                    y: {
                        ticks: { color: '#94a3b8', font: { family: 'Inter' } },
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // 2. Fetch History Log
    async function fetchHistory(searchQuery = '') {
        try {
            const url = searchQuery
                ? `/api/history?search=${encodeURIComponent(searchQuery)}`
                : '/api/history';

            const response = await fetch(url);
            const data = await response.json();

            if (data.status === 'success') {
                renderHistoryTable(data.history);
            }
        } catch (err) {
            console.error('Failed to load history list:', err);
            historyTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Error loading prediction history log.</td></tr>';
        }
    }

    // Render History Table Rows
    function renderHistoryTable(records) {
        if (!records || records.length === 0) {
            historyTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted" style="padding: 2rem;">No prediction history records found.</td></tr>';
            return;
        }

        historyTableBody.innerHTML = records.map(r => {
            const isReal = r.prediction.toUpperCase() === 'REAL';
            const badgeClass = isReal ? 'badge-real-sm' : 'badge-fake-sm';
            const icon = isReal ? '<i class="fa-solid fa-check"></i>' : '<i class="fa-solid fa-triangle-exclamation"></i>';

            // Format date string
            let dateStr = r.created_at;
            try {
                const d = new Date(r.created_at);
                dateStr = d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            } catch (e) {}

            return `
                <tr>
                    <td>#${r.id}</td>
                    <td><span class="text-muted" style="font-size: 0.8rem;">${dateStr}</span></td>
                    <td><span class="text-snippet" title="${escapeHtml(r.text)}">${escapeHtml(r.text)}</span></td>
                    <td><span class="${badgeClass}">${icon} ${r.prediction}</span></td>
                    <td><strong>${r.confidence.toFixed(1)}%</strong></td>
                    <td>${r.word_count || 0} words</td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="deleteHistoryItem(${r.id})" title="Delete record">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    // Helper: HTML Escaping
    function escapeHtml(text) {
        if (!text) return '';
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Global Delete Single History Item
    window.deleteHistoryItem = async function(id) {
        if (!confirm(`Delete prediction record #${id}?`)) return;

        try {
            const response = await fetch(`/api/history/${id}`, { method: 'DELETE' });
            const data = await response.json();
            if (data.status === 'success') {
                window.loadDashboardData();
            } else {
                alert('Could not delete record: ' + data.message);
            }
        } catch (e) {
            alert('Failed to delete history item.');
        }
    };

    // Search Filter with Debounce
    let searchTimeout = null;
    historySearch.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            fetchHistory(historySearch.value);
        }, 300);
    });

    // Clear All History Button
    clearHistoryBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to delete ALL prediction history from the database? This cannot be undone.')) return;

        try {
            const response = await fetch('/api/history', { method: 'DELETE' });
            const data = await response.json();
            if (data.status === 'success') {
                window.loadDashboardData();
            }
        } catch (e) {
            alert('Error clearing prediction history.');
        }
    });

    // Manual Refresh Button
    refreshStatsBtn.addEventListener('click', () => {
        window.loadDashboardData();
    });

    // Initial Load
    window.loadDashboardData();
});
