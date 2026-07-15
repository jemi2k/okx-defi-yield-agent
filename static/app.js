/**
 * OKX DeFi Yield Optimizer - Dashboard JavaScript
 */

var API = window.location.origin;

// ========== INIT ==========

document.addEventListener('DOMContentLoaded', function () {
    checkStatus();
    loadStats();
    loadOpportunities();
    bindEvents();
});

function bindEvents() {
    var el;

    // Hero buttons
    el = document.getElementById('btnAnalyze');
    if (el) el.addEventListener('click', runAnalysis);
    el = document.getElementById('btnStrategy');
    if (el) el.addEventListener('click', focusStrategy);

    // Panel buttons
    el = document.getElementById('btnRefreshAnalysis');
    if (el) el.addEventListener('click', runAnalysis);
    el = document.getElementById('btnRefreshOpps');
    if (el) el.addEventListener('click', loadOpportunities);
    el = document.getElementById('btnGenerateStrategy');
    if (el) el.addEventListener('click', generateStrategy);
    el = document.getElementById('btnAsk');
    if (el) el.addEventListener('click', askQuestion);

    // Enter key for Q&A
    el = document.getElementById('questionInput');
    if (el) el.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') askQuestion();
    });
}

function checkStatus() {
    fetch(API + '/health')
        .then(function (r) { return r.json(); })
        .then(function () {
            var dot = document.getElementById('statusDot');
            var txt = document.getElementById('statusText');
            if (dot) dot.className = 'status-dot online';
            if (txt) txt.textContent = 'Online';
        })
        .catch(function () {
            var dot = document.getElementById('statusDot');
            var txt = document.getElementById('statusText');
            if (dot) dot.className = 'status-dot';
            if (txt) txt.textContent = 'Offline';
        });
}

// ========== STATS ==========

function loadStats() {
    fetch(API + '/api/v1/market')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var m = data.data.metrics;
            setText('totalOpps', m.total_opportunities);
            setText('avgApy', m.average_apy + '%');
            setText('highestApy', m.highest_apy + '%');
            setText('marketTrend', m.market_trend);
        })
        .catch(function () {
            setText('totalOpps', '--');
            setText('avgApy', '--');
            setText('highestApy', '--');
            setText('marketTrend', '--');
        });
}

function loadOpportunities() {
    var body = document.getElementById('opportunitiesBody');
    if (!body) return;
    body.innerHTML = '<div class="loading">Loading opportunities...</div>';

    fetch(API + '/api/v1/opportunities')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var opps = data.data.opportunities;
            if (!opps || opps.length === 0) {
                body.innerHTML = '<div class="loading">No opportunities available.</div>';
                return;
            }
            var html = '<div class="opp-list">';
            opps.forEach(function (o) {
                html +=
                    '<div class="opp-row">' +
                    '<div><span class="opp-name">' + esc(o.name) + '</span><span class="opp-protocol">' + esc(o.protocol) + ' &middot; ' + esc(o.type) + '</span></div>' +
                    '<div class="opp-apy">' + (o.apy || 0) + '%</div>' +
                    '<div class="opp-min">Min $' + (o.min_deposit || 0) + '</div>' +
                    '<div class="opp-badge"><span class="rec-risk risk-' + (o.risk || 'medium') + '">' + (o.risk || 'medium') + '</span></div>' +
                    '</div>';
            });
            html += '</div>';
            body.innerHTML = html;
        })
        .catch(function () {
            body.innerHTML = '<div class="loading">Failed to load. Please try again.</div>';
        });
}

// ========== MARKET ANALYSIS ==========

function runAnalysis() {
    // Scroll to analysis section
    var section = document.getElementById('analysisSection');
    if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });

    var loadingEl = document.getElementById('analysisLoading');
    var contentEl = document.getElementById('analysisContent');
    if (loadingEl) { loadingEl.style.display = 'block'; loadingEl.textContent = 'Analyzing market conditions...'; }
    if (contentEl) contentEl.style.display = 'none';

    fetch(API + '/api/v1/analyze')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) throw new Error('API error');
            renderAnalysis(data.data);
        })
        .catch(function () {
            if (loadingEl) loadingEl.textContent = 'Analysis failed. Please try again.';
        });
}

function renderAnalysis(data) {
    var loadingEl = document.getElementById('analysisLoading');
    var contentEl = document.getElementById('analysisContent');
    if (!loadingEl || !contentEl) return;
    loadingEl.style.display = 'none';
    contentEl.style.display = 'block';

    var a = data.ai_analysis || {};
    var s = a.market_summary || {};
    var recs = a.top_recommendations || [];
    var aiText = a.ai_analysis || '';

    var html = '';

    // Market Overview
    html += '<div style="margin-bottom:8px;font-size:12px;color:#7B89A8;text-transform:uppercase;letter-spacing:0.6px;">Market Summary</div>';
    html += '<div class="market-overview-grid">';
    html += '<div class="metric-box"><div class="metric-label">Average APY</div><div class="metric-value">' + (s.average_apy || '--') + '%</div></div>';
    html += '<div class="metric-box"><div class="metric-label">Highest APY</div><div class="metric-value">' + (s.highest_apy || '--') + '%</div></div>';
    html += '<div class="metric-box"><div class="metric-label">Sentiment</div><div class="metric-value" style="text-transform:capitalize;">' + (s.market_sentiment || 'neutral') + '</div></div>';
    html += '</div>';

    // AI Analysis
    html += '<div class="ai-box"><div class="ai-label">AI Analysis</div><div class="ai-text">' + esc(aiText) + '</div></div>';

    // Top Recommendations
    if (recs.length > 0) {
        html += '<div style="margin-bottom:8px;font-size:12px;color:#7B89A8;text-transform:uppercase;letter-spacing:0.6px;">Top Recommendations</div>';
        html += '<div class="rec-grid">';
        recs.forEach(function (r, i) {
            html +=
                '<div class="rec-card">' +
                '<span class="rec-rank">#' + (i + 1) + '</span>' +
                '<div class="rec-protocol">' + esc(r.protocol || 'Unknown') + '</div>' +
                '<div class="rec-product">' + esc(r.name || '--') + '</div>' +
                '<div class="rec-apy">' + (r.apy || 0) + '%</div>' +
                '<span class="rec-risk risk-' + (r.risk || 'medium') + '">' + (r.risk || 'medium') + '</span>' +
                '</div>';
        });
        html += '</div>';
    }

    // Action hint
    html += '<div style="text-align:center;padding:12px 0 4px;color:#7B89A8;font-size:13px;">';
    html += 'Use the <strong>Strategy Generator</strong> below to create a personalized allocation based on this analysis.';
    html += '</div>';

    contentEl.innerHTML = html;
}

