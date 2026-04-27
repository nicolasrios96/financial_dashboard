"""
AI Analysis Engine — Groq Integration (70% AI / 30% Technical)
Handles AI-powered stock analysis, sentiment scoring, and reasoning.
"""

import os
import json
from datetime import datetime


# ---------------------------------------------------------------------------
# Groq Client (lazy-initialized)
# ---------------------------------------------------------------------------

_groq_client = None
_ai_cache = {}
_ai_cache_ttl = 1800  # 30 minutes


def _get_groq_client():
    """Lazy-initialize the Groq client using OpenAI-compatible SDK."""
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        from openai import OpenAI
        _groq_client = OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        return _groq_client
    except Exception as e:
        print(f"  ⚠️ Could not initialize Groq client: {e}")
        return None


def ai_is_available():
    """Check if AI analysis is available (Groq API key configured)."""
    return bool(os.environ.get("GROQ_API_KEY", ""))


def ai_analyze_stocks(stocks_data, market_regime=None):
    """
    Use Groq AI to analyze a batch of stocks.
    Takes pre-computed technical data and returns AI sentiment + reasoning.

    stocks_data: list of dicts with ticker, name, price, score, rsi, trend, pct_1w, pct_1m, etc.
    market_regime: dict with regime info (bull/bear/sideways)

    Returns: dict mapping ticker -> {ai_score, ai_reasoning, ai_risk, ai_confidence}
    """
    client = _get_groq_client()
    if not client or not stocks_data:
        return {}

    # Check cache
    cache_key = "ai_batch_" + "_".join(sorted(s["ticker"] for s in stocks_data[:8]))
    now = datetime.now().timestamp()
    if cache_key in _ai_cache:
        cached, ts = _ai_cache[cache_key]
        if now - ts < _ai_cache_ttl:
            return cached

    # Build the prompt
    regime_text = ""
    if market_regime and market_regime.get("regime") != "unknown":
        regime_text = f"Market regime: {market_regime['regime'].upper()} — {market_regime.get('description', '')}\n"

    stocks_text = ""
    for s in stocks_data[:8]:
        news_text = ""
        if s.get("news"):
            news_text = " | News: " + "; ".join(n.get("title", "")[:60] for n in s["news"][:3])
        stocks_text += (
            f"- {s['ticker']} ({s['name']}): ${s['price']}, "
            f"Tech Score: {s.get('score', 0)}, RSI: {s.get('rsi', 50)}, "
            f"Trend: {s.get('trend', 'neutral')}, "
            f"Week: {s.get('pct_1w', 0):+.1f}%, Month: {s.get('pct_1m', 0):+.1f}%"
            f"{', 3M: ' + str(round(s['pct_3m'], 1)) + '%' if s.get('pct_3m') is not None else ''}"
            f"{news_text}\n"
        )

    prompt = f"""You are a senior financial analyst. Analyze these stocks and provide your assessment.

{regime_text}
STOCKS TO ANALYZE:
{stocks_text}

For EACH stock, respond in this EXACT JSON format (no markdown, no extra text):
{{
  "TICKER": {{
    "score": <number from -50 to 50, your sentiment score>,
    "reasoning": "<1-2 sentence analysis including fundamentals, sector outlook, catalysts, risks>",
    "risk": "<main risk factor in 5-10 words>",
    "confidence": "<high/medium/low>"
  }}
}}

Rules:
- Positive score = bullish, negative = bearish, 0 = neutral
- Consider news sentiment, sector trends, competitive position, macro factors
- Be honest about risks — don't just agree with technical signals
- If a stock has bad fundamentals but good technicals, flag it
- If a stock is in a declining sector, penalize it regardless of short-term bounce
- Consider the current market regime in your analysis"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a senior financial analyst. Respond ONLY with valid JSON. No markdown, no code blocks, no extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1500,
            temperature=0.3,
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[:-3]
        raw = raw.strip()

        result = json.loads(raw)

        ai_results = {}
        for ticker, data in result.items():
            ticker = ticker.upper().strip()
            ai_score = max(-50, min(50, int(data.get("score", 0))))
            ai_results[ticker] = {
                "ai_score": ai_score,
                "ai_reasoning": str(data.get("reasoning", ""))[:200],
                "ai_risk": str(data.get("risk", ""))[:100],
                "ai_confidence": str(data.get("confidence", "medium")).lower(),
            }

        _ai_cache[cache_key] = (ai_results, now)
        return ai_results

    except json.JSONDecodeError as e:
        print(f"  ⚠️ AI response was not valid JSON: {e}")
        return {}
    except Exception as e:
        print(f"  ⚠️ AI analysis failed: {e}")
        return {}


def ai_analyze_single(ticker, stock_data, news=None, market_regime=None):
    """
    AI analysis for a single stock (used in search and portfolio analysis).
    Returns: {ai_score, ai_reasoning, ai_risk, ai_confidence} or empty dict.
    """
    enriched = dict(stock_data)
    if news:
        enriched["news"] = news
    results = ai_analyze_stocks([enriched], market_regime=market_regime)
    return results.get(ticker.upper(), {})


def combine_scores(technical_score, ai_score):
    """
    Combine technical and AI scores with 70/30 AI/Technical weighting.
    Returns combined score clamped to -100..100.
    """
    ai_scaled = ai_score * 2
    combined = (0.30 * technical_score) + (0.70 * ai_scaled)
    return max(-100, min(100, round(combined)))
