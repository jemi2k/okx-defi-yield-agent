/**
 * OKX DeFi Yield Optimizer - Wallet-first Autonomous Agent Dashboard
 */

var API = window.location.origin;
var WALLET_ADDRESS = null;
var WALLET_CHAIN_ID = null;

// ========== INIT ==========

document.addEventListener('DOMContentLoaded', function () {
    // Check if MetaMask is already connected
    if (typeof window.ethereum !== 'undefined') {
        window.ethereum.request({ method: 'eth_accounts' }).then(function (accounts) {
            if (accounts.length > 0) {
                onWalletConnected(accounts[0]);
                switchToXLayer();
            }
        });
    }
});

// ========== WALLET CONNECTION ==========

function connectWallet() {
    if (typeof window.ethereum === 'undefined') {
        alert('MetaMask is required. Please install MetaMask to use this application.');
        window.open('https://metamask.io/download/', '_blank');
        return;
    }

    window.ethereum.request({ method: 'eth_requestAccounts' })
        .then(function (accounts) {
            onWalletConnected(accounts[0]);
            switchToXLayer();
        })
        .catch(function (err) {
            if (err.code !== 4001) {
                console.error('Wallet connection failed:', err);
            }
        });
}

function switchToXLayer() {
    window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x7a0' }]
    }).catch(function () {
        return window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [{
                chainId: '0x7a0',
                chainName: 'X Layer Testnet',
                rpcUrls: ['https://testrpc.xlayer.tech/terigon'],
                nativeCurrency: { name: 'OKB', symbol: 'OKB', decimals: 18 },
                blockExplorerUrls: ['https://www.okx.com/web3/explorer/xlayer-test']
            }]
        });
    }).then(function () {
        if (WALLET_ADDRESS) updateWalletBalance();
    }).catch(function (err) {
        console.error('Network switch failed:', err);
    });
}

function onWalletConnected(address) {
    WALLET_ADDRESS = address;
    document.getElementById('connectSection').style.display = 'none';
    document.getElementById('dashboardSection').style.display = 'block';
    document.getElementById('btnConnectWallet').style.display = 'none';
    document.getElementById('walletInfo').style.display = 'block';
    document.getElementById('walletAddress').textContent = address.substring(0, 8) + '...' + address.substring(38);
    updateWalletBalance();
    loadInitialData();
}

function updateWalletBalance() {
    if (!WALLET_ADDRESS || typeof window.ethereum === 'undefined') return;
    window.ethereum.request({
        method: 'eth_getBalance',
        params: [WALLET_ADDRESS, 'latest']
    }).then(function (balance) {
        var okb = parseFloat(parseInt(balance, 16) / 1e18).toFixed(4);
        document.getElementById('statBalance').textContent = okb + ' OKB';
        document.getElementById('walletBalance').textContent = okb + ' OKB';
    });
}

// Listen for account/chain changes
if (typeof window.ethereum !== 'undefined') {
    window.ethereum.on('accountsChanged', function (accounts) {
        if (accounts.length === 0) {
            WALLET_ADDRESS = null;
            location.reload();
        } else {
            onWalletConnected(accounts[0]);
        }
    });
    window.ethereum.on('chainChanged', function () {
        updateWalletBalance();
    });
}

// ========== INITIAL DATA LOAD ==========

function loadInitialData() {
    loadAgentStatus();
    loadStats();
}

// ========== AGENT RUNTIME ==========

function runAgentScan() {
    var body = document.getElementById('agentBody');
    body.innerHTML = '<div class="loading">Agent scanning X Layer testnet strategies on-chain...</div>';
    document.getElementById('agentPulse').className = 'agent-pulse scanning';
    document.getElementById('agentStatusLabel').textContent = 'Scanning...';
    document.getElementById('statAgent').textContent = 'Scanning';

    fetch(API + '/api/v1/agent/scan')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) throw new Error('API error');
            renderAgentResults(data.data);
        })
        .catch(function () {
            body.innerHTML = '<div class="loading" style="color:#FF4757;">Agent scan failed. Retrying...</div>';
            setTimeout(runAgentScan, 3000);
        });
}

function loadAgentStatus() {
    fetch(API + '/api/v1/agent/status')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success && data.data.agent_status === 'active') {
                document.getElementById('agentPulse').className = 'agent-pulse active';
                document.getElementById('agentStatusLabel').textContent = 'Active - Monitoring X Layer';
                document.getElementById('statAgent').textContent = 'Active';
            }
        })
        .catch(function () {});
}

