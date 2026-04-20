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


@app.route("/api/market-regime")
def api_market_regime():
    """Get current market regime (bull/bear/sideways/correction)."""
    try:
        data = _get_cached("market_regime", get_market_regime)
        return safe_jsonify({"status": "ok", "data": data})
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
