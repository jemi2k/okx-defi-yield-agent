const API_BASE = window.location.origin;

document.addEventListener('DOMContentLoaded', function() {
    checkStatus();
    loadDashboard();
});

function checkStatus() {
    fetch(API_BASE + '/health')
        .then(r => r.json())
        .then(data => {
            document.getElementById('statusDot').className = 'status-dot online';
            document.getElementById('statusText').textContent = 'Online';
        })
        .catch(() => {
            document.getElementById('statusDot').className = 'status-dot';
            document.getElementById('statusText').textContent = 'Offline';
        });
}

function loadDashboard() {
    fetch(API_BASE + '/api/v1/market')
        .then(r => r.json())
        .then(data => {
            const metrics = data.data.metrics;
            document.getElementById('totalOpps').textContent = metrics.total_opportunities;
            document.getElementById('avgApy').textContent = metrics.average_apy + '%';
            document.getElementById('highestApy').textContent = metrics.highest_apy + '%';
            document.getElementById('marketTrend').textContent = metrics.market_trend;
        })
        .catch(() => {
            document.getElementById('totalOpps').textContent = '--';
            document.getElementById('avgApy').textContent = '--';
            document.getElementById('highestApy').textContent = '--';
            document.getElementById('marketTrend').textContent = '--';
        });

    fetchOpportunities();
}

function fetchOpportunities() {
    const body = document.getElementById('opportunitiesBody');
    body.innerHTML = '<div class="loading">Loading opportunities...</div>';

    fetch(API_BASE + '/api/v1/opportunities')
        .then(r => r.json())
        .then(data => {
            const opps = data.data.opportunities;
            if (!opps || opps.length === 0) {
                body.innerHTML = '<div class="loading">No opportunities available.</div>';
                return;
            }

            let html = '';
            opps.forEach(opp => {
                const riskClass = 'risk-' + (opp.risk || 'medium');
                html += `
                    <div class="opportunity-item">
                        <div class="opp-info">
                            <h4>${escapeHtml(opp.name || 'Unknown')}</h4>
                            <p>${escapeHtml(opp.protocol || 'Unknown')} | Min: $${opp.min_deposit || 0}</p>
                            <span class="opp-risk ${riskClass}">${opp.risk || 'medium'}</span>
                        </div>
                        <div class="opp-apy">${opp.apy || 0}%</div>
                    </div>
                `;
            });
            body.innerHTML = html;
        })
        .catch(err => {
            body.innerHTML = '<div class="loading">Failed to load opportunities. Please try again.</div>';
        });
}

function generateStrategy() {
    const result = document.getElementById('strategyResult');
    const amount = document.getElementById('amount').value;
    const risk = document.getElementById('risk').value;

    result.innerHTML = '<div class="loading">Generating strategy...</div>';

    fetch(API_BASE + '/api/v1/strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_profile: {
                amount: parseFloat(amount),
                risk_tolerance: risk,
                horizon: 'medium-term',
                preferred_protocols: ['OKX Earn', 'X Layer DEX']
            }
        })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) {
            result.innerHTML = 'Failed to generate strategy. Please try again.';
            return;
        }

        const rec = data.data.algorithmic_recommendation;
        const aiStrategy = data.data.ai_strategy;

        let html = '<div style="margin-bottom:16px;"><strong>AI Strategy:</strong></div>';
        html += '<div style="font-size:13px;margin-bottom:16px;color:#8892A8;">';
        html += escapeHtml(aiStrategy.ai_strategy || aiStrategy.ai_analysis || 'Analysis complete.');
        html += '</div>';

        if (rec && rec.diversification && rec.diversification.length > 0) {
            html += '<div style="margin-bottom:12px;"><strong>Recommended Allocation:</strong></div>';

            rec.diversification.forEach(item => {
                html += `
                    <div class="allocation-item">
                        <div class="alloc-header">
                            <span class="alloc-name">${escapeHtml(item.protocol)} - ${escapeHtml(item.product)}</span>
                            <span class="alloc-apy">${item.apy}% APY</span>
                        </div>
                        <div class="alloc-detail">
                            Invest: $${item.amount} | Est. Monthly: $${item.estimated_monthly_yield} | Risk: ${item.risk}
                        </div>
                    </div>
                `;
            });

            if (rec.estimated_monthly_yield) {
                html += `<div style="margin-top:12px;padding:10px;background:#0D1B2A;border-radius:6px;font-size:13px;">
                    <strong>Estimated Monthly Yield:</strong> $${rec.estimated_monthly_yield} |
                    <strong>Blended APY:</strong> ${rec.estimated_apy}%
                </div>`;
            }
        }

        result.innerHTML = html;
    })
    .catch(err => {
        result.innerHTML = 'Failed to generate strategy. Please try again.';
    });
}

function analyzeMarket() {
    const panel = document.getElementById('analysisPanel');
    const body = document.getElementById('analysisBody');
    panel.style.display = 'block';
    body.innerHTML = '<div class="loading">Analyzing market...</div>';

    fetch(API_BASE + '/api/v1/analyze')
        .then(r => r.json())
        .then(data => {
            if (!data.success) {
                body.innerHTML = 'Analysis failed. Please try again.';
                return;
            }

            const analysis = data.data.ai_analysis;
            const summary = analysis.market_summary || {};
            const recs = analysis.top_recommendations || [];

            let html = '<div style="margin-bottom:16px;"><strong>Market Summary</strong></div>';
            html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">';
            html += `<div style="padding:10px;background:#0D1B2A;border-radius:6px;">Avg APY: ${summary.average_apy || '--'}%</div>`;
            html += `<div style="padding:10px;background:#0D1B2A;border-radius:6px;">Highest: ${summary.highest_apy || '--'}%</div>`;
            html += `<div style="padding:10px;background:#0D1B2A;border-radius:6px;">Opportunities: ${summary.opportunity_count || '--'}</div>`;
            html += `<div style="padding:10px;background:#0D1B2A;border-radius:6px;">Sentiment: ${summary.market_sentiment || '--'}</div>`;
            html += '</div>';

            if (analysis.ai_analysis) {
                html += '<div style="margin-bottom:12px;"><strong>AI Analysis</strong></div>';
                html += '<div style="font-size:13px;color:#8892A8;padding:12px;background:#0D1B2A;border-radius:6px;line-height:1.6;">';
                html += escapeHtml(analysis.ai_analysis);
                html += '</div>';
            }

            body.innerHTML = html;
        })
        .catch(() => {
            body.innerHTML = 'Analysis failed. Please try again.';
        });
}

function closeAnalysis() {
    document.getElementById('analysisPanel').style.display = 'none';
}

function showStrategy() {
    document.getElementById('strategyPanel').scrollIntoView({ behavior: 'smooth' });
    document.getElementById('strategyPanel').style.borderColor = '#0052FF';
    setTimeout(() => {
        document.getElementById('strategyPanel').style.borderColor = '';
    }, 2000);
}

function askQuestion() {
    const input = document.getElementById('questionInput');
    const result = document.getElementById('qaResult');
    const question = input.value.trim();

    if (!question) {
        result.innerHTML = '<span style="color:#FF1744;">Please enter a question.</span>';
        return;
    }

    result.innerHTML = '<div class="loading">Thinking...</div>';

    fetch(API_BASE + '/api/v1/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            result.innerHTML = '<strong>Answer:</strong>\n\n' + escapeHtml(data.data.answer);
        } else {
            result.innerHTML = 'Failed to get answer. Please try again.';
        }
    })
    .catch(() => {
        result.innerHTML = 'Failed to get answer. Please try again.';
    });
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}