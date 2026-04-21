"""
Financial Dashboard - Flask Web Application
Run locally and access from any device on the same network.
Supports 200+ stocks, commodities, portfolio persistence, and trade history.
"""

from flask import Flask, render_template, request, Response
from analysis import (
    get_market_overview,
    get_commodities,
    get_recommendations,
    get_top_movers,
    get_sector_performance,
    get_strategies,
    get_portfolio_simulation,
    calculate_goal,
    get_todays_actions,
    check_holdings,
    analyze_portfolio_holdings,
    search_ticker,
    get_chat_context,
    get_market_regime,
    get_ai_analysis_context,
    get_stock_news,
    get_earnings_info,
    get_portfolio_intelligence,
    ai_is_available,
    ai_analyze_stocks,
    ai_analyze_single,
    combine_scores,
    get_crypto_data,
    CRYPTO_STOCKS,
)
import socket
import traceback
import math
import json
import os
from datetime import datetime

app = Flask(__name__)

# Cache to avoid hammering the API on every page load
_cache = {}
_cache_ttl = 600  # 10 minutes (increased for 200+ tickers)

# Portfolio data file path
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.json")


def _get_cached(key, func, *args, **kwargs):
    """Simple in-memory cache with TTL."""
    now = datetime.now().timestamp()
    if key in _cache:
        data, ts = _cache[key]
        if now - ts < _cache_ttl:
            return data
    data = func(*args, **kwargs)
    _cache[key] = (data, now)
    return data


# ---------------------------------------------------------------------------
# JSON sanitizer — fixes NaN/Infinity which are invalid in JSON
# ---------------------------------------------------------------------------

def _sanitize(obj):
    """Recursively replace NaN/Infinity with None in nested dicts/lists."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_sanitize(v) for v in obj]
    return obj


def safe_jsonify(data, status_code=200):
    """Like Flask's jsonify but sanitizes NaN/Infinity first."""
    clean = _sanitize(data)
    return Response(
        json.dumps(clean, ensure_ascii=False),
        status=status_code,
        mimetype="application/json",
    )


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def _parse_int(value, default, min_val=None, max_val=None):
    """Safely parse an integer query parameter with bounds."""
    try:
        result = int(value) if value is not None else default
    except (ValueError, TypeError):
        result = default
    if min_val is not None:
        result = max(min_val, result)
    if max_val is not None:
        result = min(max_val, result)
    return result


def _parse_float(value, default, min_val=None, max_val=None):
    """Safely parse a float query parameter with bounds."""
    try:
        result = float(value) if value is not None else default
    except (ValueError, TypeError):
        result = default
    if min_val is not None:
        result = max(min_val, result)
    if max_val is not None:
        result = min(max_val, result)
    return result


def _parse_market(value):
    """Validate market filter parameter."""
    allowed = {"all", "us", "eu"}
    val = (value or "all").lower().strip()
    return val if val in allowed else "all"


# ---------------------------------------------------------------------------
# Portfolio persistence helpers
# ---------------------------------------------------------------------------

