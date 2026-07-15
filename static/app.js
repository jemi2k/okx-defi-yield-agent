var API = location.origin;
var WALLET_ADDRESS = null;

(function init() {
    if (typeof ethereum !== 'undefined') {
        ethereum.request({ method: 'eth_accounts' }).then(function (a) {
            if (a.length > 0) { onWallet(a[0]); switchNet(); }
        });
    }
})();

// ========== WALLET ==========
function connectWallet() {
    if (typeof ethereum === 'undefined') { alert('MetaMask required'); open('https://metamask.io/download/'); return; }
    ethereum.request({ method: 'eth_requestAccounts' }).then(function (a) { onWallet(a[0]); switchNet(); }).catch(function () {});
}
function switchNet() {
    ethereum.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: '0x7a0' }] }).catch(function () {
        return ethereum.request({ method: 'wallet_addEthereumChain', params: [{ chainId: '0x7a0', chainName: 'X Layer Testnet', rpcUrls: ['https://testrpc.xlayer.tech/terigon'], nativeCurrency: { name: 'OKB', symbol: 'OKB', decimals: 18 }, blockExplorerUrls: ['https://www.okx.com/web3/explorer/xlayer-test'] }] });
    }).then(function () { if (WALLET_ADDRESS) updBal(); });
}
function onWallet(addr) {
    WALLET_ADDRESS = addr;
    gid('connectSection').style.display = 'none';
    gid('dashboardSection').style.display = 'block';
    gid('btnConnectWallet').style.display = 'none';
    var wi = gid('walletInfo'); if (wi) wi.style.display = 'block';
    gid('walletAddress').textContent = addr.substring(0, 8) + '...' + addr.substring(38);
    updBal(); loadInit();
}
function updBal() {
    if (!WALLET_ADDRESS) return;
    ethereum.request({ method: 'eth_getBalance', params: [WALLET_ADDRESS, 'latest'] }).then(function (b) {
        var okb = (parseInt(b, 16) / 1e18).toFixed(4);
        gid('statBalance').textContent = okb + ' OKB';
        gid('walletBalance').textContent = okb + ' OKB';
    });
}
if (typeof ethereum !== 'undefined') {
    ethereum.on('accountsChanged', function (a) { if (!a.length) location.reload(); else onWallet(a[0]); });
    ethereum.on('chainChanged', updBal);
}
function loadInit() { loadStatus(); loadStats(); }

