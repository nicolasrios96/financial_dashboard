/* ============================================================

 Financial Investment Dashboard JavaScript

 Supports: 200+ stocks, commodities, sell tracking, trade history,

 portfolio export/import, server sync, stock search, Gemini AI chat.

 ============================================================ */



// State

const dataLoaded = {};

let currentProfile = 'moderate';

let currentStrategy = 'best';

let sellTargetIndex = -1;

let chatOpen = false;

let searchTimeout = null;

let aiAvailable = false;
let currencyMode = localStorage.getItem('currency') || 'USD';
let eurRate = parseFloat(localStorage.getItem('eurRate')) || 0.92;

// Fetch EUR/USD rate on load
fetch('/api/search?ticker=EURUSD%3DX').then(r=>r.json()).then(j=>{
 if(j.status==='ok'&&j.data&&j.data.price){eurRate=round2(1/j.data.price);localStorage.setItem('eurRate',eurRate);}
}).catch(()=>{});
function round2(v){return Math.round(v*100)/100;}
function fmtMoney(v){if(v==null)return'?';v=parseFloat(v);if(isNaN(v))return'?';if(currencyMode==='EUR')return'€'+round2(v*eurRate).toLocaleString();return'$'+v.toLocaleString();}
function fmtMoneySign(v){if(v==null)return'?';v=parseFloat(v);if(isNaN(v))return'?';var sign=v>=0?'+':'';if(currencyMode==='EUR')return sign+'€'+round2(Math.abs(v)*eurRate).toLocaleString();return sign+'$'+Math.abs(v).toLocaleString();}
function fmtSymbol(){return currencyMode==='EUR'?'€':'$';}
function toDisplayVal(v){if(v==null)return v;v=parseFloat(v);if(isNaN(v))return v;return currencyMode==='EUR'?round2(v*eurRate):v;}
function toggleCurrency(){
 currencyMode=currencyMode==='USD'?'EUR':'USD';
 localStorage.setItem('currency',currencyMode);
 document.getElementById('currencyToggle').textContent=currencyMode==='USD'?'$ USD':'€ EUR';
 updateCurrencyLabels();
 showToast(currencyMode==='EUR'?'Showing EUR (rate: '+eurRate+')':'Showing USD','info');
 // Re-render all loaded sections
 if(lastActionsData)renderActions(lastActionsData);
 renderPortfolioList();
 if(lastPortfolioAnalysisData)renderPortfolioAnalysis(lastPortfolioAnalysisData.d,lastPortfolioAnalysisData.intel);
 if(lastTradeHistoryRendered)renderTradeHistory();
 if(lastGoalData)renderGoal(lastGoalData);
 if(lastCompoundHtml)calcCompoundRedraw();
 if(lastPortfolioTabData)renderPortfolio(lastPortfolioTabData);
 if(dataLoaded['market'])reRenderMarket();
 if(dataLoaded['commodities'])reRenderCommodities();
}
function updateCurrencyLabels(){
 var sym=fmtSymbol();
 document.querySelectorAll('.currency-label').forEach(function(el){el.textContent=sym;});
}
(function initCurrency(){document.getElementById('currencyToggle').textContent=currencyMode==='USD'?'$ USD':'€ EUR';})();

const COLORS = ['#448aff','#00c853','#ffd600','#ff6d00','#b388ff','#ff1744','#00bcd4','#8bc34a','#e91e63','#9c27b0','#009688','#ff5722'];

const COMMODITY_ICONS = {'Gold':'','Silver':'','Crude Oil (WTI)':'','Brent Crude':'','Natural Gas':'','Copper':'','Platinum':'','Palladium':'','Corn':'','Wheat':''};

const CRYPTO_ICONS = {'Bitcoin':'','Ethereum':'','Solana':'','Dogecoin':'','Ripple':''};
// Ticker type detection for badges
const COMMODITY_TICKERS = ['GLD','SLV','USO','PPLT','DBA','DBC','PDBC','COPX','UNG','WEAT','CORN','CPER','JO','GC=F','SI=F','CL=F','BZ=F','NG=F','HG=F','PL=F','PA=F','ZC=F','ZW=F','XAU','XAG','XPT','XPD','XAUUSD=X','XAGUSD=X','XPTUSD=X','XPDUSD=X','GOLD','SILVER'];
const CRYPTO_TICKERS = ['BTC-USD','ETH-USD','BNB-USD','SOL-USD','XRP-USD','ADA-USD','DOGE-USD','DOT-USD','AVAX-USD','MATIC-USD','LINK-USD','UNI-USD','ATOM-USD','LTC-USD','FIL-USD','NEAR-USD','APT-USD','ARB-USD','OP-USD','SUI-USD','AAVE-USD','MKR-USD','RENDER-USD','INJ-USD','FET-USD','COIN','HOOD'];
const EU_TICKER_SUFFIXES = ['.AS','.PA','.DE','.MC','.MI','.BR','.L','.CO','.ST','.SW'];
function getTickerBadge(ticker){
 ticker=ticker.toUpperCase();
 if(CRYPTO_TICKERS.includes(ticker)||ticker.endsWith('-USD'))return'<span class="badge badge-orange" style="font-size:0.55rem;margin-left:4px">₿ Crypto</span>';
 if(COMMODITY_TICKERS.includes(ticker)||ticker.endsWith('=F'))return'<span class="badge badge-yellow" style="font-size:0.55rem;margin-left:4px">🏆 Commodity</span>';
 for(var s of EU_TICKER_SUFFIXES)if(ticker.endsWith(s))return'<span class="badge badge-yellow" style="font-size:0.55rem;margin-left:4px">🇪🇺 EU</span>';
 return'<span class="badge badge-blue" style="font-size:0.55rem;margin-left:4px">🇺🇸 US</span>';
}




// Restore settings

(function restoreSettings() {

 const saved = localStorage.getItem('dashSettings');

 if (saved) { try { const s = JSON.parse(saved); if (s.investment) document.getElementById('actionInvestment').value = s.investment; if (s.strategy) currentStrategy = s.strategy; if (s.profile) currentProfile = s.profile; } catch(e) {} }

 // Restore AI settings

 const gk = localStorage.getItem('geminiApiKey');

 const gm = localStorage.getItem('geminiModel');

 const gp = localStorage.getItem('aiProvider') || 'groq';

 if (gk) document.getElementById('geminiApiKey').value = gk;

 if (gm) document.getElementById('geminiModel').value = gm;

 document.getElementById('aiProvider').value = gp;

 onProviderChange();

})();



let simpleMode = localStorage.getItem('simpleMode') !== 'false'; // Default: simple mode ON



function saveSettings() {

 localStorage.setItem('dashSettings', JSON.stringify({ investment: document.getElementById('actionInvestment').value, strategy: currentStrategy, profile: currentProfile }));

}



// ============================================================

// SIMPLE MODE Beginner-friendly view

// ============================================================

// Store last fetched data for re-rendering on mode switch

let lastActionsData = null;
let lastPortfolioAnalysisData = null;
let lastTradeHistoryRendered = false;
let lastGoalData = null;
let lastCompoundHtml = null;
let lastCompoundData = null;
let lastPortfolioTabData = null;
let lastMarketData = null;
let lastMoversData = null;
let lastCommoditiesData = null;
let lastCryptoData = null;



function toggleSimpleMode() {

 simpleMode = !simpleMode;

 localStorage.setItem('simpleMode', simpleMode);

 updateModeButton();

 document.body.classList.toggle('advanced-mode', !simpleMode);

 // Re-render with cached data (no re-fetch needed)

 if (lastActionsData) renderActions(lastActionsData);

 showToast(simpleMode ? ' Simple mode beginner-friendly view' : ' Advanced mode all technical details', 'info');

}



function updateModeButton() {

 const btn = document.getElementById('modeToggle');

 btn.textContent = simpleMode ? ' Simple' : ' Advanced';

 btn.title = simpleMode ? 'Switch to Advanced mode (show technical details)' : 'Switch to Simple mode (hide technical details)';

}



// Helper: convert score to simple label

function scoreToLabel(score) {

 if (score >= 50) return { text: 'Strong Buy ', cls: 'positive', emoji: '' };

 if (score >= 25) return { text: 'Good Buy ', cls: 'positive', emoji: '' };

 if (score >= 0) return { text: 'Okay to Hold ', cls: '', emoji: '' };

 if (score >= -25) return { text: 'Be Careful', cls: 'negative', emoji: '' };

 return { text: 'Avoid / Sell', cls: 'negative', emoji: '' };

}



// Helper: simple reason (no jargon)

function simpleReason(result) {

 const parts = [];

 if (result.pct_1w > 3) parts.push(`Going up (+${result.pct_1w.toFixed(1)}% this week)`);

 else if (result.pct_1w < -3) parts.push(`Going down (${result.pct_1w.toFixed(1)}% this week)`);

 if (result.trend === 'uptrend') parts.push('Steady upward trend');

 else if (result.trend === 'downtrend') parts.push('Downward trend risky');

 if (result.pct_from_high < -30) parts.push(`${Math.abs(result.pct_from_high).toFixed(0)}% below its peak`);

 if (result.score >= 40) parts.push('Multiple positive signals');

 else if (result.score <= -30) parts.push('Multiple warning signs');

 return parts.slice(0, 2).join(' ') || 'Mixed signals proceed with caution';

}



// Init mode

updateModeButton();

document.body.classList.toggle('advanced-mode', !simpleMode);



// ============================================================

// Toast

// ============================================================

function showToast(message, type = 'info') {

 const existing = document.querySelector('.toast'); if (existing) existing.remove();

 const toast = document.createElement('div'); toast.className = `toast ${type}`; toast.textContent = message;

 document.body.appendChild(toast); setTimeout(() => toast.remove(), 3000);

}



// ============================================================

// Tabs

// ============================================================

document.querySelectorAll('.tab').forEach(tab => {

 tab.addEventListener('click', () => {

 document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

 document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

 tab.classList.add('active');

 document.getElementById('panel-' + tab.dataset.tab).classList.add('active');

 loadTabData(tab.dataset.tab);

 });

});

function loadTabData(name) { if (dataLoaded[name]) return; switch(name) { case 'market': loadMarketData(); break; case 'commodities': loadCommodities(); break; } }



// ============================================================

// Utilities

// ============================================================

const cc = v => (v||0) >= 0 ? 'positive' : 'negative';

const ci = v => (v||0) >= 0 ? '' : '';

const fc = v => { v=v||0; return (v>=0?'+':'')+v.toFixed(2)+'%'; };

const ts = () => document.getElementById('lastUpdated').textContent = 'Updated: ' + new Date().toLocaleTimeString();

function urgencyBadge(u) { if (u==='Act now') return '<span class="urgency urgency-now"> Act now</span>'; if (u==='This week') return '<span class="urgency urgency-week"> This week</span>'; return '<span class="urgency urgency-later"> When convenient</span>'; }



// ============================================================
// SEARCH — Autocomplete while typing, Yahoo search on Enter/tap
// ============================================================

var acTimeout = null;

document.getElementById('searchInput').addEventListener('input', function() {
    clearTimeout(searchTimeout);
    clearTimeout(acTimeout);
    var val = this.value.trim();
    if (val.length < 1) { document.getElementById('searchResult').style.display = 'none'; return; }
    // Only show autocomplete suggestions while typing (no Yahoo fetch)
    acTimeout = setTimeout(function() { fetchAutocomplete(val); }, 150);
});

document.getElementById('searchInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        clearTimeout(searchTimeout);
        clearTimeout(acTimeout);
        var val = this.value.trim().toUpperCase();
        if (val) searchTicker(val);
    }
    if (e.key === 'Escape') {
        document.getElementById('searchResult').style.display = 'none';
        this.blur();
    }
});

document.addEventListener('click', function(e) { if (!e.target.closest('.search-bar')) document.getElementById('searchResult').style.display = 'none'; });

async function fetchAutocomplete(query) {
    try {
        var r = await fetch('/api/autocomplete?q=' + encodeURIComponent(query));
        var j = await r.json();
        if (j.status !== 'ok' || !j.results || j.results.length === 0) return;
        var el = document.getElementById('searchResult');
        el.style.display = 'block';
        var hasLocal = j.results.some(function(item) { return item.source === 'local'; });
        var hasYahoo = j.results.some(function(item) { return item.source === 'yahoo'; });
        var h = '<div class="ac-header">Suggestions (tap to search):</div>';
        var shownYahooHeader = false;
        j.results.forEach(function(item) {
            // Show a separator before Yahoo results
            if (item.source === 'yahoo' && !shownYahooHeader) {
                shownYahooHeader = true;
                if (hasLocal) h += '<div class="ac-divider">Yahoo Finance results:</div>';
            }
            var typeBadge = '';
            if (item.source === 'yahoo') {
                var typeLabel = item.type === 'etf' ? 'ETF' : item.type === 'cryptocurrency' ? 'Crypto' : item.type === 'mutualfund' ? 'Fund' : '';
                if (typeLabel) typeBadge = ' <span class="ac-type-badge">' + typeLabel + '</span>';
            }
            h += '<div class="ac-item" onclick="selectAutocomplete(\'' + item.ticker + '\')">';
            h += '<div><strong class="ac-ticker">' + item.ticker + '</strong>';
            h += ' <span class="ac-name">' + item.name + '</span>' + typeBadge + '</div>';
            h += '<span class="ac-action">' + (item.source === 'yahoo' ? '🌐 Search ›' : 'Search ›') + '</span>';
            h += '</div>';
        });
        el.innerHTML = h;
    } catch(e) {}
}