def _ensure_data_dir():
    """Create data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_portfolio_data():
    """Load portfolio data from JSON file."""
    try:
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return {"holdings": [], "trade_history": []}


def _save_portfolio_data(data):
    """Save portfolio data to JSON file."""
    _ensure_data_dir()
    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/market-overview")
def api_market_overview():
    try:
        data = _get_cached("market_overview", get_market_overview)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/commodities")
def api_commodities():
    try:
        data = _get_cached("commodities", get_commodities)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/recommendations")
def api_recommendations():
    try:
        market = _parse_market(request.args.get("market"))
        top_n = _parse_int(request.args.get("top_n"), 10, min_val=1, max_val=50)
        cache_key = f"recommendations_{market}_{top_n}"
        data = _get_cached(cache_key, get_recommendations, market=market, top_n=top_n)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/top-movers")
def api_top_movers():
    try:
        market = _parse_market(request.args.get("market"))
        cache_key = f"top_movers_{market}"
        data = _get_cached(cache_key, get_top_movers, market=market)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/sectors")
def api_sectors():
    try:
        data = _get_cached("sectors", get_sector_performance)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/strategies")
def api_strategies():
    try:
        data = get_strategies()
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/portfolio")
def api_portfolio():
    try:
        profile = request.args.get("profile", "moderate").lower().strip()
        if profile not in ("conservative", "moderate", "aggressive"):
            profile = "moderate"
        investment = _parse_int(request.args.get("investment"), 10000, min_val=1, max_val=10_000_000)
        timeframe_months = _parse_int(request.args.get("months"), 12, min_val=1, max_val=60)
        max_tickers = _parse_int(request.args.get("tickers"), 0, min_val=0, max_val=20)

        cache_key = f"portfolio_{profile}_{investment}_{timeframe_months}_{max_tickers}"
        data = _get_cached(cache_key, get_portfolio_simulation,
                           profile=profile, investment=investment,
                           timeframe_months=timeframe_months, max_tickers=max_tickers)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/compound")
def api_compound():
    """Compound interest calculator with monthly contributions."""
    try:
        initial = _parse_float(request.args.get("initial"), 1000, min_val=0, max_val=100_000_000)
        monthly = _parse_float(request.args.get("monthly"), 100, min_val=0, max_val=1_000_000)
        months = _parse_int(request.args.get("months"), 12, min_val=1, max_val=600)
        annual_return = _parse_float(request.args.get("return"), 10, min_val=0, max_val=100)

        monthly_rate = (annual_return / 100) / 12
        results = {}
        for label, rate_mult in [("expected", 1.0), ("optimistic", 1.5), ("pessimistic", 0.5)]:
            r = monthly_rate * rate_mult
            value = initial
            data = [{"month": 0, "value": round(value, 2), "invested": round(initial, 2)}]
            total_invested = initial
            for m in range(1, months + 1):
                value = value * (1 + r) + monthly
                total_invested += monthly
                data.append({"month": m, "value": round(value, 2), "invested": round(total_invested, 2)})
            results[label] = {
                "final_value": round(value, 2),
                "total_invested": round(total_invested, 2),
                "profit": round(value - total_invested, 2),
                "return_pct": round((value - total_invested) / total_invested * 100, 2) if total_invested > 0 else 0,
                "data": data,
            }
        return safe_jsonify({"status": "ok", "data": results})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/montecarlo")
def api_montecarlo():
    """Monte Carlo compound interest simulation using historical S&P 500 volatility."""
    try:
        import numpy as np
        initial = _parse_float(request.args.get("initial"), 1000, min_val=0, max_val=100_000_000)
        monthly = _parse_float(request.args.get("monthly"), 100, min_val=0, max_val=1_000_000)
        months = _parse_int(request.args.get("months"), 12, min_val=1, max_val=600)
        annual_return = _parse_float(request.args.get("return"), 10, min_val=0, max_val=100)
        n_sims = 1000

        # Historical S&P 500 stats (annualized)
        # Use user's return as mean, but apply realistic volatility (~15.5%)
        annual_vol = 0.155  # S&P 500 historical volatility
        monthly_mean = (annual_return / 100) / 12
        monthly_vol = annual_vol / (12 ** 0.5)

        # Run simulations
        np.random.seed(None)
        final_values = []
        # For percentile paths, store all paths
        all_paths = np.zeros((n_sims, months + 1))

        for sim in range(n_sims):
            value = initial
            all_paths[sim, 0] = value
            for m in range(1, months + 1):
                monthly_return = np.random.normal(monthly_mean, monthly_vol)
                value = value * (1 + monthly_return) + monthly
                all_paths[sim, m] = value
            final_values.append(value)

        final_values = np.array(final_values)
        total_invested = initial + monthly * months

        # Percentiles
        p10 = float(np.percentile(final_values, 10))
        p25 = float(np.percentile(final_values, 25))
        p50 = float(np.percentile(final_values, 50))
        p75 = float(np.percentile(final_values, 75))
        p90 = float(np.percentile(final_values, 90))

        # Median path for chart
        median_path = []
        p10_path = []
        p90_path = []
        for m in range(months + 1):
            median_path.append({"month": m, "value": round(float(np.percentile(all_paths[:, m], 50)), 2)})
            p10_path.append({"month": m, "value": round(float(np.percentile(all_paths[:, m], 10)), 2)})
            p90_path.append({"month": m, "value": round(float(np.percentile(all_paths[:, m], 90)), 2)})

        # Probability of profit
        prob_profit = float(np.mean(final_values > total_invested) * 100)

        results = {
            "total_invested": round(total_invested, 2),
            "median": round(p50, 2),
            "p10": round(p10, 2),
            "p25": round(p25, 2),
            "p75": round(p75, 2),
            "p90": round(p90, 2),
            "median_profit": round(p50 - total_invested, 2),
            "p10_profit": round(p10 - total_invested, 2),
            "p90_profit": round(p90 - total_invested, 2),
            "prob_profit": round(prob_profit, 1),
            "simulations": n_sims,
            "annual_vol_pct": round(annual_vol * 100, 1),
            "median_path": median_path,
            "p10_path": p10_path,
            "p90_path": p90_path,
        }
        return safe_jsonify({"status": "ok", "data": results})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/goal")
def api_goal():
    """Goal calculator: what to invest and where to generate target profit."""
    try:
        target_profit = _parse_float(request.args.get("goal"), 200, min_val=1, max_val=10_000_000)
        months = _parse_int(request.args.get("months"), 1, min_val=1, max_val=60)

        cache_key = f"goal_{target_profit}_{months}"
        data = _get_cached(cache_key, calculate_goal,
                           target_profit=target_profit, months=months)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/todays-actions")
def api_todays_actions():
    """Today's Actions — personalized buy/sell recommendations."""
    try:
        investment = _parse_float(request.args.get("investment"), 1000, min_val=1, max_val=10_000_000)
        strategy = request.args.get("strategy", "best").lower().strip()
        if strategy not in ("quick", "long", "best"):
            strategy = "best"

        cache_key = f"todays_actions_{investment}_{strategy}"
        data = _get_cached(cache_key, get_todays_actions,
                           investment=investment, strategy=strategy)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/check-holdings")