// ========== AGENT ==========
function runAgentScan() {
    var body = gid('agentBody');
    body.innerHTML = '<div class="loading">Scanning X Layer testnet on-chain...</div>';
    gid('agentPulse').className = 'agent-pulse scanning';
    gid('agentStatusLabel').textContent = 'Scanning...';
    gid('statAgent').textContent = 'Scanning';
    fetch(API + '/api/v1/agent/scan')
        .then(r => r.json())
        .then(function (d) { if (!d.success) throw Error(); renderScan(d.data); })
        .catch(function () { body.innerHTML = '<div class="loading" style="color:#FF4757;">Failed. Retrying...</div>'; setTimeout(runAgentScan, 3000); });
}
function loadStatus() {
    fetch(API + '/api/v1/agent/status')
        .then(r => r.json())
        .then(function (d) { if (d.success && d.data.agent_status === 'active') { gid('agentPulse').className = 'agent-pulse active'; gid('agentStatusLabel').textContent = 'Active'; gid('statAgent').textContent = 'Active'; } })
        .catch(function () {});
}
function renderScan(data) {
    var body = gid('agentBody');
    var dec = data.agent_decision || {};
    var strs = data.strategies || [];
    var best = data.best_strategy;
    gid('agentPulse').className = 'agent-pulse active';
    gid('agentStatusLabel').textContent = 'Active - ' + (data.scan_time ? data.scan_time.substring(11, 19) : 'now');
    gid('statAgent').textContent = 'Active';
    gid('statStrategies').textContent = data.strategy_count;
    if (best) gid('statBestApy').textContent = best.apy + '%';

    var h = '';
    h += '<div class="agent-decision-box"><div class="decision-label">Agent Decision</div><div class="decision-reason" style="font-size:16px;font-weight:600;color:#E2E8F0;">' + esc(dec.action.replace(/_/g, ' ').toUpperCase()) + '</div><div class="decision-reason" style="margin-top:4px;">' + esc(dec.reason || 'Monitoring.') + '</div></div>';
    h += '<div class="agent-status-bar"><div class="agent-metric"><div class="metric-label">Status</div><div class="metric-value" style="color:#00D67D;">ACTIVE</div></div><div class="agent-metric"><div class="metric-label">Strategies</div><div class="metric-value">' + data.strategy_count + '</div></div><div class="agent-metric"><div class="metric-label">Avg APY</div><div class="metric-value">' + data.average_apy + '%</div></div><div class="agent-metric"><div class="metric-label">Best APY</div><div class="metric-value" style="color:#00D67D;">' + (best ? best.apy + '%' : '--') + '</div></div></div>';

    if (strs.length > 0) {
        h += '<div style="margin:10px 0 6px;font-size:12px;color:#7B89A8;text-transform:uppercase;letter-spacing:0.6px;">Live On-Chain Strategies (X Layer Testnet)</div><table class="allocation-table"><thead><tr><th>Strategy</th><th>Protocol</th><th>APY</th><th>Min Deposit</th><th>Risk</th></tr></thead><tbody>';
        strs.forEach(function (s) { var isB = best && s.id === best.id; h += '<tr' + (isB ? ' style="border-left:3px solid #00D67D;"' : '') + '><td>' + esc(s.name) + (isB ? ' <span style="color:#00D67D;font-size:10px;">BEST</span>' : '') + '</td><td>' + esc(s.protocol) + '</td><td class="apy-cell">' + s.apy + '%</td><td>' + s.min_deposit + ' OKB</td><td><span class="rec-risk risk-' + (s.risk || 'medium') + '">' + s.risk + '</span></td></tr>'; });
        h += '</tbody></table>';
    }

    // Execute button for best strategy
    if (best && dec.action === 'deposit_recommend') {
        h += '<div style="text-align:center;padding:16px 0 4px;"><button class="btn btn-primary btn-lg" onclick="executeBest(' + best.id + ',' + best.min_deposit + ')">Execute: Deposit into ' + esc(best.name) + '</button></div>';
        h += '<div style="text-align:center;padding:4px 0 8px;color:#7B89A8;font-size:12px;">Min deposit: ' + best.min_deposit + ' OKB. MetaMask confirmation required.</div>';
    }
    h += '<div style="text-align:center;padding:8px;color:#7B89A8;font-size:11px;">Agent monitors YieldOptimizer.sol on X Layer Testnet.</div>';
    body.innerHTML = h;
}

function executeBest(sid, minDep) {
    if (!WALLET_ADDRESS) { alert('Connect wallet first'); return; }
    var body = gid('agentBody');
    body.innerHTML = '<div class="loading">Building transaction...</div>';
    var addr = '0xE5B0F5e6F7358a8836574caEB6330DeDAf9E140C';
    var data = '0xb6b55f25' + sid.toString(16).padStart(64, '0');
    var val = '0x' + BigInt(Math.floor(minDep * 1e18)).toString(16);
    ethereum.request({ method: 'eth_sendTransaction', params: [{ from: WALLET_ADDRESS, to: addr, value: val, data: data, gas: '0x493E0' }] })
        .then(function (tx) { body.innerHTML = '<div class="agent-decision-box"><div class="decision-label">Transaction Sent</div><div class="decision-reason">TX: <a href="https://www.okx.com/web3/explorer/xlayer-test/tx/' + tx + '" target="_blank" style="color:#0052FF;">' + tx.substring(0, 14) + '...</a><br>Amount: ' + minDep + ' OKB into Strategy #' + sid + '</div></div>'; })
        .catch(function (e) { body.innerHTML = '<div class="loading" style="color:#FF4757;">Rejected: ' + esc(e.message) + '</div>'; });
}

// ========== STATS ==========
function loadStats() {
    fetch(API + '/api/v1/agent/status')
        .then(r => r.json())
        .then(function (d) { if (d.success && d.data.recommendations) { var recs = d.data.recommendations; gid('statStrategies').textContent = recs.length; var best = recs.reduce(function (m, r) { return r.apy > m.apy ? r : m; }, recs[0]); if (best) gid('statBestApy').textContent = best.apy + '%'; } })
        .catch(function () {});
}