function selectAutocomplete(ticker) {
    clearTimeout(searchTimeout);
    clearTimeout(acTimeout);
    document.getElementById('searchInput').value = ticker;
    searchTicker(ticker);
}



async function searchTicker(ticker) {

 const el = document.getElementById('searchResult');

 el.style.display = 'block';

 el.innerHTML = '<div style="text-align:center;padding:20px;color:var(--text-muted)"><div class="spinner" style="display:inline-block;width:24px;height:24px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin 0.8s linear infinite"></div><br>Searching ' + ticker + '...</div>';

 try {

 const r = await fetch(`/api/search?ticker=${encodeURIComponent(ticker)}`);

 const j = await r.json();

 if (j.status !== 'ok') { el.innerHTML = `<div style="color:var(--red);padding:8px">${j.message}</div>`; return; }

 renderSearchResult(j.data);

 } catch(e) { el.innerHTML = `<div style="color:var(--red);padding:8px">Error: ${e.message}</div>`; }

}



function renderSearchResult(d) {

 const el = document.getElementById('searchResult');

 const scoreClass = d.score >= 25 ? 'badge-green' : d.score >= 0 ? 'badge-yellow' : 'badge-red';

 const trendIcon = d.trend === 'uptrend' ? '' : d.trend === 'downtrend' ? '' : '';

 // Analyst data
 const a = d.analyst || {};
 let analystHtml = '';
 if (a.analyst_total) {
  const buyW = a.analyst_buy_pct || 0;
  const holdW = a.analyst_hold_pct || 0;
  const sellW = a.analyst_sell_pct || 0;
  analystHtml = `<div style="margin-top:10px;padding:10px 12px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:8px">
   <div style="font-size:0.75rem;font-weight:600;margin-bottom:6px">📊 Analyst Consensus (${a.analyst_total} analysts)</div>
   <div style="display:flex;height:20px;border-radius:4px;overflow:hidden;margin-bottom:6px">
    ${buyW > 0 ? `<div style="width:${buyW}%;background:var(--green);display:flex;align-items:center;justify-content:center;font-size:0.6rem;color:#fff;font-weight:700">${buyW > 10 ? Math.round(buyW)+'%' : ''}</div>` : ''}
    ${holdW > 0 ? `<div style="width:${holdW}%;background:var(--yellow);display:flex;align-items:center;justify-content:center;font-size:0.6rem;color:#000;font-weight:700">${holdW > 10 ? Math.round(holdW)+'%' : ''}</div>` : ''}
    ${sellW > 0 ? `<div style="width:${sellW}%;background:var(--red);display:flex;align-items:center;justify-content:center;font-size:0.6rem;color:#fff;font-weight:700">${sellW > 10 ? Math.round(sellW)+'%' : ''}</div>` : ''}
   </div>
   <div style="display:flex;gap:12px;font-size:0.7rem;color:var(--text-secondary)">
    <span style="color:var(--green)">🟢 Buy ${Math.round(buyW)}%</span>
    <span style="color:var(--yellow)">🟡 Hold ${Math.round(holdW)}%</span>
    <span style="color:var(--red)">🔴 Sell ${Math.round(sellW)}%</span>
   </div>
   <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px;font-size:0.7rem">
    ${a.target_mean ? `<span>🎯 Target: <strong>${fmtMoney(a.target_mean)}</strong> <span class="${(a.target_upside_pct||0)>=0?'positive':'negative'}">(${a.target_upside_pct>=0?'+':''}${a.target_upside_pct}%)</span></span>` : ''}
    ${a.target_high ? `<span style="color:var(--text-tertiary)">High: ${fmtMoney(a.target_high)}</span>` : ''}
    ${a.target_low ? `<span style="color:var(--text-tertiary)">Low: ${fmtMoney(a.target_low)}</span>` : ''}
   </div>
   <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;font-size:0.65rem;color:var(--text-tertiary)">
    ${a.forward_pe ? `<span>Fwd P/E: <strong>${a.forward_pe}</strong></span>` : ''}
    ${a.trailing_pe ? `<span>Trail P/E: ${a.trailing_pe}</span>` : ''}
    ${a.peg_ratio ? `<span>PEG: ${a.peg_ratio}</span>` : ''}
    ${a.earnings_growth_pct != null ? `<span>EPS Growth: <strong class="${a.earnings_growth_pct>=0?'positive':'negative'}">${a.earnings_growth_pct>=0?'+':''}${a.earnings_growth_pct}%</strong></span>` : ''}
    ${a.revenue_growth_pct != null ? `<span>Rev Growth: <strong class="${a.revenue_growth_pct>=0?'positive':'negative'}">${a.revenue_growth_pct>=0?'+':''}${a.revenue_growth_pct}%</strong></span>` : ''}
   </div>
   ${d.analyst_adjustment ? `<div style="font-size:0.65rem;color:var(--accent);margin-top:4px">Score adjusted ${d.analyst_adjustment>0?'+':''}${d.analyst_adjustment} based on analyst consensus</div>` : ''}
  </div>`;
 }

 let h = `<div class="search-stock-card">

 <div class="stock-main">

 <h3><span class="ticker">${d.ticker}</span> ${d.name} <span class="badge ${d.market==='US'?'badge-blue':d.market==='EU'?'badge-yellow':'badge-orange'}" style="font-size:0.6rem">${d.market}</span></h3>

 <div style="font-size:0.85rem;margin-top:4px">

 <span class="badge ${scoreClass}">Score: ${d.score}</span>

 <span style="margin-left:8px">${d.action}</span>

 <span style="margin-left:8px">${trendIcon} ${d.trend}</span>

 </div>

 <div class="stock-metrics">

 <div class="metric">RSI: <strong>${d.rsi}</strong></div>

 <div class="metric">Week: <strong class="${cc(d.pct_1w)}">${fc(d.pct_1w)}</strong></div>

 <div class="metric">Month: <strong class="${cc(d.pct_1m)}">${fc(d.pct_1m)}</strong></div>

 ${d.pct_3m != null ? `<div class="metric">3M: <strong class="${cc(d.pct_3m)}">${fc(d.pct_3m)}</strong></div>` : ''}

 ${d.sma_200 ? `<div class="metric">SMA200: <strong>${fmtMoney(d.sma_200)}</strong></div>` : ''}

 <div class="metric">From High: <strong class="${cc(d.pct_from_high)}">${fc(d.pct_from_high)}</strong></div>

 </div>
 ${analystHtml}

 </div>

 <div class="stock-price">

 <div class="price">${d.price != null ? fmtMoney(d.price) : '🔒 Market Closed'}</div>

 <div class="${cc(d.daily_change)}" style="font-size:0.9rem;font-weight:600">${ci(d.daily_change)} ${fc(d.daily_change)}</div>

 <div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px">

 ${fmtMoney(d.target_price)}<br> ${fmtMoney(d.stop_loss)}

 </div>

 </div>

 </div>

 <div style="display:flex;gap:8px;margin-top:12px;border-top:1px solid var(--border);padding-top:12px">

 <button class="btn" style="font-size:0.8rem" onclick="addFromSearch('${d.ticker}',${d.price})"> Add to Portfolio</button>

 <button class="btn" style="font-size:0.8rem" onclick="askAIAbout('${d.ticker}')"> Ask AI about ${d.ticker}</button>

 </div>`;

 el.innerHTML = h;

}



function addFromSearch(ticker, price) {

 myPortfolio.push({ ticker, shares: 1, buy_price: price, buy_date: new Date().toISOString().split('T')[0] });

 savePortfolio(); renderPortfolioList();

 showToast(`Added 1 share of ${ticker} at $${price}`, 'success');

 document.getElementById('searchResult').style.display = 'none';

}



// ============================================================

// SETTINGS Gemini API

// ============================================================

function openSettings() { document.getElementById('settingsModal').style.display = 'flex'; }

function closeSettings() { document.getElementById('settingsModal').style.display = 'none'; }

document.getElementById('settingsModal').addEventListener('click', function(e) { if (e.target === this) closeSettings(); });



function toggleKeyVisibility() {

 const inp = document.getElementById('geminiApiKey');

 inp.type = inp.type === 'password' ? 'text' : 'password';

}



// Provider change handler

function onProviderChange() {

 const provider = document.getElementById('aiProvider').value;

 const modelSelect = document.getElementById('geminiModel');

 const helpEl = document.getElementById('providerHelp');



 if (provider === 'groq') {

 modelSelect.innerHTML = `

 <option value="llama-3.3-70b-versatile">Llama 3.3 70B (best, free)</option>

 <option value="llama-3.1-8b-instant">Llama 3.1 8B (fastest, free)</option>

 <option value="mixtral-8x7b-32768">Mixtral 8x7B (good, free)</option>

 <option value="gemma2-9b-it">Gemma 2 9B (Google, free)</option>`;

 helpEl.innerHTML = 'Get a free API key at <a href="https://console.groq.com" target="_blank" style="color:var(--accent)">console.groq.com</a> sign up with Google, no billing required. Works in EU.';

 } else {

 modelSelect.innerHTML = `

 <option value="gemini-2.0-flash">Gemini 2.0 Flash (fast)</option>

 <option value="gemini-2.0-flash-lite">Gemini 2.0 Flash Lite (fastest)</option>

 <option value="gemini-1.5-flash">Gemini 1.5 Flash (stable)</option>

 <option value="gemini-1.5-pro-latest">Gemini 1.5 Pro (best, paid)</option>`;

 helpEl.innerHTML = 'Get an API key at <a href="https://aistudio.google.com/apikey" target="_blank" style="color:var(--accent)">aistudio.google.com/apikey</a>. Free tier may not work in EU enable billing if needed.';

 }

 // Restore saved model if it matches

 const savedModel = localStorage.getItem('geminiModel');

 if (savedModel) { const opt = modelSelect.querySelector(`option[value="${savedModel}"]`); if (opt) modelSelect.value = savedModel; }

}



function saveGeminiSettings() {

 const key = document.getElementById('geminiApiKey').value.trim();

 const model = document.getElementById('geminiModel').value;

 const provider = document.getElementById('aiProvider').value;

 if (key) localStorage.setItem('geminiApiKey', key);

 else localStorage.removeItem('geminiApiKey');

 localStorage.setItem('geminiModel', model);

 localStorage.setItem('aiProvider', provider);

 closeSettings();

 showToast('Settings saved!', 'success');

}