def api_check_holdings():
    """Check health of user's holdings (simple ticker list)."""
    try:
        tickers = request.args.get("tickers", "").strip()
        if not tickers:
            return safe_jsonify({"status": "error", "message": "No tickers provided."}, 400)

        cache_key = f"holdings_{tickers}"
        data = _get_cached(cache_key, check_holdings, tickers_str=tickers)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/analyze-portfolio", methods=["POST"])
def api_analyze_portfolio():
    """Analyze user's portfolio with purchase history (buy price, date, shares)."""
    try:
        body = request.get_json(force=True)
        holdings = body.get("holdings", [])
        trade_history = body.get("trade_history", [])
        if not holdings:
            return safe_jsonify({"status": "error", "message": "No holdings provided."}, 400)

        # Validate and limit
        holdings = holdings[:20]
        trade_history = trade_history[:100]
        data = analyze_portfolio_holdings(holdings, trade_history=trade_history)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


# ---------------------------------------------------------------------------
# Portfolio persistence routes
# ---------------------------------------------------------------------------

@app.route("/api/portfolio-data", methods=["GET"])
def api_get_portfolio_data():
    """Load saved portfolio data (holdings + trade history)."""
    try:
        data = _load_portfolio_data()
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/portfolio-data", methods=["POST"])
def api_save_portfolio_data():
    """Save portfolio data (holdings + trade history) to server."""
    try:
        body = request.get_json(force=True)
        holdings = body.get("holdings", [])
        trade_history = body.get("trade_history", [])

        # Limit sizes
        holdings = holdings[:50]
        trade_history = trade_history[:500]

        data = {"holdings": holdings, "trade_history": trade_history}
        _save_portfolio_data(data)
        return safe_jsonify({"status": "ok", "message": "Portfolio saved"})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


# ---------------------------------------------------------------------------
# Stock Search — any ticker
# ---------------------------------------------------------------------------

