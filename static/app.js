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

    // AI Analysis (rendered as markdown-like HTML)
    html += '<div class="ai-box"><div class="ai-label">AI Analysis</div><div class="ai-text">' + renderMarkdown(aiText) + '</div></div>';

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

    // AI Strategy text (rendered as markdown-like HTML)
    if (ai.ai_strategy) {
        html += '<div class="ai-box"><div class="ai-label">AI Strategy</div><div class="ai-text">' + renderMarkdown(ai.ai_strategy) + '</div></div>';
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
                renderMarkdown(data.data.answer) +
                '</div>';
        } else {
            result.innerHTML = '<div class="loading">Could not get answer. Please try again.</div>';
        }
    })
    .catch(function () {
        result.innerHTML = '<div class="loading">Could not get answer. Please try again.</div>';
    });
}

// ========== MARKDOWN RENDERER ==========

function renderMarkdown(text) {
    if (!text) return '';
    var lines = text.split('\n');
    var html = '';
    var inTable = false;
    var inOrderedList = false;
    var inUnorderedList = false;

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var trimmed = line.trim();

        // Empty line - close open structures
        if (!trimmed) {
            if (inTable) { html += '</tbody></table>'; inTable = false; }
            if (inOrderedList) { html += '</ol>'; inOrderedList = false; }
            if (inUnorderedList) { html += '</ul>'; inUnorderedList = false; }
            html += '<div style="height:6px;"></div>';
            continue;
        }

        // Headings
        if (trimmed.startsWith('### ')) {
            closeAll();
            html += '<h4 style="font-size:15px;font-weight:600;color:#E2E8F0;margin:16px 0 8px;">' + esc(trimmed.slice(4)) + '</h4>';
            continue;
        }
        if (trimmed.startsWith('## ')) {
            closeAll();
            html += '<h3 style="font-size:17px;font-weight:700;color:#E2E8F0;margin:20px 0 10px;">' + esc(trimmed.slice(3)) + '</h3>';
            continue;
        }
        if (trimmed.startsWith('# ')) {
            closeAll();
            html += '<h2 style="font-size:19px;font-weight:700;color:#E2E8F0;margin:24px 0 12px;">' + esc(trimmed.slice(2)) + '</h2>';
            continue;
        }

        // Horizontal rule
        if (trimmed === '---') {
            closeAll();
            html += '<hr style="border:0;border-top:1px solid #1A2440;margin:14px 0;">';
            continue;
        }

        // Tables
        if (trimmed.startsWith('|') && !inTable) {
            var sep = lines[i + 1] ? lines[i + 1].trim() : '';
            if (sep && sep.startsWith('|') && sep.indexOf('---') !== -1) {
                closeAll();
                inTable = true;
                var headers = trimmed.split('|').filter(function(c) { return c.trim(); });
                html += '<table style="width:100%;border-collapse:collapse;margin:10px 0;font-size:13px;"><thead><tr>';
                headers.forEach(function(h) {
                    html += '<th style="text-align:left;padding:7px 10px;border-bottom:1px solid #1A2440;color:#7B89A8;font-weight:500;text-transform:uppercase;font-size:11px;letter-spacing:0.5px;">' + esc(h.trim()) + '</th>';
                });
                html += '</tr></thead><tbody>';
                i++; // skip separator line
                continue;
            }
        }
        if (inTable && trimmed.startsWith('|')) {
            var cells = trimmed.split('|').filter(function(c) { return c.trim(); });
            html += '<tr>';
            cells.forEach(function(c) {
                html += '<td style="padding:7px 10px;border-bottom:1px solid #1A2440;color:#E2E8F0;">' + formatBold(c.trim()) + '</td>';
            });
            html += '</tr>';
            // Check if next line is NOT a table row
            var next = lines[i + 1] ? lines[i + 1].trim() : '';
            if (!next || !next.startsWith('|')) {
                html += '</tbody></table>';
                inTable = false;
            }
            continue;
        }

        // Ordered lists
        var olMatch = trimmed.match(/^(\d+)[.)]\s+(.*)/);
        if (olMatch) {
            if (inUnorderedList) { html += '</ul>'; inUnorderedList = false; }
            if (!inOrderedList) { html += '<ol style="margin:6px 0;padding-left:24px;">'; inOrderedList = true; }
            html += '<li style="margin-bottom:5px;line-height:1.6;">' + formatBold(olMatch[2]) + '</li>';
            continue;
        }

        // Unordered lists
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            var content = trimmed.startsWith('- ') ? trimmed.slice(2) : trimmed.slice(2);
            if (inOrderedList) { html += '</ol>'; inOrderedList = false; }
            if (!inUnorderedList) { html += '<ul style="margin:6px 0;padding-left:24px;">'; inUnorderedList = true; }
            html += '<li style="margin-bottom:5px;line-height:1.6;">' + formatBold(content) + '</li>';
            continue;
        }

        // Code blocks
        if (trimmed.startsWith('```')) {
            closeAll();
            html += '<pre style="background:#080C14;border:1px solid #1A2440;border-radius:8px;padding:14px 16px;margin:10px 0;font-size:12px;overflow-x:auto;font-family:monospace;color:#E2E8F0;line-height:1.6;">';
            var j = i + 1;
            while (j < lines.length && !lines[j].trim().startsWith('```')) {
                html += esc(lines[j]) + '\n';
                j++;
            }
            i = j;
            html += '</pre>';
            continue;
        }

        // Regular paragraph
        if (inOrderedList) { html += '</ol>'; inOrderedList = false; }
        if (inUnorderedList) { html += '</ul>'; inUnorderedList = false; }
        html += '<p style="margin:0 0 5px;line-height:1.7;">' + formatBold(trimmed) + '</p>';
    }

    // Close any remaining open elements
    closeAll();

    return html;

    function closeAll() {
        if (inTable) { html += '</tbody></table>'; inTable = false; }
        if (inOrderedList) { html += '</ol>'; inOrderedList = false; }
        if (inUnorderedList) { html += '</ul>'; inUnorderedList = false; }
    }
}

function formatBold(text) {
    return esc(text).replace(/\*\*(.*?)\*\*/g, '<strong style="color:#E2E8F0;">$1</strong>');
}

function esc(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}

function setText(id, val) {
    var el = document.getElementById(id);
    if (el) el.textContent = val;
}