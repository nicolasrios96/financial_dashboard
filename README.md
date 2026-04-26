# 📊 Financial Investment Dashboard

A real-time financial investment dashboard built with Flask and yfinance. Provides market data, technical analysis, AI-powered stock recommendations, portfolio simulations, commodities & crypto tracking, and investment calculators — all accessible from any device.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3+-green) ![Stocks](https://img.shields.io/badge/Stocks-500+-orange) ![AI](https://img.shields.io/badge/AI-Groq%20Llama%203.3-purple) ![License](https://img.shields.io/badge/License-Personal-yellow)

## ✨ Features

| Tab | Description |
|-----|-------------|
| **🎯 Today's Actions** | Personalized buy/sell plan scanning 500+ US & EU stocks with exact shares, costs, stop-losses, targets, and analyst consensus data |
| **💼 My Holdings** | Full portfolio tracker with buy/sell tracking, trade history, P&L analysis, win rate stats, AI insights, and PIN-based cross-device sync |
| **💰 Goal Calculator** | "I want to make $X" calculator + compound interest simulator + Monte Carlo simulation (1,000 scenarios) |
| **📊 Portfolios** | 3 risk profiles (Conservative/Moderate/Aggressive) with exact buy lists, forward projections, and allocation charts |
| **📈 Market & Movers** | Real-time US & EU market indices + biggest daily gainers/losers across 500+ stocks |
| **🏆 Commodities & Crypto** | Gold, Silver, Oil, Gas, Copper, Platinum + Top 25 cryptocurrencies with daily/weekly changes |

### AI Features (Groq-powered)
- **🤖 AI Chatbot ("Stonks")** — Sarcastic Wall Street veteran with real-time market data, portfolio analysis, and macro context (VIX, Gold, Treasury yields)
- **🧠 AI-Enhanced Picks** — Groq Llama 3.3 70B analyzes top picks with sentiment scoring, risk assessment, and reasoning
- **📊 Analyst Consensus** — Buy/Hold/Sell percentages, 12-month price targets, P/E ratios, earnings growth from Wall Street analysts

### Portfolio Features
- **Buy & Sell tracking** — Record purchases and sales with dates and prices
- **Trade History** — Full log of closed positions with P&L per trade
- **Performance Stats** — Win rate, average return, risk/reward ratio, best/worst trades
- **AI Insights** — Pattern analysis of your trading behavior with actionable advice
- **🔐 PIN Sync** — Save/load portfolio across devices with a secure PIN (bcrypt hashed, rate-limited)
- **Export/Import** — Download your portfolio as JSON or CSV, import on any device
- **USD/EUR Toggle** — Switch currency display with live exchange rate

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd financial_dashboard
pip install -r requirements.txt
```

### 2. Run the dashboard

```bash
python app.py
```

### 3. Open in browser

- **Local:** http://localhost:5000
- **Phone/Other PC:** http://YOUR_IP:5000 (shown in terminal)

### 4. (Optional) Enable AI features

```bash
# Set your Groq API key (free at console.groq.com)
export GROQ_API_KEY=your_key_here
python app.py
```

## ☁️ Deploy Online (Free)

### Render.com (Recommended)

1. Push this folder to a GitHub repository
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` and deploy
5. Set `GROQ_API_KEY` in Render's Environment Variables for AI features
6. Your dashboard will be live at `https://your-app.onrender.com`

> **Note:** Free tier sleeps after 15 min of inactivity (~30s to wake up). Cache warming pre-fetches market data on startup to minimize wait time. Portfolio data in localStorage persists per browser. Use PIN sync or Export/Import for backup.

## 📁 Project Structure

```
financial_dashboard/
├── app.py                  # Flask web server & API routes (20+ endpoints)
├── analysis.py             # Financial analysis engine (500+ stocks, AI, commodities)
├── requirements.txt        # Python dependencies (flask, yfinance, bcrypt, etc.)
├── Procfile                # Render/Heroku deployment config
├── render.yaml             # Render.com one-click deploy config
├── runtime.txt             # Python version specification
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── data/                   # Portfolio data (auto-created, gitignored)
│   ├── portfolio.json      # Saved holdings & trade history (local)
│   └── portfolios.db       # PIN-based portfolio storage (SQLite)
├── templates/
│   └── index.html          # Main HTML template (6 tabs, modals, chat panel)
└── static/
    ├── style.css           # Dashboard styles (Apple-inspired light theme)
    └── main.js             # Frontend JavaScript (tabs, charts, API calls)
```

## 🔧 Technical Details

- **Data Source:** Yahoo Finance via `yfinance` (no API key needed)
- **AI Engine:** Groq (Llama 3.3 70B) for sentiment analysis, chat, and stock reasoning
- **Stock Universe:** 170+ US stocks + 70+ EU stocks + 25 cryptos + 10 commodity futures + 50+ ETFs = **500+ instruments**
- **Technical Indicators:** RSI (14), MACD (12/26/9), SMA (20/50/200), volume ratio, trend detection
- **Scoring System:** -100 to +100 combining RSI, MACD, SMA crossovers, momentum, volume, trend structure, dead cat bounce detection, and analyst consensus adjustment
- **Caching:** In-memory cache with 10-minute TTL + startup cache warming
- **Retry Logic:** Automatic retries with exponential backoff for failed downloads
- **SSL Fix:** Built-in `certifi` certificate handling for macOS compatibility
- **Threading:** Concurrent downloads (10 workers) for balanced speed vs rate limiting
- **Security:** bcrypt PIN hashing, flask-limiter rate limiting (5/min load, 10/min save), IP lockout after 5 failed attempts
- **Portfolio Persistence:** localStorage (browser) + PIN sync (SQLite/bcrypt) + JSON/CSV export/import

### Stock Coverage

| Market | Count | Examples |
|--------|-------|---------|
| US Blue Chips | 50 | AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA... |
| US Growth/Tech | 25 | UBER, SHOP, PLTR, CRWD, SNOW, NET, PANW... |
| US Additional S&P 500 | 70+ | ABBV, INTU, ADP, FDX, TJX, CME, MSCI... |
| US Biotech/Pharma | 11 | MRNA, REGN, VRTX, ISRG, AMGN... |
| US Other | 20+ | Fintech, EV, Consumer, Defense, Semis, REITs, AI/Cloud |
| EU Stocks | 70+ | ASML, LVMH, SAP, Novo Nordisk, Shell, AstraZeneca, Ferrari... |
| Crypto | 25 | BTC, ETH, SOL, XRP, DOGE, AVAX, LINK, UNI... |
| Commodities | 10 | Gold, Silver, Oil, Gas, Copper, Platinum, Wheat... |
| ETFs | 50+ | SPY, QQQ, GLD, SLV, Sector ETFs, EU-domiciled UCITS ETFs... |

### API Endpoints (20+)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/market-overview` | GET | US & EU market indices |
| `/api/commodities` | GET | Commodity futures prices |
| `/api/crypto` | GET | Top 25 crypto prices |
| `/api/recommendations` | GET | Top stock picks by score |
| `/api/top-movers` | GET | Daily gainers & losers |
| `/api/sectors` | GET | Sector ETF performance |
| `/api/todays-actions` | GET | Personalized buy/sell plan |
| `/api/portfolio` | GET | Portfolio simulation |
| `/api/compound` | GET | Compound interest calculator |
| `/api/montecarlo` | GET | Monte Carlo simulation |
| `/api/goal` | GET | Goal calculator |
| `/api/search` | GET | Search any ticker |
| `/api/analyst` | GET | Analyst consensus data |
| `/api/news` | GET | Stock news headlines |
| `/api/autocomplete` | GET | Ticker/name autocomplete |
| `/api/analyze-portfolio` | POST | Portfolio P&L analysis |
| `/api/intelligence` | POST | News + earnings warnings |
| `/api/chat` | POST | AI chatbot (server-side) |
| `/api/ai-enhance` | POST | AI-enhanced stock analysis |
| `/api/portfolio-pin/save` | POST | Save portfolio with PIN |
| `/api/portfolio-pin/load` | POST | Load portfolio from PIN |
| `/api/market-regime` | GET | Bull/bear/correction detection |
| `/api/ai-status` | GET | Check AI availability |

## 📱 Mobile Support

The dashboard is fully responsive and works on phones/tablets. Features include:
- Compact ticker rows with tap-to-expand detail sheets
- Horizontal-scrolling tabs
- Touch-optimized controls
- Full-screen chat panel

Access it from any device on the same WiFi network using the Network URL shown when you start the server.

## ⚠️ Disclaimer

This is an educational tool using algorithm-based technical analysis and AI. It is **NOT** professional financial advice. Always do your own research before making investment decisions.