@app.route("/api/search")
def api_search():
    """Search and analyze any Yahoo Finance ticker."""
    try:
        ticker = request.args.get("ticker", "").strip().upper()
        if not ticker:
            return safe_jsonify({"status": "error", "message": "No ticker provided."}, 400)
        if len(ticker) > 20:
            return safe_jsonify({"status": "error", "message": "Invalid ticker."}, 400)

        # Use short cache for search results (2 minutes)
        cache_key = f"search_{ticker}"
        now = datetime.now().timestamp()
        if cache_key in _cache:
            data, ts = _cache[cache_key]
            if now - ts < 120:
                return safe_jsonify({"status": "ok", "data": data})

        data = search_ticker(ticker)
        if "error" in data:
            return safe_jsonify({"status": "error", "message": data["error"]}, 404)

        _cache[cache_key] = (data, now)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


# ---------------------------------------------------------------------------
# Chat Context — for AI chatbot
# ---------------------------------------------------------------------------

@app.route("/api/chat-context", methods=["POST"])
def api_chat_context():
    """Build enhanced context for the AI chatbot with market regime and trade patterns."""
    try:
        body = request.get_json(force=True)
        holdings = body.get("holdings", [])
        trade_history = body.get("trade_history", [])

        # Use enhanced AI context (includes market regime + trade patterns)
        ai_context = get_ai_analysis_context(
            holdings=holdings[:20],
            trade_history=trade_history[:50],
        )
        # Also get the role/instructions
        chat_context = get_chat_context(
            holdings=holdings[:20],
            trade_history=trade_history[:50],
        )
        # Combine: AI analysis data + role instructions
        full_context = ai_context + "\n\n" + chat_context
        return safe_jsonify({"status": "ok", "context": full_context})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/news")
def api_news():
    """Get news headlines for a stock ticker."""
    try:
        ticker = request.args.get("ticker", "").strip().upper()
        if not ticker:
            return safe_jsonify({"status": "error", "message": "No ticker provided."}, 400)
        cache_key = f"news_{ticker}"
        now = datetime.now().timestamp()
        if cache_key in _cache:
            data, ts = _cache[cache_key]
            if now - ts < 300:  # 5 min cache for news
                return safe_jsonify({"status": "ok", "data": data})
        data = get_stock_news(ticker)
        _cache[cache_key] = (data, now)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/intelligence", methods=["POST"])
def api_intelligence():
    """Get comprehensive portfolio intelligence: news, earnings, market regime."""
    try:
        body = request.get_json(force=True)
        holdings = body.get("holdings", [])[:10]
        trade_history = body.get("trade_history", [])[:50]
        data = get_portfolio_intelligence(holdings, trade_history)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/market-regime")
def api_market_regime():
    """Get current market regime (bull/bear/sideways/correction)."""
    try:
        data = _get_cached("market_regime", get_market_regime)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


# ---------------------------------------------------------------------------
# AI-Enhanced Analysis Endpoints
# ---------------------------------------------------------------------------

@app.route("/api/autocomplete")
def api_autocomplete():
    """Search stock names and tickers for autocomplete suggestions."""
    from analysis import STOCK_NAMES
    q = request.args.get("q", "").strip().upper()
    if len(q) < 1:
        return safe_jsonify({"status": "ok", "results": []})
    results = []
    for ticker, name in STOCK_NAMES.items():
        if q in ticker.upper() or q in name.upper():
            results.append({"ticker": ticker, "name": name})
            if len(results) >= 10:
                break
    return safe_jsonify({"status": "ok", "results": results})


@app.route("/api/ai-status")
def api_ai_status():
    """Check if server-side AI analysis is available."""
    return safe_jsonify({
        "status": "ok",
        "ai_available": ai_is_available(),
        "model": "llama-3.3-70b-versatile" if ai_is_available() else None,
        "provider": "groq" if ai_is_available() else None,
    })