async function testAIKey() {

 const key = document.getElementById('geminiApiKey').value.trim();

 const model = document.getElementById('geminiModel').value;

 const provider = document.getElementById('aiProvider').value;

 const el = document.getElementById('geminiTestResult');

 if (!key) { el.innerHTML = '<span style="color:var(--red)"> No key entered</span>'; return; }

 el.innerHTML = '<span style="color:var(--text-muted)">Testing...</span>';

 try {

 let r;

 if (provider === 'groq') {

 r = await fetch('https://api.groq.com/openai/v1/chat/completions', {

 method: 'POST',

 headers: {'Content-Type':'application/json', 'Authorization': `Bearer ${key}`},

 body: JSON.stringify({model: model, messages:[{role:'user',content:"Say OK"}], max_tokens: 5})

 });

 } else {

 r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`, {

 method: 'POST', headers: {'Content-Type':'application/json'},

 body: JSON.stringify({contents:[{parts:[{text:"Say OK"}]}]})

 });

 }

 if (r.ok) { el.innerHTML = '<span style="color:var(--green)"> Connected!</span>'; }

 else {

 const j = await r.json();

 const msg = j.error?.message || 'Failed';

 if (msg.includes('quota') || msg.includes('Quota')) {

 el.innerHTML = `<span style="color:var(--red)"> Quota exceeded. Try Groq provider instead (free, works in EU).</span>`;

 } else if (msg.includes('not found') || msg.includes('not supported')) {

 el.innerHTML = `<span style="color:var(--red)"> Model not available. Try a different model.</span>`;

 } else if (msg.includes('Invalid API Key') || msg.includes('invalid_api_key')) {

 el.innerHTML = `<span style="color:var(--red)"> Invalid API key. Check and try again.</span>`;

 } else {

 el.innerHTML = `<span style="color:var(--red)"> ${msg}</span>`;

 }

 }

 } catch(e) { el.innerHTML = `<span style="color:var(--red)"> ${e.message}</span>`; }

}



// ============================================================

// CHAT Gemini AI

// ============================================================

let chatHistory = [];



function toggleChat() {

 chatOpen = !chatOpen;

 document.getElementById('chatPanel').style.display = chatOpen ? 'flex' : 'none';

 document.getElementById('chatToggle').style.display = chatOpen ? 'none' : 'flex';

 if (chatOpen) document.getElementById('chatInput').focus();

}



function sendQuickPrompt(text) {

 document.getElementById('chatInput').value = text;

 sendChat();

}



function askAIAbout(ticker) {

 if (!chatOpen) toggleChat();

 document.getElementById('chatInput').value = `Should I buy ${ticker}? Analyze it for me.`;

 sendChat();

}



async function sendChat() {

 const input = document.getElementById('chatInput');

 const msg = input.value.trim();

 if (!msg) return;

 input.value = '';



 const messagesEl = document.getElementById('chatMessages');

 messagesEl.innerHTML += `<div class="chat-msg user">${escapeHtml(msg)}</div>`;

 messagesEl.innerHTML += `<div class="chat-msg ai loading" id="chatLoading"> Thinking...</div>`;

 messagesEl.scrollTop = messagesEl.scrollHeight;



 try {

 // Send to server-side chat endpoint (uses GROQ_API_KEY on server)

 const r = await fetch('/api/chat', {

 method: 'POST',

 headers: {'Content-Type':'application/json'},

 body: JSON.stringify({

 message: msg,

 history: chatHistory.slice(-10),

 holdings: myPortfolio,

 trade_history: myTradeHistory,

 })

 });

 const j = await r.json();



 let reply = '';

 if (j.status === 'ok' && j.reply) {

 reply = j.reply;

 } else if (j.message) {

 reply = ` ${j.message}`;

 } else {

 reply = ' No response. Try again.';

 }



 // Store in history for context

 chatHistory.push({role: 'user', content: msg});

 chatHistory.push({role: 'assistant', content: reply});



 const loadingEl = document.getElementById('chatLoading');

 if (loadingEl) loadingEl.outerHTML = `<div class="chat-msg ai">${formatChatResponse(reply)}</div>`;



 } catch(e) {

 const loadingEl = document.getElementById('chatLoading');

 if (loadingEl) loadingEl.outerHTML = `<div class="chat-msg ai"> Error: ${e.message}</div>`;

 }



 messagesEl.scrollTop = messagesEl.scrollHeight;

}



function escapeHtml(text) { const d = document.createElement('div'); d.textContent = text; return d.innerHTML; }



function formatChatResponse(text) {

 // Basic markdown-like formatting

 return text

 .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')

 .replace(/\*(.*?)\*/g, '<em>$1</em>')

 .replace(/`(.*?)`/g, '<code style="background:var(--bg);padding:2px 6px;border-radius:4px">$1</code>')

 .replace(/\n/g, '<br>');

}



// Keyboard shortcuts

document.addEventListener('keydown', function(e) {

 if ((e.ctrlKey || e.metaKey) && e.key === '/') { e.preventDefault(); toggleChat(); }

 if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); document.getElementById('searchInput').focus(); }

 if (e.key === 'Escape') {

 if (chatOpen) toggleChat();

 document.getElementById('searchResult').style.display = 'none';

 closeSettings(); closeSellModal();

 }

});



// ============================================================

// TODAY'S ACTIONS

// ============================================================

function selectStrategy(strategy, btn) { currentStrategy = strategy; document.querySelectorAll('.strategy-btn').forEach(b => b.classList.remove('active')); btn.classList.add('active'); }



async function loadTodaysActions() {
 const investment = document.getElementById('actionInvestment').value || 1000;
 const el = document.getElementById('actionsContent');
 saveSettings();

 // --- STEP 1: Show cached data instantly (if available) ---
 const cacheKey = 'cachedActions_' + investment + '_' + currentStrategy;
 const cached = localStorage.getItem(cacheKey);
 let showedCache = false;
 if (cached) {
  try {
   const cachedData = JSON.parse(cached);
   const age = Date.now() - (cachedData._cachedAt || 0);
   const ageMin = Math.round(age / 60000);
   if (age < 3600000) { // Show cache if less than 1 hour old
    renderActions(cachedData);
    showedCache = true;
    // Add "refreshing" banner at top
    const banner = document.createElement('div');
    banner.id = 'refreshBanner';
    banner.style.cssText = 'padding:8px 14px;background:var(--blue-bg);border:1px solid rgba(0,122,255,0.2);border-radius:8px;margin-bottom:10px;font-size:0.75rem;color:var(--blue);display:flex;align-items:center;gap:8px';
    banner.innerHTML = '<div class="spinner" style="width:14px;height:14px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin 0.8s linear infinite;flex-shrink:0"></div> Showing data from ' + ageMin + ' min ago — refreshing with latest prices...';
    el.prepend(banner);
   }
  } catch(e) {}
 }

 // --- STEP 2: If no cache, show progress steps ---
 if (!showedCache) {
  el.innerHTML = '<div class="loading" id="loadingProgress">' +
   '<div class="spinner"></div><br>' +
   '<div id="loadStep" style="font-size:0.85rem;color:var(--text-secondary)">📡 Connecting to market data...</div>' +
   '<div style="margin-top:12px;font-size:0.7rem;color:var(--text-tertiary)">This takes 15-30s on first load (500+ stocks to scan)</div>' +
   '</div>';
  // Simulate progress steps
  setTimeout(() => { const s = document.getElementById('loadStep'); if (s) s.innerHTML = '📊 Fetching US & EU stock data...'; }, 3000);
  setTimeout(() => { const s = document.getElementById('loadStep'); if (s) s.innerHTML = '🧮 Running technical analysis on 500+ stocks...'; }, 8000);
  setTimeout(() => { const s = document.getElementById('loadStep'); if (s) s.innerHTML = '🎯 Selecting best picks for your strategy...'; }, 15000);
  setTimeout(() => { const s = document.getElementById('loadStep'); if (s) s.innerHTML = '⏳ Almost done — finalizing recommendations...'; }, 25000);
 }

 // --- STEP 3: Fetch market indices quickly (show at top) ---
 if (!showedCache) {
  fetch('/api/market-overview').then(r => r.json()).then(j => {
   if (j.status === 'ok' && j.data) {
    const indices = [...(j.data.us || []), ...(j.data.eu || [])];
    if (indices.length > 0 && document.getElementById('loadingProgress')) {
     const quickBar = document.createElement('div');
     quickBar.style.cssText = 'display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:16px;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:10px';
     indices.slice(0, 6).forEach(idx => {
      const cls = idx.change >= 0 ? 'positive' : 'negative';
      const sign = idx.change >= 0 ? '+' : '';
      quickBar.innerHTML += '<div style="text-align:center;min-width:80px"><div style="font-size:0.6rem;color:var(--text-tertiary)">' + idx.name + '</div><div style="font-size:0.8rem;font-weight:700">' + idx.price.toLocaleString() + '</div><div class="' + cls + '" style="font-size:0.7rem;font-weight:600">' + sign + idx.change.toFixed(2) + '%</div></div>';
     });
     const lp = document.getElementById('loadingProgress');
     if (lp) lp.parentNode.insertBefore(quickBar, lp);
    }
   }
  }).catch(() => {});
 }

 // --- STEP 4: Fetch full analysis ---
 try {
  const [actionsRes, regimeRes] = await Promise.all([
   fetch('/api/todays-actions?investment=' + investment + '&strategy=' + currentStrategy),
   fetch('/api/market-regime').catch(() => null)
  ]);
  const j = await actionsRes.json();
  if (j.status !== 'ok') throw new Error(j.message);

  let regimeData = null;
  if (regimeRes) {
   try { const rj = await regimeRes.json(); if (rj.status === 'ok') regimeData = rj.data; } catch(e) {}
  }
  j.data.market_regime = regimeData;

  // Cache results for next visit
  j.data._cachedAt = Date.now();
  try { localStorage.setItem(cacheKey, JSON.stringify(j.data)); } catch(e) {}

  renderActions(j.data); dataLoaded['actions'] = true; ts();
 } catch(e) {
  if (!showedCache) {
   el.innerHTML = '<div class="error-msg">❌ ' + e.message + '<br><br><button class="btn" onclick="loadTodaysActions()">🔄 Try Again</button></div>';
  } else {
   // Remove refresh banner, keep cached data
   const banner = document.getElementById('refreshBanner');
   if (banner) banner.innerHTML = '⚠️ Could not refresh — showing cached data. <button class="btn" style="font-size:0.7rem;padding:3px 8px;margin-left:8px" onclick="loadTodaysActions()">Retry</button>';
  }
 }
}



function renderActions(d) {

 lastActionsData = d; // Cache for mode toggle re-render

 const el = document.getElementById('actionsContent');

 const sm = simpleMode;

 // Market regime banner

 let h = '';

 if (d.market_regime && d.market_regime.regime !== 'unknown') {

 const mr = d.market_regime;

 const regimeColors = {bull:'green',bear:'red',correction:'yellow',sideways:'yellow'};

 const regimeIcons = {bull:'',bear:'',correction:'',sideways:''};

 h += `<div class="sentiment-bar ${regimeColors[mr.regime]||'yellow'}" style="margin-bottom:8px">

 <strong>${regimeIcons[mr.regime]||''} Market: ${mr.regime.toUpperCase()}</strong> ${mr.description}

 <span style="margin-left:auto;font-size:0.75rem">S&P 500: ${fmtMoney(mr.sp500_price)} (${mr.sp500_1m>=0?'+':''}${mr.sp500_1m}% 1M)</span>

 </div>`;

 if (!simpleMode) h += `<div style="font-size:0.8rem;color:var(--text-muted);margin-bottom:12px;padding:0 4px"> Strategy: ${mr.strategy_hint}</div>`;

 }

 h += `<div class="sentiment-bar ${d.sentiment.color}"><strong>${d.sentiment.label}</strong> ${d.sentiment.desc}<span style="margin-left:auto;font-size:0.8rem">${d.strategy_label} ${fmtMoney(d.investment)}</span></div>`;
 if (d.fallback_note) h += `<div style="padding:10px 16px;background:var(--yellow-bg);border:1px solid rgba(255,214,0,0.3);border-radius:8px;margin-bottom:12px;font-size:0.8rem;color:var(--yellow)">${d.fallback_note}</div>`;

 if (d.actions.length > 0) {

 h += `<div style="margin-bottom:8px;font-size:0.9rem;color:var(--text-muted)"> <strong style="color:var(--green)">BUY</strong> Your investment plan:</div>`;

 d.actions.forEach(a => {

 const label = scoreToLabel(a.score);

 const reasonText = sm ? simpleReason(a) : a.reason;

 h += `<div class="action-card buy">

 <div class="action-badge buy">BUY</div>

 <div class="action-info">

 <h3><span class="ticker">${a.ticker}</span> ${a.name} <span class="badge ${a.market==='US'?'badge-blue':'badge-yellow'}" style="font-size:0.6rem">${a.market}</span>

 ${sm ? ` <span class="badge ${label.cls === 'positive' ? 'badge-green' : 'badge-yellow'}" style="font-size:0.65rem">${label.text}</span>` : ''}

 </h3>

 <div class="meta">

 <span>${a.hold_label}</span>

 <span>${urgencyBadge(a.urgency)}</span>

 <span>${fmtMoney(a.price)}/share</span>

 ${!sm ? `<span style="color:var(--text-muted)">Score: ${a.score} RSI: ${a.rsi}</span>` : ''}

 </div>

 <div class="reason"> ${reasonText}</div>
 ${a.analyst && a.analyst.analyst_total ? `<div style="margin-top:4px;font-size:0.7rem;color:var(--text-secondary)">📊 Analysts (${a.analyst.analyst_total}): <span style="color:var(--green)">${Math.round(a.analyst.analyst_buy_pct||0)}% Buy</span> · <span style="color:var(--yellow)">${Math.round(a.analyst.analyst_hold_pct||0)}% Hold</span> · <span style="color:var(--red)">${Math.round(a.analyst.analyst_sell_pct||0)}% Sell</span>${a.analyst.target_mean ? ` · 🎯 Target: ${fmtMoney(a.analyst.target_mean)} <span class="${(a.analyst.target_upside_pct||0)>=0?'positive':'negative'}">(${(a.analyst.target_upside_pct||0)>=0?'+':''}${a.analyst.target_upside_pct}%)</span>` : ''}${a.analyst.forward_pe ? ` · P/E: ${a.analyst.forward_pe}` : ''}</div>` : ''}

 </div>

 <div class="action-numbers">

 <div class="invest-amt">${fmtMoney(a.invest_amount)}</div>

 <div class="shares">${a.shares.toFixed(4)} shares</div>

 ${!sm ? `<div class="targets"><span class="target-up"> ${fmtMoney(a.target_price)} (+${a.potential_gain_pct}%)</span><span class="target-down"> ${fmtMoney(a.stop_loss)} (${a.potential_loss_pct}%)</span></div>` : `<div style="font-size:0.8rem;color:var(--green);margin-top:4px">Potential: +${a.potential_gain_pct}%</div>`}

 </div>

 </div>`;

 });

 } else { h += '<div style="padding:20px;text-align:center;color:var(--text-muted)">No strong buy signals right now. Consider holding cash or check the Portfolios tab.</div>'; }

 if (d.sell_alerts.length > 0) {

 h += `<div style="margin:20px 0 8px;font-size:0.9rem;color:var(--text-muted)"> <strong style="color:var(--red)">SELL / AVOID</strong> Stay away from these:</div>`;

 d.sell_alerts.forEach(s => {

 const cls = s.action==='SELL'?'sell':'avoid';

 h += `<div class="action-card ${cls}">

 <div class="action-badge ${cls}">${s.action}</div>

 <div class="action-info">

 <h3><span class="ticker">${s.ticker}</span> ${s.name}</h3>

 <div class="meta">

 <span>${urgencyBadge(s.urgency)}</span>

 <span class="${cc(s.pct_1w)}">Week: ${fc(s.pct_1w)}</span>

 ${!sm ? `<span class="${cc(s.pct_1m)}">Month: ${fc(s.pct_1m)}</span>` : ''}

 </div>

 <div class="reason"> ${s.reason}</div>

 </div>

 <div class="action-numbers"><div style="font-size:1rem;color:var(--text-muted)">${fmtMoney(s.price)}</div></div>

 </div>`;

 });

 }

 if (d.cash_remaining > 0.01) h += `<div style="padding:12px;background:var(--bg);border:1px solid var(--border);border-radius:10px;font-size:0.85rem;color:var(--text-muted);margin-top:12px"> Cash remaining: <strong style="color:var(--text)">${fmtMoney(d.cash_remaining)}</strong></div>`;

 el.innerHTML = h;

}



// ============================================================

// MY PORTFOLIO

// ============================================================

let myPortfolio = []; let myTradeHistory = [];

try { const s = localStorage.getItem('myPortfolio'); if (s) myPortfolio = JSON.parse(s); } catch(e) {}

try { const s = localStorage.getItem('myTradeHistory'); if (s) myTradeHistory = JSON.parse(s); } catch(e) {}

function savePortfolio() { localStorage.setItem('myPortfolio', JSON.stringify(myPortfolio)); localStorage.setItem('myTradeHistory', JSON.stringify(myTradeHistory)); }



function addHolding() {

 const ticker = (document.getElementById('addTicker').value||'').toUpperCase().trim();

 const shares = parseFloat(document.getElementById('addShares').value);

 const buyPrice = parseFloat(document.getElementById('addBuyPrice').value);

 const buyDate = document.getElementById('addBuyDate').value || '';

 if (!ticker) { alert('Enter a ticker'); return; } if (!shares||shares<=0) { alert('Enter shares'); return; } if (!buyPrice||buyPrice<=0) { alert('Enter buy price'); return; }

 myPortfolio.push({ ticker, shares, buy_price: buyPrice, buy_date: buyDate });

 savePortfolio(); renderPortfolioList(); showToast(`Added ${shares} shares of ${ticker}`, 'success');

 document.getElementById('addTicker').value=''; document.getElementById('addShares').value=''; document.getElementById('addBuyPrice').value=''; document.getElementById('addBuyDate').value='';

}

function removeHolding(i) { if (!confirm(`Remove ${myPortfolio[i].ticker}?`)) return; myPortfolio.splice(i,1); savePortfolio(); renderPortfolioList(); document.getElementById('holdingsContent').innerHTML=''; }



// Sell Modal

function openSellModal(i) { sellTargetIndex=i; const h=myPortfolio[i]; document.getElementById('sellModalInfo').textContent=`Selling ${h.ticker} ${h.shares} shares at $${h.buy_price.toFixed(2)}`; document.getElementById('sellShares').value=h.shares; document.getElementById('sellPrice').value=''; document.getElementById('sellDate').value=new Date().toISOString().split('T')[0]; document.getElementById('sellModal').style.display='flex'; }

function closeSellModal() { document.getElementById('sellModal').style.display='none'; sellTargetIndex=-1; }

document.getElementById('sellModal').addEventListener('click', function(e) { if (e.target===this) closeSellModal(); });



function confirmSell() {

 if (sellTargetIndex<0) return; const h=myPortfolio[sellTargetIndex];

 const ss=parseFloat(document.getElementById('sellShares').value), sp=parseFloat(document.getElementById('sellPrice').value), sd=document.getElementById('sellDate').value||'';

 if (!ss||ss<=0) { alert('Enter shares'); return; } if (ss>h.shares) { alert(`Only ${h.shares} shares`); return; } if (!sp||sp<=0) { alert('Enter sell price'); return; }

 myTradeHistory.push({ticker:h.ticker,shares:ss,buy_price:h.buy_price,buy_date:h.buy_date,sell_price:sp,sell_date:sd});

 const rem=h.shares-ss; if (rem<=0.0001) myPortfolio.splice(sellTargetIndex,1); else myPortfolio[sellTargetIndex].shares=parseFloat(rem.toFixed(4));

 savePortfolio(); closeSellModal(); renderPortfolioList(); renderTradeHistory(); document.getElementById('holdingsContent').innerHTML='';

 const pnl=(sp-h.buy_price)*ss; showToast(`Sold ${ss} ${h.ticker} (${pnl>=0?'+':''}$${pnl.toFixed(2)})`, pnl>=0?'success':'error');

}



function renderPortfolioList() {
 const el=document.getElementById('portfolioHoldings');
 if (!myPortfolio.length) { el.innerHTML='<div style="text-align:center;padding:20px;color:var(--text-muted)">No holdings yet. Add your first stock above! </div>'; renderTradeHistory(); return; }
 // Group holdings by ticker
 var groups={}, groupOrder=[];
 myPortfolio.forEach(function(p,i){
  var t=p.ticker.toUpperCase();
  if(!groups[t]){groups[t]={ticker:t,lots:[],totalShares:0,totalCost:0};groupOrder.push(t);}
  groups[t].lots.push({idx:i,shares:p.shares,buy_price:p.buy_price,buy_date:p.buy_date||''});
  groups[t].totalShares+=p.shares;
  groups[t].totalCost+=p.shares*p.buy_price;
 });
 var totalLots=myPortfolio.length;
 var totalTickers=groupOrder.length;
 // Portfolio hero card
 var totalInvested=0;
 groupOrder.forEach(function(t){totalInvested+=groups[t].totalCost;});
 let h='<div class="portfolio-hero-card">';
 if(lastPortfolioAnalysisData && lastPortfolioAnalysisData.d){
  var pa=lastPortfolioAnalysisData.d;
  var pnlCls=pa.total_pnl>=0?'positive':'negative';
  h+='<div class="hero-value">'+fmtMoney(pa.total_current_value)+'</div>';
  h+='<div class="hero-pnl '+pnlCls+'">'+fmtMoneySign(pa.total_pnl)+' &nbsp; '+(pa.total_pnl>=0?'▲':'▼')+' '+Math.abs(pa.total_pnl_pct).toFixed(1)+'%</div>';
  h+='<div class="hero-invested">Invested: '+fmtMoney(pa.total_invested)+' · '+totalTickers+' ticker(s)</div>';
 } else {
  h+='<div class="hero-value">'+fmtMoney(totalInvested)+'</div>';
  h+='<div class="hero-pnl" style="color:rgba(255,255,255,0.5)">Total invested</div>';
  h+='<div class="hero-invested" style="opacity:0.7">Click Analyze for live P&L · '+totalTickers+' ticker(s)</div>';
 }
 h+='</div>';
 h+='<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px"><span style="font-size:0.9rem;font-weight:600">'+totalTickers+' ticker(s) · '+totalLots+' lot(s)</span><button class="btn btn-primary" onclick="analyzePortfolio()"> Analyze</button></div>';
 groupOrder.forEach(function(t){
  var g=groups[t];
  var avgPrice=g.totalCost/g.totalShares;
  var badge=getTickerBadge(t);
  var hasMultiple=g.lots.length>1;
  var expandId='lots_'+t.replace(/[^a-zA-Z0-9]/g,'_');
  h+='<div class="holding-group" style="margin-bottom:6px">';
  h+='<div class="holding-group-header" '+(hasMultiple?'onclick="toggleLots(\''+expandId+'\')" style="cursor:pointer"':'style="cursor:default"')+'>';
  h+='<div style="display:flex;align-items:center;gap:10px;flex:1;min-width:0">';
  if(hasMultiple) h+='<span class="lot-arrow" id="arrow_'+expandId+'">▶</span>';
  else h+='<span style="width:16px"></span>';
  h+='<strong style="color:var(--accent);font-size:0.95rem">'+t+'</strong>'+badge;
  h+='<span style="color:var(--text-secondary);font-size:0.8rem;margin-left:8px">'+g.totalShares.toFixed(4)+' shares</span>';
  h+='</div>';
  h+='<div style="display:flex;align-items:center;gap:16px">';
  h+='<span style="font-size:0.8rem;color:var(--text-secondary)">Avg '+fmtMoney(avgPrice)+'</span>';
  h+='<span style="font-size:0.9rem;font-weight:600">'+fmtMoney(g.totalCost)+'</span>';
  if(!hasMultiple){
   var idx=g.lots[0].idx;
   h+='<button class="btn btn-sell" onclick="event.stopPropagation();openSellModal('+idx+')">💰 Sell</button>';
   h+='<button class="btn btn-danger" onclick="event.stopPropagation();removeHolding('+idx+')">🗑️</button>';
  }
  h+='</div></div>';
  // Expandable lots panel
  if(hasMultiple){
   h+='<div class="lots-panel" id="'+expandId+'" style="display:none">';
   h+='<table style="width:100%;font-size:0.82rem"><thead><tr><th style="width:30px">#</th><th>Shares</th><th>Buy Price</th><th>Date</th><th>Cost</th><th>Actions</th></tr></thead><tbody>';
   g.lots.forEach(function(lot,li){
    h+='<tr><td style="color:var(--text-tertiary)">'+(li+1)+'</td>';
    h+='<td>'+lot.shares+'</td>';
    h+='<td>'+fmtMoney(lot.buy_price)+'</td>';
    h+='<td>'+lot.buy_date+'</td>';
    h+='<td>'+fmtMoney(lot.shares*lot.buy_price)+'</td>';
    h+='<td><button class="btn btn-sell" onclick="openSellModal('+lot.idx+')">💰 Sell</button> <button class="btn btn-danger" onclick="removeHolding('+lot.idx+')">🗑️</button></td></tr>';
   });
   h+='</tbody></table></div>';
  }
  h+='</div>';
 });
 el.innerHTML=h; renderTradeHistory();
}
function toggleLots(id){
 var panel=document.getElementById(id);
 var arrow=document.getElementById('arrow_'+id);
 if(!panel)return;
 if(panel.style.display==='none'){
  panel.style.display='block';
  panel.style.maxHeight='0';panel.style.overflow='hidden';
  requestAnimationFrame(function(){panel.style.maxHeight=panel.scrollHeight+'px';});
  setTimeout(function(){panel.style.maxHeight='none';panel.style.overflow='visible';},300);
  if(arrow)arrow.textContent='▼';
 } else {
  panel.style.maxHeight=panel.scrollHeight+'px';panel.style.overflow='hidden';
  requestAnimationFrame(function(){panel.style.maxHeight='0';});
  setTimeout(function(){panel.style.display='none';},300);
  if(arrow)arrow.textContent='▶';
 }
}



function renderTradeHistory() {

 const el=document.getElementById('tradeHistorySection');

 if (!myTradeHistory.length) { el.innerHTML=''; return; }

 let h=`<h3 style="margin-bottom:12px"> Trade History</h3>`;

 let tp=0,tl=0,w=0,l=0;

 const trades=myTradeHistory.map(t=>{const pnl=(t.sell_price-t.buy_price)*t.shares,pp=((t.sell_price-t.buy_price)/t.buy_price)*100;let dh=null;if(t.buy_date&&t.sell_date)dh=Math.round((new Date(t.sell_date)-new Date(t.buy_date))/(864e5));if(pnl>=0){w++;tp+=pnl}else{l++;tl+=pnl}return{...t,pnl,pnlPct:pp,daysHeld:dh}});

 const tot=w+l,wr=tot>0?((w/tot)*100).toFixed(1):0,net=tp+tl;

 h+=`<div class="trade-stats-grid"><div class="trade-stat"><div class="label">Trades</div><div class="value">${tot}</div></div><div class="trade-stat"><div class="label">Win Rate</div><div class="value ${parseFloat(wr)>=50?'positive':'negative'}">${wr}%</div></div><div class="trade-stat"><div class="label">Wins</div><div class="value positive">${w}</div></div><div class="trade-stat"><div class="label">Losses</div><div class="value negative">${l}</div></div><div class="trade-stat" style="border-color:${net>=0?'var(--green)':'var(--red)'}"><div class="label">Net P&L</div><div class="value ${net>=0?'positive':'negative'}">${fmtMoneySign(net)}</div></div></div>`;

 h+='<div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Shares</th><th>Buy</th><th>Sell</th><th>P&L</th><th>%</th><th>Days</th><th></th></tr></thead><tbody>';

 trades.slice().reverse().forEach((t,ri)=>{const i=trades.length-1-ri;const pc=t.pnl>=0?'positive':'negative';const ps=t.pnl>=0?'+':'';h+=`<tr><td><strong>${t.ticker}</strong></td><td>${t.shares}</td><td>${fmtMoney(t.buy_price)}</td><td>${fmtMoney(t.sell_price)}</td><td class="${pc}" style="font-weight:700">${fmtMoneySign(t.pnl)}</td><td class="${pc}">${ps}${t.pnlPct.toFixed(1)}%</td><td>${t.daysHeld!=null?t.daysHeld+'d':'?'}</td><td><button class="btn btn-danger" onclick="removeTrade(${i})">🗑️</button></td></tr>`;});
 lastTradeHistoryRendered=true;

 h+='</tbody></table></div><div style="margin-top:8px;text-align:right"><button class="btn btn-danger" onclick="clearTradeHistory()" style="font-size:0.8rem"> Clear History</button></div>';

 el.innerHTML=h;

}

function removeTrade(i) { if (!confirm('Remove trade?')) return; myTradeHistory.splice(i,1); savePortfolio(); renderTradeHistory(); }

function clearTradeHistory() { if (!confirm('Clear ALL history?')) return; myTradeHistory=[]; savePortfolio(); renderTradeHistory(); showToast('History cleared','info'); }



async function analyzePortfolio() {

 const el=document.getElementById('holdingsContent');

 if (!myPortfolio.length) { el.innerHTML='<div class="error-msg">Add holdings first!</div>'; return; }

 el.innerHTML='<div class="loading"><div class="spinner"></div><br>Analyzing portfolio + fetching news & earnings...</div>';

 try {

 // Fetch portfolio analysis AND intelligence (news + earnings) in parallel

 const [analysisRes, intelRes] = await Promise.all([

 fetch('/api/analyze-portfolio',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({holdings:myPortfolio,trade_history:myTradeHistory})}),

 fetch('/api/intelligence',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({holdings:myPortfolio,trade_history:myTradeHistory})}).catch(()=>null)

 ]);

 const j=await analysisRes.json(); if (j.status!=='ok') throw new Error(j.message);



 // Add intelligence data if available

 let intel = null;

 if (intelRes) { try { const ij = await intelRes.json(); if (ij.status === 'ok') intel = ij.data; } catch(e) {} }



 renderPortfolioAnalysis(j.data, intel);
 renderPortfolioList(); // Re-render hero card with P&L data

 } catch(e) { el.innerHTML=`<div class="error-msg"> ${e.message}<br><button class="btn" onclick="analyzePortfolio()"> Retry</button></div>`; }

}



function renderPortfolioAnalysis(d, intel) {

 const el=document.getElementById('holdingsContent'); let h='';

 const sc=d.total_pnl>=0?'green':'red';

 lastPortfolioAnalysisData={d:d,intel:intel};

 if (d.counts) h+=`<div style="display:flex;gap:12px;margin-bottom:16px"><span class="badge badge-green"> ${d.counts.green}</span><span class="badge badge-yellow"> ${d.counts.yellow}</span><span class="badge badge-red"> ${d.counts.red}</span></div>`;



 // Earnings warnings

 if (intel && intel.earnings_warnings && intel.earnings_warnings.length > 0) {

 h += `<div style="margin-bottom:16px">`;

 intel.earnings_warnings.forEach(w => {

 h += `<div style="padding:10px 16px;background:var(--yellow-bg);border:1px solid rgba(255,214,0,0.3);border-radius:8px;margin-bottom:6px;font-size:0.85rem;color:var(--yellow)">${w.warning}</div>`;

 });

 h += `</div>`;

 }



 // News headlines

 if (intel && intel.news && Object.keys(intel.news).length > 0) {

 h += `<div style="margin-bottom:16px"><div style="font-size:0.9rem;font-weight:600;margin-bottom:8px"> Latest News</div>`;

 for (const [ticker, headlines] of Object.entries(intel.news)) {

 headlines.forEach(n => {

 h += `<div style="padding:8px 12px;background:var(--bg);border:1px solid var(--border);border-radius:8px;margin-bottom:4px;font-size:0.8rem">

 <strong style="color:var(--accent)">${ticker}</strong> ${n.title}

 <span style="color:var(--text-muted);margin-left:8px">${n.publisher} ${n.date}</span>

 </div>`;

 });

 }

 h += `</div>`;

 }



 // Market regime in portfolio view

 if (intel && intel.market_regime && intel.market_regime.regime !== 'unknown') {

 const mr = intel.market_regime;

 const regimeColors = {bull:'green',bear:'red',correction:'yellow',sideways:'yellow'};

 h += `<div class="sentiment-bar ${regimeColors[mr.regime]||'yellow'}" style="margin-bottom:16px;font-size:0.85rem">

 <strong> Market: ${mr.regime.toUpperCase()}</strong> ${mr.strategy_hint}

 </div>`;

 }

 if (d.trade_stats) { const ts=d.trade_stats; h+=`<div style="margin-bottom:16px"><div style="font-size:0.9rem;font-weight:600;margin-bottom:8px"> Trading Insights</div>`; if(ts.insights)ts.insights.forEach(i=>{h+=`<div class="insight-card">${i}</div>`;}); if(ts.best_trade)h+=`<div style="display:flex;gap:12px;margin-top:8px;font-size:0.8rem;color:var(--text-muted)"><span> Best: <strong class="positive">${ts.best_trade.ticker} +${ts.best_trade.pnl_pct}%</strong></span><span> Worst: <strong class="negative">${ts.worst_trade.ticker} ${ts.worst_trade.pnl_pct}%</strong></span></div>`; h+=`</div>`; }

 d.holdings.forEach(h2=>{const pc=(h2.pnl||0)>=0?'positive':'negative';const ps=(h2.pnl||0)>=0?'+':'';h+=`<div class="holding-card" style="border-left:4px solid var(--${h2.status==='green'?'green':h2.status==='red'?'red':h2.status==='yellow'?'yellow':'border'})"><div class="status-dot ${h2.status}"></div><div class="info"><h4><strong style="color:var(--accent)">${h2.ticker}</strong> ${h2.name} <span style="font-size:0.75rem;color:var(--text-muted)">${h2.status_label}</span>${h2.days_held!=null?` <span style="font-size:0.7rem;color:var(--text-muted)"> ${h2.days_label}</span>`:''}</h4><div class="advice"> ${h2.advice}</div><div style="font-size:0.75rem;color:var(--text-muted);margin-top:4px">${h2.shares} shares ${fmtMoney(h2.buy_price)} ${fmtMoney(h2.current_price)}</div></div><div class="price-info" style="min-width:140px">${h2.pnl!=null?`<div class="${pc}" style="font-size:1.2rem;font-weight:700">${fmtMoneySign(h2.pnl)}</div><div class="${pc}" style="font-size:0.85rem">${ps}${h2.pnl_pct}%</div>`:'<div style="color:var(--text-muted)">No data</div>'}</div></div>`;});

 el.innerHTML=h;

}

renderPortfolioList();



// Export/Import/Sync

function exportPortfolio() { const d={holdings:myPortfolio,trade_history:myTradeHistory,exported_at:new Date().toISOString()}; const b=new Blob([JSON.stringify(d,null,2)],{type:'application/json'}); const u=URL.createObjectURL(b); const a=document.createElement('a'); a.href=u; a.download=`portfolio_${new Date().toISOString().split('T')[0]}.json`; a.click(); URL.revokeObjectURL(u); showToast('Exported JSON!','success'); }

function exportPortfolioCSV() {
 if (!myPortfolio.length) { showToast('No holdings to export', 'info'); return; }
 let csv = 'ticker,shares,buy_price,buy_date\n';
 myPortfolio.forEach(h => {
  csv += `${h.ticker},${h.shares},${h.buy_price},${h.buy_date || ''}\n`;
 });
 const b = new Blob([csv], {type: 'text/csv'});
 const u = URL.createObjectURL(b);
 const a = document.createElement('a');
 a.href = u; a.download = `portfolio_${new Date().toISOString().split('T')[0]}.csv`;
 a.click(); URL.revokeObjectURL(u);
 showToast('Exported CSV!', 'success');
}

function importPortfolio(event) {
 const f = event.target.files[0];
 if (!f) return;
 const ext = f.name.split('.').pop().toLowerCase();
 const r = new FileReader();
 r.onload = function(e) {
  try {
   if (ext === 'csv') {
    let text = e.target.result;
    if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1);
    const lines = text.split(/\r?\n/).filter(l => l.trim());
    if (lines.length < 2) { alert('CSV file is empty or has no data rows.'); return; }
    const header = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/['"]/g, ''));
    const colMap = {};
    const tickerNames = ['ticker','symbol','stock','instrument','code'];
    const sharesNames = ['shares','quantity','qty','amount','units'];
    const priceNames = ['buy_price','price','avg_price','cost_per_share','average_price','cost','buy price','avg price'];
    const dateNames = ['buy_date','date','purchase_date','bought','buy date','purchase date'];
    header.forEach((col, i) => {
     if (colMap.ticker === undefined && tickerNames.includes(col)) colMap.ticker = i;
     else if (colMap.shares === undefined && sharesNames.includes(col)) colMap.shares = i;
     else if (colMap.buy_price === undefined && priceNames.includes(col)) colMap.buy_price = i;
     else if (colMap.buy_date === undefined && dateNames.includes(col)) colMap.buy_date = i;
    });
    if (colMap.ticker === undefined) { alert('CSV must have a "ticker" or "symbol" column.\n\nExpected format:\nticker,shares,buy_price,buy_date\nNVDA,5,200.50,2026-03-15'); return; }
    if (colMap.shares === undefined) { alert('CSV must have a "shares" or "quantity" column.'); return; }
    if (colMap.buy_price === undefined) { alert('CSV must have a "buy_price" or "price" column.'); return; }
    const parsed = [];
    const errors = [];
    for (let i = 1; i < lines.length; i++) {
     const cols = lines[i].split(',').map(c => c.trim().replace(/^["']|["']$/g, ''));
     const ticker = (cols[colMap.ticker] || '').toUpperCase().trim();
     const shares = parseFloat(cols[colMap.shares]);
     const buy_price = parseFloat(cols[colMap.buy_price]);
     const buy_date = colMap.buy_date !== undefined ? (cols[colMap.buy_date] || '').trim() : '';
     if (!ticker) continue;
     if (isNaN(shares) || shares <= 0) { errors.push('Row '+(i+1)+': Invalid shares for '+ticker); continue; }
     if (isNaN(buy_price) || buy_price <= 0) { errors.push('Row '+(i+1)+': Invalid price for '+ticker); continue; }
     parsed.push({ ticker, shares, buy_price, buy_date });
    }
    if (parsed.length === 0) { alert('No valid holdings found in CSV.' + (errors.length ? '\n\nErrors:\n' + errors.join('\n') : '')); return; }
    let msg = 'Found ' + parsed.length + ' holdings in CSV:\n\n';
    parsed.slice(0, 8).forEach(h => { msg += '  ' + h.ticker + ': ' + h.shares + ' shares @ $' + h.buy_price + '\n'; });
    if (parsed.length > 8) msg += '  ... and ' + (parsed.length - 8) + ' more\n';
    if (errors.length) msg += '\n⚠️ ' + errors.length + ' row(s) skipped (invalid data)';
    msg += '\n\nImport these holdings?';
    if (!confirm(msg)) return;
    myPortfolio = parsed;
    myTradeHistory = [];
    savePortfolio(); renderPortfolioList();
    document.getElementById('holdingsContent').innerHTML = '';
    showToast('Imported ' + parsed.length + ' holdings from CSV!', 'success');
   } else {
    const d = JSON.parse(e.target.result);
    if (d.holdings && Array.isArray(d.holdings)) {
     if (!confirm('Import ' + d.holdings.length + ' holdings?')) return;
     myPortfolio = d.holdings;
     myTradeHistory = d.trade_history || [];
     savePortfolio(); renderPortfolioList();
     document.getElementById('holdingsContent').innerHTML = '';
     showToast('Imported from JSON!', 'success');
    } else { alert('Invalid JSON file. Expected {holdings: [...]}'); }
   }
  } catch(err) { alert('Error reading file: ' + err.message); }
 };
 r.readAsText(f);
 event.target.value = '';
}

async function syncToServer() { try{const r=await fetch('/api/portfolio-data',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({holdings:myPortfolio,trade_history:myTradeHistory})});const j=await r.json();if(j.status==='ok')showToast('Saved to server!','success');else throw new Error(j.message);}catch(e){showToast('Failed: '+e.message,'error');} }

async function syncFromServer() { try{const r=await fetch('/api/portfolio-data');const j=await r.json();if(j.status==='ok'&&j.data){const d=j.data;if(!d.holdings?.length&&!d.trade_history?.length){showToast('No data on server','info');return;}if(!confirm(`Load ${d.holdings?.length||0} holdings?`))return;myPortfolio=d.holdings||[];myTradeHistory=d.trade_history||[];savePortfolio();renderPortfolioList();document.getElementById('holdingsContent').innerHTML='';showToast('Loaded!','success');}else throw new Error(j.message||'No data');}catch(e){showToast('Failed: '+e.message,'error');} }

// ============================================================
// PIN-BASED PORTFOLIO SYNC (cross-device)
// ============================================================
async function pinSave() {
 var pinEl = document.getElementById('pinInput');
 var pin = (pinEl ? pinEl.value : '').trim();
 if (!pin || pin.length < 6) { showToast('Enter a PIN (6+ characters)', 'error'); return; }
 if (!myPortfolio.length && !myTradeHistory.length) { showToast('No portfolio data to save', 'info'); return; }
 try {
  var r = await fetch('/api/portfolio-pin/save', {
   method: 'POST', headers: {'Content-Type':'application/json'},
   body: JSON.stringify({ pin: pin, holdings: myPortfolio, trade_history: myTradeHistory })
  });
  var j = await r.json();
  if (j.status === 'ok') {
   localStorage.setItem('portfolioPin', pin);
   showToast('✅ ' + j.message, 'success');
  } else { showToast('❌ ' + j.message, 'error'); }
 } catch(e) { showToast('Failed: ' + e.message, 'error'); }
}

async function pinLoad() {
 var pinEl = document.getElementById('pinInput');
 var pin = (pinEl ? pinEl.value : '').trim();
 if (!pin || pin.length < 6) { showToast('Enter your PIN (6+ characters)', 'error'); return; }
 try {
  var r = await fetch('/api/portfolio-pin/load', {
   method: 'POST', headers: {'Content-Type':'application/json'},
   body: JSON.stringify({ pin: pin })
  });
  var j = await r.json();
  if (j.status === 'ok' && j.data) {
   var d = j.data;
   var count = (d.holdings || []).length;
   if (!confirm('Load ' + count + ' holdings from PIN?\nLast saved: ' + (j.updated_at || '?').substring(0, 16))) return;
   myPortfolio = d.holdings || [];
   myTradeHistory = d.trade_history || [];
   savePortfolio();
   localStorage.setItem('portfolioPin', pin);
   renderPortfolioList();
   document.getElementById('holdingsContent').innerHTML = '';
   showToast('✅ ' + j.message, 'success');
  } else { showToast('❌ ' + (j.message || 'Not found'), 'error'); }
 } catch(e) { showToast('Failed: ' + e.message, 'error'); }
}

// Restore saved PIN
(function() {
 var savedPin = localStorage.getItem('portfolioPin');
 if (savedPin) {
  setTimeout(function() {
   var el = document.getElementById('pinInput');
   if (el) el.value = savedPin;
  }, 100);
 }
})();



// ============================================================

// GOAL / COMPOUND / PORTFOLIO / MARKET / COMMODITIES

// ============================================================

async function calcGoal() { const g=document.getElementById('goalAmount').value||200,m=document.getElementById('goalMonths').value||1,el=document.getElementById('goalResult'); el.innerHTML='<div class="loading"><div class="spinner"></div><br>Scanning 500+ stocks...</div>'; try{const r=await fetch(`/api/goal?goal=${g}&months=${m}`);const j=await r.json();if(j.status!=='ok')throw new Error(j.message);renderGoal(j.data);}catch(e){el.innerHTML=`<div class="error-msg"> ${e.message}<br><button class="btn" onclick="calcGoal()"> Retry</button></div>`;} }

function renderGoal(d) { lastGoalData=d; const el=document.getElementById('goalResult'),picks=d.picks; if(!picks?.length){el.innerHTML='<div class="error-msg">No stocks found.</div>';return;} let h=`<div style="padding:12px;background:var(--bg);border:1px solid var(--border);border-radius:10px;font-size:0.9rem;margin:16px 0"> To make <strong style="color:var(--green)">${fmtMoney(parseFloat(d.target_profit))}</strong> in <strong>${d.months} month(s)</strong>:</div>`; const top3=picks.slice(0,3),ranks=[' Best',' Second',' Third']; h+='<div class="grid-3">'; top3.forEach((p,i)=>{const fb=p.feasibility_color==='green'?'badge-green':p.feasibility_color==='red'?'badge-red':'badge-yellow';h+=`<div class="goal-card" ${i===0?'style="border-color:var(--accent)"':''}><div class="rank">${ranks[i]}</div><div class="ticker-name"><span class="ticker">${p.ticker}</span> ${p.is_etf?'<span class="badge badge-blue" style="font-size:0.6rem">ETF</span>':''}</div><div style="color:var(--text-muted);font-size:0.85rem">${p.name}</div><div class="invest-big">${fmtMoney(p.investment_needed)}</div><div style="font-size:0.8rem;color:var(--text-muted)">at ${fmtMoney(p.price)}/share</div><div class="scenarios"><div class="scenario"><div class="positive"> +${fmtMoney(p.optimistic_profit)}</div><div style="color:var(--text-muted)">Best</div></div><div class="scenario"><div style="color:var(--blue)"> +${fmtMoney(p.expected_profit)}</div><div style="color:var(--text-muted)">Expected</div></div><div class="scenario"><div class="${p.pessimistic_profit>=0?'positive':'negative'}"> ${fmtMoneySign(p.pessimistic_profit)}</div><div style="color:var(--text-muted)">Worst</div></div></div><div style="margin-top:12px"><span class="badge ${fb}">${p.feasibility}</span></div></div>`;}); h+='</div>'; if(picks.length>3){h+=`<details style="margin-top:16px"><summary style="cursor:pointer;color:var(--accent);font-size:0.9rem"> ${picks.length-3} more...</summary><div class="table-wrap" style="margin-top:12px"><table><thead><tr><th>#</th><th>Stock</th><th>Price</th><th>Invest</th><th>Expected</th><th>Feasibility</th></tr></thead><tbody>`;picks.slice(3).forEach((p,i)=>{const fb=p.feasibility_color==='green'?'badge-green':'badge-yellow';h+=`<tr><td>${i+4}</td><td><strong>${p.ticker}</strong><br><span style="font-size:0.7rem;color:var(--text-muted)">${p.name}</span></td><td>${fmtMoney(p.price)}</td><td style="font-weight:700;color:var(--accent)">${fmtMoney(p.investment_needed)}</td><td style="color:var(--blue)">+${fmtMoney(p.expected_profit)}</td><td><span class="badge ${fb}">${p.feasibility}</span></td></tr>`;});h+='</tbody></table></div></details>';} el.innerHTML=h; }



let compoundMode = 'simple'; // 'simple' or 'montecarlo'

async function calcCompound() {
 const i=document.getElementById('compInitial').value||1000;
 const m=document.getElementById('compMonthly').value||200;
 const mo=document.getElementById('compMonths').value||24;
 const rt=document.getElementById('compReturn').value||10;
 const el=document.getElementById('compoundResult');

 if (compoundMode === 'montecarlo') {
  el.innerHTML='<div class="loading"><div class="spinner"></div><br>Running 1,000 simulations...</div>';
  try {
   const r=await fetch(`/api/montecarlo?initial=${i}&monthly=${m}&months=${mo}&return=${rt}`);
   const j=await r.json();
   if(j.status!=='ok') throw new Error(j.message);
   const d=j.data;
   lastCompoundData={mode:'montecarlo',data:d};lastCompoundHtml=true;
   el.innerHTML=`<div class="sim-stats" style="margin-top:16px">
    <div class="sim-stat"><div class="label">Invested</div><div class="value">${fmtMoney(d.total_invested)}</div></div>
    <div class="sim-stat" style="border-color:var(--green)"><div class="label">🎲 90th %ile</div><div class="value positive">${fmtMoney(d.p90)}</div><div style="font-size:0.6rem;color:var(--text-tertiary)">Best 10% of outcomes</div></div>
    <div class="sim-stat" style="border-color:var(--blue)"><div class="label">🎲 Median</div><div class="value">${fmtMoney(d.median)}</div><div style="font-size:0.6rem;color:var(--text-tertiary)">Most likely outcome</div></div>
    <div class="sim-stat" style="border-color:var(--red)"><div class="label">🎲 10th %ile</div><div class="value ${d.p10_profit>=0?'positive':'negative'}">${fmtMoney(d.p10)}</div><div style="font-size:0.6rem;color:var(--text-tertiary)">Worst 10% of outcomes</div></div>
   </div>
   <div style="padding:12px 16px;background:var(--bg);border:1px solid var(--border);border-radius:10px;margin-top:12px;font-size:0.8rem;color:var(--text-secondary)">
    <strong>🎲 Monte Carlo Simulation</strong> — ${d.simulations.toLocaleString()} random scenarios using historical S&P 500 volatility (σ=${d.annual_vol_pct}%/yr).<br>
    <strong>${d.prob_profit}%</strong> chance of making a profit · Median profit: <strong class="${d.median_profit>=0?'positive':'negative'}">${fmtMoney(d.median_profit)}</strong> ·
    Range: <span class="negative">${fmtMoney(d.p10_profit)}</span> to <span class="positive">+${fmtMoney(d.p90_profit)}</span>
   </div>`;
   // Render Monte Carlo chart
   if (typeof renderCompoundChart === 'function') renderCompoundChart(d, 'montecarlo');
  } catch(err) { el.innerHTML=`<div class="error-msg">${err.message}</div>`; }
 } else {
  try {
   const r=await fetch(`/api/compound?initial=${i}&monthly=${m}&months=${mo}&return=${rt}`);
   const j=await r.json();
   if(j.status!=='ok') throw new Error(j.message);
   const d=j.data,e=d.expected,o=d.optimistic,p=d.pessimistic;
   const annRt = parseFloat(rt);
   lastCompoundData={mode:'simple',expected:e,optimistic:o,pessimistic:p,annRt:annRt};lastCompoundHtml=true;
   el.innerHTML=`<div class="sim-stats" style="margin-top:16px">
    <div class="sim-stat"><div class="label">Invested</div><div class="value">${fmtMoney(e.total_invested)}</div></div>
    <div class="sim-stat" style="border-color:var(--green)"><div class="label">📈 Optimistic</div><div class="value positive">${fmtMoney(o.final_value)}</div><div style="font-size:0.6rem;color:var(--text-tertiary)">${(annRt*1.5).toFixed(1)}%/yr</div></div>
    <div class="sim-stat" style="border-color:var(--blue)"><div class="label">📊 Expected</div><div class="value">${fmtMoney(e.final_value)}</div><div style="font-size:0.6rem;color:var(--text-tertiary)">${annRt.toFixed(1)}%/yr</div></div>
    <div class="sim-stat" style="border-color:var(--red)"><div class="label">📉 Pessimistic</div><div class="value">${fmtMoney(p.final_value)}</div><div style="font-size:0.6rem;color:var(--text-tertiary)">${(annRt*0.5).toFixed(1)}%/yr</div></div>
   </div>
   <div style="padding:12px 16px;background:var(--bg);border:1px solid var(--border);border-radius:10px;margin-top:12px;font-size:0.8rem;color:var(--text-secondary)">
    <strong>ℹ️ How scenarios work:</strong> Expected uses your set return (${annRt}%). Optimistic = 1.5× (${(annRt*1.5).toFixed(1)}%). Pessimistic = 0.5× (${(annRt*0.5).toFixed(1)}%). These are simple multipliers showing a range — not guarantees. Try <strong style="color:var(--accent);cursor:pointer" onclick="compoundMode='montecarlo';document.getElementById('mcToggle').classList.add('active');document.getElementById('simpleToggle').classList.remove('active');calcCompound()">🎲 Monte Carlo</strong> for a more realistic simulation.
   </div>`;
   // Render simple compound chart
   if (typeof renderCompoundChart === 'function') renderCompoundChart({expected:e,optimistic:o,pessimistic:p}, 'simple');
  } catch(err) { el.innerHTML=`<div class="error-msg">${err.message}</div>`; }
 }
}

function setCompoundMode(mode, btn) {
 compoundMode = mode;
 document.getElementById('simpleToggle').classList.toggle('active', mode === 'simple');
 document.getElementById('mcToggle').classList.toggle('active', mode === 'montecarlo');
}



function selectProfile(profile, el) { currentProfile=profile; document.querySelectorAll('.profile-card').forEach(c=>c.classList.remove('active')); el.classList.add('active'); saveSettings(); }

async function loadPortfolio() { const a=document.getElementById('investmentAmount').value||10000,m=document.getElementById('timeframeMonths').value||12,c=document.getElementById('portfolioContent'); c.innerHTML='<div class="loading"><div class="spinner"></div><br>Building portfolio...</div>'; try{const r=await fetch(`/api/portfolio?profile=${currentProfile}&investment=${a}&months=${m}&tickers=0`);const j=await r.json();if(j.status!=='ok')throw new Error(j.message);renderPortfolio(j.data);dataLoaded['portfolios']=true;ts();}catch(e){c.innerHTML=`<div class="error-msg">${e.message}</div>`;} }

function renderPortfolio(d) { lastPortfolioTabData=d; const c=document.getElementById('portfolioContent'); let h=`<div style="margin-bottom:20px"><h3>${d.name}</h3><p style="color:var(--text-muted);font-size:0.9rem">${d.description}</p><div style="display:flex;gap:12px;margin-top:8px;flex-wrap:wrap"><span class="badge badge-blue">Risk: ${d.risk_level}</span><span class="badge badge-green">Target: ${d.target_return}</span><span class="badge badge-yellow">Rebalance: ${d.rebalance}</span></div></div>`; if(d.simulation){const s=d.simulation;h+=`<div style="margin-bottom:12px"><strong> ${d.timeframe_label||'1y'} Projection</strong></div><div class="sim-stats"><div class="sim-stat"><div class="label">Invested</div><div class="value">${fmtMoney(d.investment)}</div></div><div class="sim-stat" style="border-color:var(--green)"><div class="label"> Optimistic</div><div class="value positive">${fmtMoney(s.optimistic_value)}</div></div><div class="sim-stat" style="border-color:var(--blue)"><div class="label"> Expected</div><div class="value">${fmtMoney(s.end_value)}</div></div><div class="sim-stat" style="border-color:var(--red)"><div class="label"> Pessimistic</div><div class="value">${fmtMoney(s.pessimistic_value)}</div></div></div>`;} h+='<div style="margin:16px 0"><strong>Allocation:</strong></div><div class="alloc-bar">'; d.buy_list.forEach((b,i)=>{h+=`<div class="alloc-segment" style="width:${b.target_pct}%;background:${COLORS[i%COLORS.length]}">${b.target_pct>5?b.target_pct+'%':''}</div>`;}); h+='</div><div class="alloc-legend">'; d.buy_list.forEach((b,i)=>{h+=`<div class="alloc-legend-item"><div class="alloc-dot" style="background:${COLORS[i%COLORS.length]}"></div>${b.ticker} (${b.target_pct}%)</div>`;}); h+=`</div><div style="margin-top:24px"><h3> Buy List:</h3></div><div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Name</th><th>%</th><th>Price</th><th>Shares</th><th>Cost</th><th>Why</th></tr></thead><tbody>`; d.buy_list.forEach(b=>{h+=`<tr><td><strong>${b.ticker}</strong></td><td>${b.name}</td><td>${b.target_pct}%</td><td>${b.price?fmtMoney(b.price):'N/A'}</td><td style="font-weight:700;color:var(--accent)">${b.shares_to_buy.toFixed(4)}</td><td>${fmtMoney(b.cost)}</td><td style="font-size:0.8rem;color:var(--text-muted)">${b.why}</td></tr>`;}); h+=`</tbody></table></div><div style="margin-top:16px;padding:16px;background:var(--bg);border:1px solid var(--border);border-radius:10px"><strong>Total:</strong> ${fmtMoney(d.total_allocated)} | <strong>Cash:</strong> ${fmtMoney(d.cash_remaining)}</div>`; c.innerHTML=h; if(d.simulation && typeof renderPortfolioChart === 'function') renderPortfolioChart(d.simulation); }



async function loadMarketData() { try{const[mr,mv]=await Promise.all([fetch('/api/market-overview'),fetch('/api/top-movers?market=all')]);const mkt=await mr.json(),mov=await mv.json();if(mkt.status==='ok'){lastMarketData=mkt.data;renderIndices('usIndices',mkt.data.us);renderIndices('euIndices',mkt.data.eu);}if(mov.status==='ok'){lastMoversData=mov.data;renderMovers('gainersTable',mov.data.gainers);renderMovers('losersTable',mov.data.losers);}dataLoaded['market']=true;ts();}catch(e){document.getElementById('usIndices').innerHTML=`<div class="error-msg">${e.message}</div>`;} }

function renderIndices(id,indices) { const el=document.getElementById(id); if(!indices?.length){el.innerHTML='<div class="error-msg">No data</div>';return;} el.innerHTML=indices.filter(i=>i.price!=null).map(i=>`<div class="index-card"><div class="name">${i.name}</div><div class="price">${(i.price||0).toLocaleString()}</div><div class="change ${cc(i.change)}">${ci(i.change)} ${fc(i.change)}</div></div>`).join(''); }

function renderMovers(id,movers) { const el=document.getElementById(id); if(!movers?.length){el.innerHTML='<div class="error-msg">No data</div>';return;} let h='<table><thead><tr><th>#</th><th>Stock</th><th>Price</th><th>Change</th></tr></thead><tbody>'; movers.forEach((m,i)=>{h+=`<tr><td>${i+1}</td><td><strong>${m.ticker}</strong><br><span style="font-size:0.7rem;color:var(--text-muted)">${m.name}</span></td><td>${fmtMoney(m.price)}</td><td class="${cc(m.change)}" style="font-weight:700">${ci(m.change)} ${fc(m.change)}</td></tr>`;}); el.innerHTML=h+'</tbody></table>'; }



async function loadCommodities() { const el=document.getElementById('commoditiesContent'); el.innerHTML='<div class="loading"><div class="spinner"></div><br>Loading...</div>'; try{const r=await fetch('/api/commodities');const j=await r.json();if(j.status!=='ok')throw new Error(j.message);renderCommodities(j.data);dataLoaded['commodities']=true;ts();}catch(e){el.innerHTML=`<div class="error-msg"> ${e.message}<br><button class="btn" onclick="loadCommodities()"> Retry</button></div>`;} }

function renderCommodities(commodities) { lastCommoditiesData=commodities; const el=document.getElementById('commoditiesContent'); if(!commodities?.length){el.innerHTML='<div class="error-msg">No data</div>';return;} let h='<div class="commodity-grid">'; commodities.forEach(c=>{const icon=COMMODITY_ICONS[c.name]||'';h+=`<div class="commodity-card"><div class="commodity-ticker">${c.ticker}</div><div class="commodity-icon">${icon}</div><div class="commodity-name">${c.name}</div><div class="commodity-price">${fmtMoney(c.price)}</div><div class="commodity-change ${cc(c.change)}">${ci(c.change)} ${fc(c.change)}</div>${c.pct_1w!=null?`<div class="commodity-week">Week: <span class="${cc(c.pct_1w)}">${fc(c.pct_1w)}</span></div>`:''}</div>`;}); h+=`</div><div style="margin-top:20px;padding:16px;background:var(--bg);border:1px solid var(--border);border-radius:10px"><div style="font-size:0.9rem;font-weight:600;margin-bottom:8px"> Commodity ETFs:</div><div style="font-size:0.85rem;color:var(--text-muted)"><strong style="color:var(--accent)">GLD</strong> Gold <strong style="color:var(--accent)">SLV</strong> Silver <strong style="color:var(--accent)">USO</strong> Oil <strong style="color:var(--accent)">PPLT</strong> Platinum <strong style="color:var(--accent)">UNG</strong> Gas <strong style="color:var(--accent)">DBC</strong> Broad</div></div>`; el.innerHTML=h; }




function calcCompoundRedraw(){if(!lastCompoundData)return;if(lastCompoundData.mode==='montecarlo'){var d=lastCompoundData.data;document.getElementById('compoundResult').innerHTML='<div class="sim-stats" style="margin-top:16px"><div class="sim-stat"><div class="label">Invested</div><div class="value">'+fmtMoney(d.total_invested)+'</div></div><div class="sim-stat" style="border-color:var(--green)"><div class="label">90th %ile</div><div class="value positive">'+fmtMoney(d.p90)+'</div></div><div class="sim-stat" style="border-color:var(--blue)"><div class="label">Median</div><div class="value">'+fmtMoney(d.median)+'</div></div><div class="sim-stat" style="border-color:var(--red)"><div class="label">10th %ile</div><div class="value">'+fmtMoney(d.p10)+'</div></div></div>';}else if(lastCompoundData.mode==='simple'){var e=lastCompoundData.expected,o=lastCompoundData.optimistic,p=lastCompoundData.pessimistic;document.getElementById('compoundResult').innerHTML='<div class="sim-stats" style="margin-top:16px"><div class="sim-stat"><div class="label">Invested</div><div class="value">'+fmtMoney(e.total_invested)+'</div></div><div class="sim-stat" style="border-color:var(--green)"><div class="label">Optimistic</div><div class="value positive">'+fmtMoney(o.final_value)+'</div></div><div class="sim-stat" style="border-color:var(--blue)"><div class="label">Expected</div><div class="value">'+fmtMoney(e.final_value)+'</div></div><div class="sim-stat" style="border-color:var(--red)"><div class="label">Pessimistic</div><div class="value">'+fmtMoney(p.final_value)+'</div></div></div>';}}
function reRenderMarket(){if(lastMarketData){renderIndices('usIndices',lastMarketData.us);renderIndices('euIndices',lastMarketData.eu);}if(lastMoversData){renderMovers('gainersTable',lastMoversData.gainers);renderMovers('losersTable',lastMoversData.losers);}}
function reRenderCommodities(){if(lastCommoditiesData)renderCommodities(lastCommoditiesData);if(lastCryptoData){var el=document.getElementById('commoditiesContent');var h=el.innerHTML;h+='<div style="margin-top:24px"><h3 style="margin-bottom:12px">Crypto Top 25</h3></div><div class="crypto-grid">';lastCryptoData.forEach(function(c){h+='<div class="crypto-card"><div class="crypto-name">'+c.name+'</div><div class="crypto-price">'+fmtMoney(c.price)+'</div><div class="crypto-change '+cc(c.change)+'">'+ci(c.change)+' '+fc(c.change)+'</div></div>';});h+='</div>';el.innerHTML=h;}}

async function refreshAll() { await fetch('/api/clear-cache',{method:'POST'}); Object.keys(dataLoaded).forEach(k=>dataLoaded[k]=false); const active=document.querySelector('.tab.active'); if(active)loadTabData(active.dataset.tab); showToast('Refreshing...','info'); }



// Init

document.querySelectorAll('.strategy-btn').forEach(b=>{if(b.dataset.strategy===currentStrategy){document.querySelectorAll('.strategy-btn').forEach(x=>x.classList.remove('active'));b.classList.add('active');}});

document.querySelectorAll('.profile-card').forEach(c=>{if(c.textContent.toLowerCase().includes(currentProfile)){document.querySelectorAll('.profile-card').forEach(x=>x.classList.remove('active'));c.classList.add('active');}});

// Hide beginner tips if user dismissed them

if (localStorage.getItem('hideTips') === '1') {

 const tips = document.getElementById('beginnerTips');

 if (tips) tips.style.display = 'none';

}



// ============================================================

// AI STATUS Check if server-side AI is available

// ============================================================

async function checkAIStatus() {

 const badge = document.getElementById('aiStatusBadge');

 try {

 const r = await fetch('/api/ai-status');

 const j = await r.json();

 if (j.ai_available) {

 aiAvailable = true;

 badge.className = 'ai-status-badge active';

 badge.textContent = ' AI Active';

 badge.title = `AI Analysis: ${j.model} via ${j.provider}`;

 } else {

 aiAvailable = false;

 badge.className = 'ai-status-badge inactive';

 badge.textContent = ' Technical Only';

 badge.title = 'Set GROQ_API_KEY on server to enable AI analysis';

 }

 } catch(e) {

 badge.className = 'ai-status-badge inactive';

 badge.textContent = ' Technical Only';

 }

}



// ============================================================

// AI ENHANCE Add AI insights to action cards after render

// ============================================================

async function aiEnhanceActions(actions) {

 if (!aiAvailable || !actions || actions.length === 0) return;



 // Build stock data for AI

 const stocks = actions.map(a => ({

 ticker: a.ticker, name: a.name, price: a.price,

 score: a.score, rsi: a.rsi, trend: a.trend || 'neutral',

 pct_1w: a.pct_1w, pct_1m: a.pct_1m,

 pct_3m: a.pct_3m || null,

 }));



 try {

 const r = await fetch('/api/ai-enhance', {

 method: 'POST', headers: {'Content-Type':'application/json'},

 body: JSON.stringify({ stocks })

 });

 const j = await r.json();

 if (!j.ai_enhanced || !j.results) return;



 // Inject AI insights into the DOM

 for (const [ticker, ai] of Object.entries(j.results)) {

 const cards = document.querySelectorAll('.action-card.buy');

 cards.forEach(card => {

 if (card.querySelector('.ticker')?.textContent === ticker) {

 // Check if already has AI insight

 if (card.querySelector('.ai-insight-box')) return;

 const infoDiv = card.querySelector('.action-info');

 if (!infoDiv) return;



 const confCls = ai.ai_confidence === 'high' ? 'high' : ai.ai_confidence === 'low' ? 'low' : 'medium';

 const scoreCls = ai.ai_score > 10 ? 'positive' : ai.ai_score < -10 ? 'negative' : 'neutral';



 const aiBox = document.createElement('div');

 aiBox.className = 'ai-insight-box';

 aiBox.innerHTML = `

 <span class="ai-label"> AI:</span>

 <span class="ai-reasoning">${ai.ai_reasoning}</span>

 ${ai.ai_risk ? `<br><span class="ai-risk"> ${ai.ai_risk}</span>` : ''}

 <span class="ai-confidence ${confCls}">${ai.ai_confidence}</span>

 <span class="ai-score-badge ${scoreCls}">AI: ${ai.ai_score > 0 ? '+' : ''}${ai.ai_score}</span>

 ${ai.combined_score != null ? `<span class="ai-score-badge ${ai.combined_score >= 25 ? 'positive' : ai.combined_score >= 0 ? 'neutral' : 'negative'}">Combined: ${ai.combined_score}</span>` : ''}

 `;

 infoDiv.appendChild(aiBox);

 }

 });

 }

 } catch(e) {

 console.log('AI enhance failed:', e.message);

 }

}



// Override renderActions to trigger AI enhancement after render

const _originalRenderActions = renderActions;

renderActions = function(d) {

 _originalRenderActions(d);

 // After rendering, trigger AI enhancement for buy actions (async, non-blocking)

 if (aiAvailable && d.actions && d.actions.length > 0) {

 const el = document.getElementById('actionsContent');

 // Add loading indicator

 const aiLoading = document.createElement('div');

 aiLoading.className = 'ai-loading-inline';

 aiLoading.id = 'aiLoadingIndicator';

 aiLoading.textContent = ' AI is analyzing your picks...';

 el.prepend(aiLoading);



 aiEnhanceActions(d.actions).then(() => {

 const indicator = document.getElementById('aiLoadingIndicator');

 if (indicator) indicator.remove();

 });

 }

};



// ============================================================

// CRYPTO Load crypto prices (on commodities tab)

// ============================================================

const _originalLoadCommodities = loadCommodities;

loadCommodities = async function() {

 await _originalLoadCommodities();

 // Also load crypto after commodities

 try {

 const r = await fetch('/api/crypto');

 const j = await r.json();

 if (j.status === 'ok' && j.data && j.data.length > 0) {
 lastCryptoData=j.data;
 const el = document.getElementById('commoditiesContent');

 let h = el.innerHTML;

 h += `<div style="margin-top:24px"><h3 style="margin-bottom:12px"> Crypto Top 25</h3></div>`;

 h += '<div class="crypto-grid">';

 j.data.forEach(c => {

 const icon = CRYPTO_ICONS[c.name] || '';

 h += `<div class="crypto-card">

 <div style="font-size:1.4rem;margin-bottom:4px">${icon}</div>

 <div class="crypto-name">${c.name}</div>

 <div class="crypto-price">${fmtMoney(c.price)}</div>

 <div class="crypto-change ${cc(c.change)}">${ci(c.change)} ${fc(c.change)}</div>

 ${c.pct_1w != null ? `<div style="font-size:0.75rem;color:var(--text-muted);margin-top:2px">Week: <span class="${cc(c.pct_1w)}">${fc(c.pct_1w)}</span></div>` : ''}

 </div>`;

 });

 h += '</div>';

 el.innerHTML = h;

 }

 } catch(e) { console.log('Crypto load failed:', e.message); }

};



// Init

checkAIStatus();




// ============================================================
// MOBILE: Compact ticker rows + detail bottom sheet
// ============================================================
const isMobile = () => window.innerWidth <= 768;
let _actionsDataForMobile = null;

function openStockDetail(idx) {
    const a = _actionsDataForMobile[idx];
    if (!a) return;
    const el = document.getElementById('stockDetailContent');
    const changeCls = (a.pct_1w||0) >= 0 ? 'positive' : 'negative';
    const changeSign = (a.pct_1w||0) >= 0 ? '+' : '';
    el.innerHTML = '<div class="detail-handle"></div>' +
        '<div class="detail-header"><div><div class="detail-ticker">' + a.ticker + '</div>' +
        '<div class="detail-name">' + a.name + ' <span class="badge badge-' + (a.market==='US'?'blue':'yellow') + '" style="font-size:0.55rem">' + a.market + '</span></div></div>' +
        '<div style="text-align:right"><div class="detail-price">' + fmtMoney(a.price) + '</div>' +
        '<div class="' + changeCls + '" style="font-size:0.8rem;font-weight:600">' + changeSign + (a.pct_1w||0).toFixed(1) + '% week</div></div></div>' +
        '<div class="detail-grid">' +
        '<div class="detail-item"><div class="label">Invest</div><div class="value">' + fmtMoney(a.invest_amount) + '</div></div>' +
        '<div class="detail-item"><div class="label">Shares</div><div class="value">' + a.shares.toFixed(4) + '</div></div>' +
        '<div class="detail-item"><div class="label">Target</div><div class="value positive">' + fmtMoney(a.target_price) + ' (+' + a.potential_gain_pct + '%)</div></div>' +
        '<div class="detail-item"><div class="label">Stop Loss</div><div class="value negative">' + fmtMoney(a.stop_loss) + ' (' + a.potential_loss_pct + '%)</div></div>' +
        '<div class="detail-item"><div class="label">Score</div><div class="value">' + a.score + '</div></div>' +
        '<div class="detail-item"><div class="label">RSI</div><div class="value">' + a.rsi + '</div></div>' +
        '</div>' +
        (a.reason ? '<div class="detail-reason">' + a.reason + '</div>' : '') +
        '<div class="detail-actions">' +
        '<button class="btn" onclick="addFromSearch(\'' + a.ticker + '\',' + a.price + ');closeStockDetail()">+ Add to Portfolio</button>' +
        '<button class="btn" onclick="closeStockDetail()">Close</button></div>';
    document.getElementById('stockDetailModal').style.display = 'flex';
}

function closeStockDetail() {
    document.getElementById('stockDetailModal').style.display = 'none';
}

// Inject mobile compact rows after renderActions
const _origRenderForMobile = renderActions;
renderActions = function(d) {
    _origRenderForMobile(d);
    if (!isMobile()) return;
    _actionsDataForMobile = d.actions;
    // Add compact rows after the action cards
    const el = document.getElementById('actionsContent');
    let mobileHtml = '';

    // BUY section with header
    if (d.actions && d.actions.length > 0) {
        mobileHtml += '<div class="mobile-section-header buy-header">📈 <strong>BUY</strong> — ' + d.actions.length + ' picks</div>';
        d.actions.forEach(function(a, i) {
            var changeCls = (a.pct_1w||0) >= 0 ? 'positive' : 'negative';
            var changeSign = (a.pct_1w||0) >= 0 ? '+' : '';
            mobileHtml += '<div class="mobile-ticker-row buy-row" onclick="openStockDetail(' + i + ')">' +
                '<div class="ticker-left">' +
                '<span class="ticker-symbol">' + a.ticker + '</span>' +
                '<span class="ticker-name">' + a.name + '</span>' +
                '<span class="ticker-badge" style="background:var(--green-bg);color:var(--green)">BUY</span>' +
                '</div>' +
                '<div class="ticker-right">' +
                '<div class="ticker-price">' + fmtMoney(a.price) + '</div>' +
                '<div class="ticker-change ' + changeCls + '">' + changeSign + (a.pct_1w||0).toFixed(1) + '%</div>' +
                '</div></div>';
        });
    }

    // SELL/AVOID section with header
    if (d.sell_alerts && d.sell_alerts.length > 0) {
        mobileHtml += '<div class="mobile-section-header sell-header">📉 <strong>SELL / AVOID</strong> — ' + d.sell_alerts.length + ' warnings</div>';
        d.sell_alerts.forEach(function(s) {
            var changeCls = (s.pct_1w||0) >= 0 ? 'positive' : 'negative';
            var changeSign = (s.pct_1w||0) >= 0 ? '+' : '';
            mobileHtml += '<div class="mobile-ticker-row ' + (s.action==='SELL'?'sell-row':'avoid-row') + '">' +
                '<div class="ticker-left">' +
                '<span class="ticker-symbol">' + s.ticker + '</span>' +
                '<span class="ticker-name">' + s.name + '</span>' +
                '<span class="ticker-badge" style="background:var(--red-bg);color:var(--red)">' + s.action + '</span>' +
                '</div>' +
                '<div class="ticker-right">' +
                '<div class="ticker-price">' + fmtMoney(s.price) + '</div>' +
                '<div class="ticker-change ' + changeCls + '">' + changeSign + (s.pct_1w||0).toFixed(1) + '%</div>' +
                '</div></div>';
        });
    }
    if (mobileHtml) el.innerHTML += mobileHtml;
};






// ============================================================
// CHARTS — Chart.js visualizations
// ============================================================
var compoundChart = null;
var portfolioChart = null;

function renderCompoundChart(data, mode) {
    // Destroy previous chart if exists
    if (compoundChart) { compoundChart.destroy(); compoundChart = null; }

    // Create canvas if not exists
    var container = document.getElementById('compoundResult');
    var existingCanvas = document.getElementById('compoundChartCanvas');
    if (existingCanvas) existingCanvas.parentElement.remove();

    var wrapper = document.createElement('div');
    wrapper.style.cssText = 'margin-top:16px;padding:16px;background:var(--bg);border:1px solid var(--border);border-radius:12px;position:relative;height:280px';
    wrapper.innerHTML = '<canvas id="compoundChartCanvas"></canvas>';
    container.appendChild(wrapper);

    var ctx = document.getElementById('compoundChartCanvas').getContext('2d');
    var datasets = [];
    var labels = [];

    if (mode === 'montecarlo') {
        var mc = data;
        labels = mc.median_path.map(function(p) { return 'M' + p.month; });
        datasets = [
            { label: '90th Percentile (Best 10%)', data: mc.p90_path.map(function(p){return p.value;}), borderColor: '#34C759', backgroundColor: 'rgba(52,199,89,0.08)', borderWidth: 1.5, pointRadius: 0, fill: '+1', tension: 0.3 },
            { label: 'Median (Most Likely)', data: mc.median_path.map(function(p){return p.value;}), borderColor: '#007AFF', backgroundColor: 'rgba(0,122,255,0.05)', borderWidth: 2.5, pointRadius: 0, fill: false, tension: 0.3 },
            { label: '10th Percentile (Worst 10%)', data: mc.p10_path.map(function(p){return p.value;}), borderColor: '#FF3B30', backgroundColor: 'rgba(255,59,48,0.08)', borderWidth: 1.5, pointRadius: 0, fill: '-1', tension: 0.3 },
            { label: 'Total Invested', data: mc.median_path.map(function(p,i){return mc.median_path[0].value + (mc.median_path[mc.median_path.length-1].value > mc.median_path[0].value ? (mc.total_invested - mc.median_path[0].value) * i / (mc.median_path.length-1) : 0);}), borderColor: '#86868b', backgroundColor: 'transparent', borderWidth: 1, borderDash: [5,5], pointRadius: 0, fill: false, tension: 0 }
        ];
        // Fix invested line to use actual invested amounts
        var initVal = mc.median_path[0].value;
        var monthlyContrib = (mc.total_invested - initVal) / (mc.median_path.length - 1);
        datasets[3].data = mc.median_path.map(function(p, i) { return Math.round((initVal + monthlyContrib * i) * 100) / 100; });
    } else {
        var e = data.expected, o = data.optimistic, p = data.pessimistic;
        labels = e.data.map(function(d) { return 'M' + d.month; });
        datasets = [
            { label: 'Optimistic', data: o.data.map(function(d){return d.value;}), borderColor: '#34C759', backgroundColor: 'rgba(52,199,89,0.08)', borderWidth: 1.5, pointRadius: 0, fill: '+1', tension: 0.3 },
            { label: 'Expected', data: e.data.map(function(d){return d.value;}), borderColor: '#007AFF', backgroundColor: 'rgba(0,122,255,0.05)', borderWidth: 2.5, pointRadius: 0, fill: false, tension: 0.3 },
            { label: 'Pessimistic', data: p.data.map(function(d){return d.value;}), borderColor: '#FF3B30', backgroundColor: 'rgba(255,59,48,0.08)', borderWidth: 1.5, pointRadius: 0, fill: '-1', tension: 0.3 },
            { label: 'Total Invested', data: e.data.map(function(d){return d.invested;}), borderColor: '#86868b', backgroundColor: 'transparent', borderWidth: 1, borderDash: [5,5], pointRadius: 0, fill: false, tension: 0 }
        ];
    }

    // Reduce labels for readability
    var step = Math.max(1, Math.floor(labels.length / 12));
    var displayLabels = labels.map(function(l, i) { return i % step === 0 ? l : ''; });

    compoundChart = new Chart(ctx, {
        type: 'line',
        data: { labels: displayLabels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12, font: { size: 11 }, color: '#86868b' } },
                tooltip: {
                    backgroundColor: 'rgba(29,29,31,0.95)', titleColor: '#fff', bodyColor: '#fff', borderColor: '#d2d2d7', borderWidth: 1, padding: 10,
                    callbacks: { label: function(ctx) { return ctx.dataset.label + ': ' + fmtMoney(ctx.raw); } }
                }
            },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#aeaeb2', font: { size: 10 }, maxRotation: 0 } },
                y: { grid: { color: 'rgba(210,210,215,0.3)' }, ticks: { color: '#aeaeb2', font: { size: 10 }, callback: function(v) { return fmtMoney(v); } } }
            }
        }
    });
}