// ========== STRATEGY ==========
function generateStrategy() {
    var res = gid('strategyResult');
    var amt = parseFloat(gid('amount').value) || 5000;
    var rsk = gid('risk').value || 'moderate';
    res.style.display = 'block';
    res.innerHTML = '<div class="loading">Generating...</div>';
    fetch(API + '/api/v1/strategy', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user_profile: { amount: amt, risk_tolerance: rsk, horizon: 'medium-term', preferred_protocols: ['OKX Earn', 'X Layer DEX'] } }) })
        .then(r => r.json())
        .then(function (d) { if (!d.success) throw Error(); renderStrategy(d.data, amt); })
        .catch(function () { res.innerHTML = '<div class="loading" style="color:#FF4757;">Failed</div>'; });
}
function renderStrategy(data, amount) {
    var res = gid('strategyResult');
    var rec = data.algorithmic_recommendation || {};
    var ai = data.ai_strategy || {};
    var div = rec.diversification || [];
    var h = '';
    if (ai.ai_strategy) h += '<div class="ai-box"><div class="ai-label">AI Strategy</div><div class="ai-text">' + md(ai.ai_strategy) + '</div></div>';
    if (div.length > 0) {
        h += '<table class="allocation-table"><thead><tr><th>Protocol</th><th>Product</th><th>APY</th><th>Amount</th><th>Monthly</th><th>Risk</th></tr></thead><tbody>';
        div.forEach(function (i) { h += '<tr><td>' + esc(i.protocol) + '</td><td>' + esc(i.product) + '</td><td class="apy-cell">' + i.apy + '%</td><td class="amount-cell">$' + i.amount + '</td><td>$' + i.estimated_monthly_yield + '</td><td><span class="rec-risk risk-' + (i.risk || 'medium') + '">' + i.risk + '</span></td></tr>'; });
        h += '</tbody></table>';
        h += '<div class="strategy-summary"><div class="summary-item"><div class="summary-label">Investment</div><div class="summary-value">$' + amount.toLocaleString() + '</div></div><div class="summary-item"><div class="summary-label">Monthly Return</div><div class="summary-value" style="color:#00D67D;">$' + (rec.estimated_monthly_yield || 0) + '</div></div><div class="summary-item"><div class="summary-label">Blended APY</div><div class="summary-value" style="color:#00D67D;">' + (rec.estimated_apy || 0) + '%</div></div></div>';
    }
    res.innerHTML = h;
}

// ========== ANALYSIS ==========
function runAnalysis() {
    var ld = gid('analysisLoading');
    var ct = gid('analysisContent');
    ld.style.display = 'block'; ld.textContent = 'DeepSeek AI analyzing X Layer...'; ct.style.display = 'none';
    fetch(API + '/api/v1/analyze')
        .then(r => r.json())
        .then(function (d) { if (!d.success) throw Error(); ld.style.display = 'none'; ct.style.display = 'block'; var a = d.data.ai_analysis || {}, s = a.market_summary || {}, recs = a.top_recommendations || []; var h = ''; h += '<div class="market-overview-grid"><div class="metric-box"><div class="metric-label">Avg APY</div><div class="metric-value">' + (s.average_apy || '--') + '%</div></div><div class="metric-box"><div class="metric-label">Highest APY</div><div class="metric-value">' + (s.highest_apy || '--') + '%</div></div><div class="metric-box"><div class="metric-label">Sentiment</div><div class="metric-value" style="text-transform:capitalize;">' + (s.market_sentiment || 'neutral') + '</div></div></div>'; if (a.ai_analysis) h += '<div class="ai-box"><div class="ai-label">AI Analysis</div><div class="ai-text">' + md(a.ai_analysis) + '</div></div>'; if (recs.length > 0) { h += '<div class="rec-grid">'; recs.forEach(function (r, i) { h += '<div class="rec-card"><span class="rec-rank">#' + (i + 1) + '</span><div class="rec-protocol">' + esc(r.protocol || '') + '</div><div class="rec-product">' + esc(r.name || '') + '</div><div class="rec-apy">' + r.apy + '%</div><span class="rec-risk risk-' + (r.risk || 'medium') + '">' + r.risk + '</span></div>'; }); h += '</div>'; } ct.innerHTML = h; })
        .catch(function () { ld.textContent = 'Failed.'; });
}