@app.route("/api/ai-enhance", methods=["POST"])
def api_ai_enhance():
    """AI-enhance a list of stock picks. Adds AI reasoning and combined scores."""
    try:
        if not ai_is_available():
            return safe_jsonify({"status": "ok", "ai_enhanced": False, "results": {}})

        body = request.get_json(force=True)
        stocks = body.get("stocks", [])[:8]
        if not stocks:
            return safe_jsonify({"status": "ok", "ai_enhanced": False, "results": {}})

        # Get market regime for context
        regime = None
        try:
            regime = _get_cached("market_regime", get_market_regime)
        except Exception:
            pass

        # Fetch news for each stock
        for s in stocks:
            ticker = s.get("ticker", "")
            if ticker:
                try:
                    news = get_stock_news(ticker)
                    if news.get("count", 0) > 0:
                        s["news"] = news["headlines"][:3]
                except Exception:
                    pass

        # Run AI analysis
        ai_results = ai_analyze_stocks(stocks, market_regime=regime)

        # Combine scores
        for ticker, ai_data in ai_results.items():
            # Find the original stock data to get technical score
            for s in stocks:
                if s.get("ticker", "").upper() == ticker:
                    tech_score = s.get("score", 0)
                    ai_data["combined_score"] = combine_scores(tech_score, ai_data["ai_score"])
                    ai_data["technical_score"] = tech_score
                    break

        return safe_jsonify({
            "status": "ok",
            "ai_enhanced": True,
            "results": ai_results,
        })
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "ok", "ai_enhanced": False, "results": {}, "error": str(e)})