// ========== STRATEGY ==========

function focusStrategy() {
    var section = document.getElementById('strategySection');
    if (section) section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function generateStrategy() {
    var amount = parseFloat(document.getElementById('amount').value) || 5000;
    var risk = document.getElementById('risk').value || 'moderate';

    var loadingEl = document.getElementById('strategyLoading');
    var contentEl = document.getElementById('strategyContent');
    if (loadingEl) { loadingEl.style.display = 'block'; loadingEl.textContent = 'Generating personalized strategy...'; }
    if (contentEl) contentEl.style.display = 'none';

    fetch(API + '/api/v1/strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_profile: {
                amount: amount,
                risk_tolerance: risk,
                horizon: 'medium-term',
                preferred_protocols: ['OKX Earn', 'X Layer DEX']
            }
        })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success) throw new Error('API error');
        renderStrategy(data.data, amount);
    })
    .catch(function () {
        if (loadingEl) loadingEl.textContent = 'Failed to generate strategy. Please try again.';
    });
}

function renderStrategy(data, amount) {
    var loadingEl = document.getElementById('strategyLoading');
    var contentEl = document.getElementById('strategyContent');
    if (!loadingEl || !contentEl) return;
    loadingEl.style.display = 'none';
    contentEl.style.display = 'block';

    var rec = data.algorithmic_recommendation || {};
    var ai = data.ai_strategy || {};
    var div = rec.diversification || [];

    var html = '';

    // AI Strategy text
    if (ai.ai_strategy) {
        html += '<div class="ai-box"><div class="ai-label">AI Strategy</div><div class="ai-text">' + esc(ai.ai_strategy) + '</div></div>';
    }

    // Allocation table
    if (div.length > 0) {
        html += '<div style="margin-bottom:8px;font-size:12px;color:#7B89A8;text-transform:uppercase;letter-spacing:0.6px;">Recommended Allocation</div>';
        html += '<table class="allocation-table">';
        html += '<thead><tr><th>Protocol</th><th>Product</th><th>APY</th><th>Amount</th><th>Monthly</th><th>Risk</th></tr></thead><tbody>';

        div.forEach(function (item) {
            html += '<tr>' +
                '<td>' + esc(item.protocol) + '</td>' +
                '<td>' + esc(item.product) + '</td>' +
                '<td class="apy-cell">' + item.apy + '%</td>' +
                '<td class="amount-cell">$' + item.amount + '</td>' +
                '<td>$' + item.estimated_monthly_yield + '</td>' +
                '<td><span class="rec-risk risk-' + (item.risk || 'medium') + '">' + (item.risk || 'medium') + '</span></td>' +
                '</tr>';
        });

        html += '</tbody></table>';

        // Summary bar
        html += '<div class="strategy-summary">';
        html += '<div class="summary-item"><div class="summary-label">Total Investment</div><div class="summary-value">$' + amount.toLocaleString() + '</div></div>';
        html += '<div class="summary-item"><div class="summary-label">Estimated Monthly Return</div><div class="summary-value" style="color:#00D67D;">$' + (rec.estimated_monthly_yield || 0) + '</div></div>';
        html += '<div class="summary-item"><div class="summary-label">Blended APY</div><div class="summary-value" style="color:#00D67D;">' + (rec.estimated_apy || 0) + '%</div></div>';
        html += '</div>';
    } else {
        html += '<div class="loading">No allocation data available for this profile.</div>';
    }

    // Action hint
    html += '<div style="text-align:center;padding:12px 0 4px;color:#7B89A8;font-size:13px;">';
    html += 'This strategy is generated by DeepSeek AI analyzing current DeFi market conditions. ';
    html += 'Adjust your <strong>investment amount</strong> or <strong>risk tolerance</strong> above to explore different strategies.';
    html += '</div>';

    contentEl.innerHTML = html;

    // Scroll to the result
    contentEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ========== Q&A ==========

function askQuestion() {
    var input = document.getElementById('questionInput');
    var result = document.getElementById('qaResult');
    if (!input || !result) return;
    var question = input.value.trim();
    if (!question) return;

    result.style.display = 'block';
    result.innerHTML = '<div class="loading">Thinking...</div>';

    fetch(API + '/api/v1/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (data.success) {
            result.innerHTML =
                '<div class="qa-answer-box">' +
                '<div class="qa-question">Q: ' + esc(question) + '</div>' +
                esc(data.data.answer) +
                '</div>';
        } else {
            result.innerHTML = '<div class="loading">Could not get answer. Please try again.</div>';
        }
    })
    .catch(function () {
        result.innerHTML = '<div class="loading">Could not get answer. Please try again.</div>';
    });
}

// ========== UTILS ==========

function setText(id, val) {
    var el = document.getElementById(id);
    if (el) el.textContent = val;
}

function esc(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}