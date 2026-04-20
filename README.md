# 📊 Financial Investment Dashboard

A real-time financial investment dashboard built with Flask and yfinance. Provides market data, technical analysis, stock recommendations, portfolio simulations, commodities tracking, and investment calculators — all accessible from any device on your local network.

![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3+-green) ![Stocks](https://img.shields.io/badge/Stocks-200+-orange) ![License](https://img.shields.io/badge/License-Personal-yellow)

## ✨ Features

| Tab | Description |
|-----|-------------|
| **🎯 Today's Actions** | Personalized buy/sell plan scanning 200+ US & EU stocks with exact shares, costs, stop-losses, and targets |
| **💼 My Holdings** | Full portfolio tracker with buy/sell tracking, trade history, P&L analysis, win rate stats, and AI insights |
| **💰 Goal Calculator** | "I want to make $X" calculator + compound interest simulator |
| **📊 Portfolios** | 3 risk profiles (Conservative/Moderate/Aggressive) with exact buy lists and forward projections |
| **📈 Market & Movers** | Real-time US & EU market indices + biggest daily gainers/losers across 200+ stocks |
| **🏆 Commodities** | Gold, Silver, Oil, Natural Gas, Copper, Platinum, Palladium, Corn, Wheat — real-time futures prices |

### Portfolio Features
- **Buy & Sell tracking** — Record purchases and sales with dates and prices
- **Trade History** — Full log of closed positions with P&L per trade
- **Performance Stats** — Win rate, average return, risk/reward ratio, best/worst trades
- **AI Insights** — Pattern analysis of your trading behavior with actionable advice
- **Export/Import** — Download your portfolio as JSON, import on any device
- **Server Sync** — Save/load portfolio to server for cross-device access

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

## ☁️ Deploy Online (Free)

### Render.com (Recommended)

1. Push this folder to a GitHub repository
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` and deploy
5. Your dashboard will be live at `https://your-app.onrender.com`

> **Note:** Free tier sleeps after 15 min of inactivity (~30s to wake up). Portfolio data in localStorage persists per browser. Use Export/Import for backup.

### Alternative: Manual Deploy

```bash
# Set PORT environment variable
export PORT=5000
# Run with gunicorn (production server)
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## 📁 Project Structure

```
financial_dashboard/
├── app.py                  # Flask web server & API routes (14 endpoints)
├── analysis.py             # Financial analysis engine (200+ stocks, commodities)
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku/Render deployment config
├── render.yaml             # Render.com one-click deploy config
├── README.md               # This file
├── .gitignore              # Git ignore rules
├── data/                   # Portfolio data (auto-created, gitignored)
│   └── portfolio.json      # Saved holdings & trade history
├── templates/
│   └── index.html          # Main HTML template (6 tabs)
└── static/
    ├── style.css           # Dashboard styles (dark theme)
    └── main.js             # Frontend JavaScript (tabs, charts, API calls)
```

## 🔧 Technical Details

- **Data Source:** Yahoo Finance via `yfinance` (no API key needed)
- **Stock Universe:** 120 US stocks + 55 EU stocks + 10 commodity futures + 9 commodity ETFs + 11 sector ETFs + 9 market indices = **200+ instruments**
- **Technical Indicators:** RSI (14), MACD (12/26/9), SMA (20/50), volume ratio
- **Scoring System:** -100 to +100 combining RSI, MACD, SMA crossovers, momentum, and volume
- **Caching:** In-memory cache with 10-minute TTL to avoid rate limiting
- **Retry Logic:** Automatic retries with exponential backoff for failed downloads
- **SSL Fix:** Built-in `certifi` certificate handling for macOS compatibility
- **Threading:** Concurrent downloads (12 workers) for faster data fetching
- **Portfolio Persistence:** localStorage (browser) + JSON file (server) + Export/Import (manual)

### Stock Coverage

| Market | Count | Examples |
|--------|-------|---------|
| US Blue Chips | 50 | AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA... |
| US Growth/Tech | 25 | UBER, SHOP, PLTR, CRWD, SNOW, NET, PANW... |
| US Biotech | 11 | MRNA, REGN, VRTX, ISRG, AMGN... |
| US Other | 34 | Fintech, EV, Consumer, Defense, Semis, REITs |
| EU Stocks | 55 | ASML, LVMH, SAP, Novo Nordisk, Shell, AstraZeneca... |
| Commodities | 10 | Gold, Silver, Oil, Gas, Copper, Platinum, Wheat... |
| ETFs | 20+ | SPY, QQQ, GLD, SLV, Sector ETFs... |

## 📱 Mobile Support

The dashboard is fully responsive and works on phones/tablets. Access it from any device on the same WiFi network using the Network URL shown when you start the server.

## ⚠️ Disclaimer

This is an educational tool using algorithm-based technical analysis. It is **NOT** professional financial advice. Always do your own research before making investment decisions.