@app.route("/api/crypto")
def api_crypto():
    """Get current crypto prices and daily changes."""
    try:
        data = _get_cached("crypto", get_crypto_data)
        return safe_jsonify({"status": "ok", "data": data})
    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Server-side AI chat — uses GROQ_API_KEY so users don't need their own key."""
    try:
        if not ai_is_available():
            return safe_jsonify({"status": "error", "message": "AI not configured. Set GROQ_API_KEY on server."}, 503)

        body = request.get_json(force=True)
        user_message = body.get("message", "").strip()
        history = body.get("history", [])[:20]  # Limit history
        holdings = body.get("holdings", [])[:20]
        trade_history = body.get("trade_history", [])[:50]

        if not user_message:
            return safe_jsonify({"status": "error", "message": "No message provided."}, 400)

        # Build context
        from analysis import get_chat_context, get_ai_analysis_context, _get_groq_client, STOCK_NAMES
        ai_context = get_ai_analysis_context(holdings=holdings, trade_history=trade_history)
        chat_context = get_chat_context(holdings=holdings, trade_history=trade_history)

        # --- REAL-TIME DATA INJECTION ---
        # Detect ticker symbols mentioned in the user's message
        import re
        msg_upper = user_message.upper()
        mentioned_tickers = set()

        # 1. Match against our known stock universe
        for ticker in STOCK_NAMES:
            # Match whole-word tickers (avoid matching "A" or "S" in normal words)
            # For short tickers (1-2 chars), require exact match or $ prefix
            if len(ticker) <= 2:
                if f"${ticker}" in msg_upper or f" {ticker} " in f" {msg_upper} ":
                    mentioned_tickers.add(ticker)
            else:
                # For longer tickers, match as whole word
                if re.search(r'\b' + re.escape(ticker) + r'\b', msg_upper):
                    mentioned_tickers.add(ticker)

        # 2. Also detect $TICKER pattern (e.g., "$NVDA")
        dollar_tickers = re.findall(r'\$([A-Z]{1,10}(?:\.[A-Z]{1,2})?(?:-[A-Z]{1,4})?)', msg_upper)
        for t in dollar_tickers:
            mentioned_tickers.add(t)

        # 3. Match company names → resolve to ticker
        # e.g., "Micron Technology" → MU, "Tesla" → TSLA, "Apple" → AAPL
        for ticker, name in STOCK_NAMES.items():
            name_upper = name.upper()
            # Match full company name
            if name_upper in msg_upper:
                mentioned_tickers.add(ticker)
                continue
            # Match first word of company name (if 4+ chars to avoid false positives)
            first_word = name_upper.split()[0]
            if len(first_word) >= 4 and re.search(r'\b' + re.escape(first_word) + r'\b', msg_upper):
                mentioned_tickers.add(ticker)

        # 3. Fetch real-time data for mentioned tickers (limit to 5 to avoid slow responses)
        realtime_context = ""
        if mentioned_tickers:
            realtime_parts = ["\n=== REAL-TIME MARKET DATA (LIVE — use these prices, do NOT guess) ==="]
            for ticker in list(mentioned_tickers)[:5]:
                try:
                    data = search_ticker(ticker)
                    if data and "error" not in data:
                        line = (
                            f"- {data['ticker']} ({data['name']}): "
                            f"Price: ${data['price']}, "
                            f"Daily: {data['daily_change']:+.2f}%, "
                            f"Week: {data['pct_1w']:+.2f}%, "
                            f"Month: {data['pct_1m']:+.2f}%, "
                        )
                        if data.get('pct_3m') is not None:
                            line += f"3M: {data['pct_3m']:+.2f}%, "
                        line += (
                            f"RSI: {data['rsi']}, "
                            f"Score: {data['score']}, "
                            f"Action: {data['action']}, "
                            f"Trend: {data['trend']}"
                        )
                        if data.get('sma_50'):
                            line += f", SMA50: ${data['sma_50']}"
                        if data.get('sma_200'):
                            line += f", SMA200: ${data['sma_200']}"
                        line += f", Target: ${data['target_price']}, Stop-Loss: ${data['stop_loss']}"
                        realtime_parts.append(line)
                except Exception:
                    pass
            if len(realtime_parts) > 1:
                realtime_context = "\n".join(realtime_parts)

        # 4. Also fetch live prices for user's portfolio holdings
        portfolio_prices_context = ""
        if holdings:
            held_tickers = list(set(h.get("ticker", "").upper().strip() for h in holdings if h.get("ticker")))[:10]
            # Only fetch if not already fetched above
            unfetched = [t for t in held_tickers if t not in mentioned_tickers]
            if unfetched:
                portfolio_parts = ["\n=== LIVE PORTFOLIO PRICES ==="]
                for ticker in unfetched[:10]:
                    try:
                        data = search_ticker(ticker)
                        if data and "error" not in data:
                            # Find buy price from holdings
                            buy_info = ""
                            for h in holdings:
                                if h.get("ticker", "").upper().strip() == ticker:
                                    bp = float(h.get("buy_price", 0))
                                    shares = float(h.get("shares", 0))
                                    if bp > 0:
                                        pnl_pct = ((data['price'] - bp) / bp) * 100
                                        buy_info = f", User bought at ${bp:.2f} ({pnl_pct:+.1f}% P&L, {shares} shares)"
                                    break
                            portfolio_parts.append(
                                f"- {data['ticker']}: ${data['price']} "
                                f"(Day: {data['daily_change']:+.2f}%, Week: {data['pct_1w']:+.2f}%, "
                                f"Score: {data['score']}, {data['action']}){buy_info}"
                            )
                    except Exception:
                        pass
                if len(portfolio_parts) > 1:
                    portfolio_prices_context = "\n".join(portfolio_parts)

        system_prompt = (
            ai_context + "\n\n"
            + realtime_context + "\n"
            + portfolio_prices_context + "\n\n"
            + chat_context
            + "\n\nCRITICAL RULES:"
            + "\n1. ALWAYS use the real-time prices provided above. NEVER guess, estimate, or use memorized stock prices."
            + "\n2. If a stock's live data is provided, cite the exact price and metrics."
            + "\n3. If asked about a stock NOT in the data above, say 'I don't have live data for that ticker right now — use the search bar to look it up.'"
            + "\n4. Be confident, specific, and actionable. Use ticker symbols and numbers."
            + "\n5. Keep responses to 3-5 sentences unless asked for more detail."
            + "\n6. Always end with a brief disclaimer."
        )

        client = _get_groq_client()
        if not client:
            return safe_jsonify({"status": "error", "message": "AI client not available."}, 503)

        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        for h in history[-10:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )

        reply = response.choices[0].message.content.strip() if response.choices else "No response."
        return safe_jsonify({"status": "ok", "reply": reply})

    except Exception as e:
        traceback.print_exc()
        return safe_jsonify({"status": "error", "message": str(e)}, 500)


@app.route("/api/clear-cache", methods=["POST"])
def api_clear_cache():
    _cache.clear()
    return safe_jsonify({"status": "ok", "message": "Cache cleared"})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def get_local_ip():
    """Get the local network IP so you can access from phone."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    _ensure_data_dir()
    local_ip = get_local_ip()
    port = 5000
    print("=" * 60)
    print("  📊 Financial Investment Dashboard")
    print("=" * 60)
    print(f"  Local:   http://localhost:{port}")
    print(f"  Network: http://{local_ip}:{port}  (for phone/other PC)")
    print("=" * 60)
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