function renderAgentResults(data) {
    var body = document.getElementById('agentBody');
    var decision = data.agent_decision || {};
    var strategies = data.strategies || [];
    var best = data.best_strategy;

    document.getElementById('agentPulse').className = 'agent-pulse active';
    document.getElementById('agentStatusLabel').textContent = 'Active - Last scan: ' + (data.scan_time ? data.scan_time.substring(11, 19) : 'now');
    document.getElementById('statAgent').textContent = 'Active';
    document.getElementById('statStrategies').textContent = data.strategy_count;
    if (best) {
        document.getElementById('statBestApy').textContent = best.apy + '%';
    }

    var html = '';

    // Agent Decision
    html += '<div class="agent-decision-box">';
    html += '<div class="decision-label">Agent Decision</div>';
    html += '<div class="decision-reason" style="font-size:16px;font-weight:600;color:#E2E8F0;">' + esc(decision.action.replace(/_/g, ' ').toUpperCase()) + '</div>';
    html += '<div class="decision-reason" style="margin-top:4px;">' + esc(decision.reason || 'Monitoring market conditions.') + '</div>';
    html += '</div>';

    // Agent metrics
    html += '<div class="agent-status-bar">';
    html += '<div class="agent-metric"><div class="metric-label">Status</div><div class="metric-value" style="color:#00D67D;">ACTIVE</div></div>';
    html += '<div class="agent-metric"><div class="metric-label">Strategies On-Chain</div><div class="metric-value">' + data.strategy_count + '</div></div>';
    html += '<div class="agent-metric"><div class="metric-label">Average APY</div><div class="metric-value">' + data.average_apy + '%</div></div>';
    html += '<div class="agent-metric"><div class="metric-label">Best APY</div><div class="metric-value" style="color:#00D67D;">' + (best ? best.apy + '%' : '--') + '</div></div>';
    html += '</div>';

    // On-chain strategies table
    if (strategies.length > 0) {
        html += '<div style="margin:10px 0 6px;font-size:12px;color:#7B89A8;text-transform:uppercase;letter-spacing:0.6px;">Live On-Chain Strategies (X Layer Testnet)</div>';
        html += '<table class="allocation-table"><thead><tr><th>Strategy</th><th>Protocol</th><th>APY</th><th>Min Deposit</th><th>Risk</th></tr></thead><tbody>';
        strategies.forEach(function (s) {
            var isBest = best && s.id === best.id;
            var style = isBest ? ' style="border-left:3px solid #00D67D;"' : '';
            html += '<tr' + style + '>' +
                '<td>' + esc(s.name) + (isBest ? ' <span style="color:#00D67D;font-size:10px;">BEST</span>' : '') + '</td>' +
                '<td>' + esc(s.protocol) + '</td>' +
                '<td class="apy-cell">' + s.apy + '%</td>' +
                '<td>' + s.min_deposit + ' OKB</td>' +
                '<td><span class="rec-risk risk-' + (s.risk || 'medium') + '">' + s.risk + '</span></td>' +
                '</tr>';
        });
        html += '</tbody></table>';
    }

    html += '<div style="text-align:center;padding:10px;color:#7B89A8;font-size:12px;">';
    html += 'Agent continuously monitors YieldOptimizer.sol on X Layer Testnet. ';
    html += 'Auto-scans and re-evaluates strategies for optimal yield allocation.';
    html += '</div>';

    body.innerHTML = html;
}

// ========== STATS ==========

function loadStats() {
    fetch(API + '/api/v1/agent/status')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (data.success && data.data.recommendations) {
                var recs = data.data.recommendations;
                document.getElementById('statStrategies').textContent = recs.length;
                var best = recs.reduce(function (max, r) { return r.apy > max.apy ? r : max; }, recs[0]);
                if (best) document.getElementById('statBestApy').textContent = best.apy + '%';
            }
        })
        .catch(function () {});
}

// ========== STRATEGY GENERATOR ==========

function generateStrategy() {
    var result = document.getElementById('strategyResult');
    var amount = parseFloat(document.getElementById('amount').value) || 5000;
    var risk = document.getElementById('risk').value || 'moderate';

    result.style.display = 'block';
    result.innerHTML = '<div class="loading">Generating strategy from live on-chain data...</div>';

    fetch(API + '/api/v1/strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_profile: { amount: amount, risk_tolerance: risk, horizon: 'medium-term', preferred_protocols: ['OKX Earn', 'X Layer DEX'] }
        })
    })
    .then(function (r) { return r.json(); })
    .then(function (data) {
        if (!data.success) throw new Error('API error');
        renderStrategy(data.data, amount);
    })
    .catch(function () {
        result.innerHTML = '<div class="loading" style="color:#FF4757;">Failed to generate strategy.</div>';
    });
}