// ========== MARKDOWN ==========
function md(text) {
    if (!text) return '';
    var L = text.split('\n'), h = '', t = false, o = false, u = false;
    function close() { if (t) { h += '</tbody></table>'; t = false; } if (o) { h += '</ol>'; o = false; } if (u) { h += '</ul>'; u = false; } }
    for (var i = 0; i < L.length; i++) {
        var l = L[i].trim();
        if (!l) { close(); h += '<div style="height:6px;"></div>'; continue; }
        if (l.startsWith('### ')) { close(); h += '<h4 style="font-size:15px;font-weight:600;color:#E2E8F0;margin:16px 0 8px;">' + esc(l.slice(4)) + '</h4>'; continue; }
        if (l.startsWith('## ')) { close(); h += '<h3 style="font-size:17px;font-weight:700;color:#E2E8F0;margin:20px 0 10px;">' + esc(l.slice(3)) + '</h3>'; continue; }
        if (l.startsWith('# ')) { close(); h += '<h2 style="font-size:19px;font-weight:700;color:#E2E8F0;margin:24px 0 12px;">' + esc(l.slice(2)) + '</h2>'; continue; }
        if (l === '---') { close(); h += '<hr style="border:0;border-top:1px solid #1A2440;margin:14px 0;">'; continue; }
        if (l.startsWith('|') && !t) { var s = L[i + 1] ? L[i + 1].trim() : ''; if (s && s.startsWith('|') && s.indexOf('---') !== -1) { close(); t = true; var hdrs = l.split('|').filter(function (c) { return c.trim(); }); h += '<table style="width:100%;border-collapse:collapse;margin:10px 0;font-size:13px;"><thead><tr>'; hdrs.forEach(function (hd) { h += '<th style="text-align:left;padding:7px 10px;border-bottom:1px solid #1A2440;color:#7B89A8;font-weight:500;text-transform:uppercase;font-size:11px;letter-spacing:0.5px;">' + esc(hd.trim()) + '</th>'; }); h += '</tr></thead><tbody>'; i++; continue; } }
        if (t && l.startsWith('|')) { var cells = l.split('|').filter(function (c) { return c.trim(); }); h += '<tr>'; cells.forEach(function (c) { h += '<td style="padding:7px 10px;border-bottom:1px solid #1A2440;color:#E2E8F0;">' + bold(c.trim()) + '</td>'; }); h += '</tr>'; var nx = L[i + 1] ? L[i + 1].trim() : ''; if (!nx || !nx.startsWith('|')) { h += '</tbody></table>'; t = false; } continue; }
        var om = l.match(/^(\d+)[.)]\s+(.*)/);
        if (om) { if (u) { h += '</ul>'; u = false; } if (!o) { h += '<ol style="margin:6px 0;padding-left:24px;">'; o = true; } h += '<li style="margin-bottom:5px;line-height:1.6;">' + bold(om[2]) + '</li>'; continue; }
        if (l.startsWith('- ') || l.startsWith('* ')) { var c = l.startsWith('- ') ? l.slice(2) : l.slice(2); if (o) { h += '</ol>'; o = false; } if (!u) { h += '<ul style="margin:6px 0;padding-left:24px;">'; u = true; } h += '<li style="margin-bottom:5px;line-height:1.6;">' + bold(c) + '</li>'; continue; }
        if (l.startsWith('```')) { close(); h += '<pre style="background:#080C14;border:1px solid #1A2440;border-radius:8px;padding:14px 16px;margin:10px 0;font-size:12px;overflow-x:auto;font-family:monospace;color:#E2E8F0;">'; var j = i + 1; while (j < L.length && !L[j].trim().startsWith('```')) { h += esc(L[j]) + '\n'; j++; } i = j; h += '</pre>'; continue; }
        if (o) { h += '</ol>'; o = false; } if (u) { h += '</ul>'; u = false; }
        h += '<p style="margin:0 0 5px;line-height:1.7;">' + bold(l) + '</p>';
    }
    close();
    return h;
}
function bold(text) { return esc(text).replace(/\*\*(.*?)\*\*/g, '<strong style="color:#E2E8F0;">$1</strong>'); }
function esc(str) { if (!str) return ''; var d = document.createElement('div'); d.textContent = String(str); return d.innerHTML; }
function gid(id) { return document.getElementById(id); }