function renderPortfolioChart(simulation) {
    if (!simulation || !simulation.monthly_data) return;

    // Destroy previous chart
    if (portfolioChart) { portfolioChart.destroy(); portfolioChart = null; }

    var container = document.getElementById('portfolioContent');
    var existingCanvas = document.getElementById('portfolioChartCanvas');
    if (existingCanvas) existingCanvas.parentElement.remove();

    var wrapper = document.createElement('div');
    wrapper.id = 'portfolioChartCanvas';
    wrapper.style.cssText = 'margin-top:16px;margin-bottom:16px;padding:16px;background:var(--bg);border:1px solid var(--border);border-radius:12px;position:relative;height:260px';
    wrapper.innerHTML = '<canvas id="portChartCtx"></canvas>';

    // Insert after sim-stats
    var simStats = container.querySelector('.sim-stats');
    if (simStats) simStats.after(wrapper);
    else container.prepend(wrapper);

    var ctx = document.getElementById('portChartCtx').getContext('2d');
    var labels = simulation.monthly_data.map(function(d) { return d.date.substring(5); }); // MM-DD
    var step = Math.max(1, Math.floor(labels.length / 8));
    var displayLabels = labels.map(function(l, i) { return i % step === 0 ? l : ''; });

    portfolioChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: displayLabels,
            datasets: [
                { label: 'Optimistic', data: simulation.optimistic_data.map(function(d){return d.value;}), borderColor: '#34C759', backgroundColor: 'rgba(52,199,89,0.06)', borderWidth: 1.5, pointRadius: 0, fill: '+1', tension: 0.3 },
                { label: 'Expected', data: simulation.monthly_data.map(function(d){return d.value;}), borderColor: '#007AFF', backgroundColor: 'rgba(0,122,255,0.04)', borderWidth: 2.5, pointRadius: 0, fill: false, tension: 0.3 },
                { label: 'Pessimistic', data: simulation.pessimistic_data.map(function(d){return d.value;}), borderColor: '#FF3B30', backgroundColor: 'rgba(255,59,48,0.06)', borderWidth: 1.5, pointRadius: 0, fill: '-1', tension: 0.3 },
                { label: 'Invested', data: simulation.monthly_data.map(function(){return simulation.start_value;}), borderColor: '#86868b', backgroundColor: 'transparent', borderWidth: 1, borderDash: [5,5], pointRadius: 0, fill: false }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12, font: { size: 11 }, color: '#86868b' } },
                tooltip: {
                    backgroundColor: 'rgba(29,29,31,0.95)', titleColor: '#fff', bodyColor: '#fff', borderColor: '#d2d2d7', borderWidth: 1, padding: 10,
                    callbacks: { label: function(ctx) { return ctx.dataset.label + ': ' + fmtMoney(ctx.raw); } }
                }
            },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#aeaeb2', font: { size: 10 }, maxRotation: 0 } },
                y: { grid: { color: 'rgba(210,210,215,0.3)' }, ticks: { color: '#aeaeb2', font: { size: 10 }, callback: function(v) { return fmtMoney(v); } } }
            }
        }
    });
}