function renderStrategy(data, amount) {
    var result = document.getElementById('strategyResult');
    var rec = data.algorithmic_recommendation || {};
    var ai = data.ai_strategy || {};
    var div = rec.diversification || [];

    var html = '';
    if (ai.ai_strategy) {
        html += '<div class="ai-box"><div class="ai-label">AI Strategy</div><div class="ai-text">' + esc(ai.ai_strategy) + '</div></div>';
    }

    if (div.length > 0) {
        html += '<table class="allocation-table"><thead><tr><th>Protocol</th><th>Product</th><th>APY</th><th>Amount</th><th>Monthly</th><th>Risk</th></tr></thead><tbody>';
        div.forEach(function (item) {
            html += '<tr>' +
                '<td>' + esc(item.protocol) + '</td><td>' + esc(item.product) + '</td>' +
                '<td class="apy-cell">' + item.apy + '%</td><td class="amount-cell">$' + item.amount + '</td>' +
                '<td>$' + item.estimated_monthly_yield + '</td>' +
                '<td><span class="rec-risk risk-' + (item.risk || 'medium') + '">' + item.risk + '</span></td></tr>';
        });
        html += '</tbody></table>';

        html += '<div class="strategy-summary">';
        html += '<div class="summary-item"><div class="summary-label">Investment</div><div class="summary-value">$' + amount.toLocaleString() + '</div></div>';
        html += '<div class="summary-item"><div class="summary-label">Monthly Return</div><div class="summary-value" style="color:#00D67D;">$' + (rec.estimated_monthly_yield || 0) + '</div></div>';
        html += '<div class="summary-item"><div class="summary-label">Blended APY</div><div class="summary-value" style="color:#00D67D;">' + (rec.estimated_apy || 0) + '%</div></div>';
        html += '</div>';
    }

    result.innerHTML = html;
}

// ========== MARKET ANALYSIS ==========

function runAnalysis() {
    var loadingEl = document.getElementById('analysisLoading');
    var contentEl = document.getElementById('analysisContent');
    loadingEl.style.display = 'block';
    loadingEl.textContent = 'DeepSeek AI analyzing live X Layer data...';
    contentEl.style.display = 'none';

    fetch(API + '/api/v1/analyze')
        .then(function (r) { return r.json(); })
        .then(function (data) {
            if (!data.success) throw new Error('API error');
            loadingEl.style.display = 'none';
            contentEl.style.display = 'block';
            var a = data.data.ai_analysis || {};
            var s = a.market_summary || {};
            var recs = a.top_recommendations || [];
            var html = '';

            html += '<div class="market-overview-grid">';
            html += '<div class="metric-box"><div class="metric-label">Avg APY</div><div class="metric-value">' + (s.average_apy || '--') + '%</div></div>';
            html += '<div class="metric-box"><div class="metric-label">Highest APY</div><div class="metric-value">' + (s.highest_apy || '--') + '%</div></div>';
            html += '<div class="metric-box"><div class="metric-label">Sentiment</div><div class="metric-value" style="text-transform:capitalize;">' + (s.market_sentiment || 'neutral') + '</div></div>';
            html += '</div>';

            if (a.ai_analysis) {
                html += '<div class="ai-box"><div class="ai-label">AI Analysis</div><div class="ai-text">' + esc(a.ai_analysis) + '</div></div>';
            }

            if (recs.length > 0) {
                html += '<div class="rec-grid">';
                recs.forEach(function (r, i) {
                    html += '<div class="rec-card"><span class="rec-rank">#' + (i + 1) + '</span>' +
                        '<div class="rec-protocol">' + esc(r.protocol || 'Unknown') + '</div>' +
                        '<div class="rec-product">' + esc(r.name || '--') + '</div>' +
                        '<div class="rec-apy">' + r.apy + '%</div>' +
                        '<span class="rec-risk risk-' + (r.risk || 'medium') + '">' + r.risk + '</span></div>';
                });
                html += '</div>';
            }

            contentEl.innerHTML = html;
        })
        .catch(function () {
            loadingEl.textContent = 'Analysis failed. Please try again.';
        });
}

// ========== UTILS ==========

function esc(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
}