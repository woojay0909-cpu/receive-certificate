import random
import numpy as np
import pandas as pd
import datetime as dt
from typing import Optional, Dict

class MarketData:
    """Mock market data. Replace methods with real data fetchers (yfinance, ccxt, etc.)."""
    def get_latest_price(self, symbol: str) -> float:
        base = {"EUR/USD": 1.1000, "GBP/USD": 1.2600}.get(symbol, 1.0)
        return base + random.uniform(-0.0025, 0.0025)

class Sentiment:
    """Stub sentiment. Replace with NewsAPI / custom NLP later."""
    def get_sentiment_score(self, symbol: str) -> float:
        return float(np.clip( np.random.normal(0, 0.15), -1.0, 1.0 ))

class Cosmic:
    """Mock cosmic modifiers. Replace with real ephemeris data or NOAA/NASA feeds if desired."""
    def get_cosmic_modifier(self, symbol: str, when: dt.datetime = None) -> float:
        if when is None: when = dt.datetime.utcnow()
        # Simple, deterministic-ish modifier: uses hour to create a slow wave
        h = when.hour + when.minute/60.0
        modifier = 1.0 + 0.06 * np.sin(h/24.0 * 2*np.pi + (0 if symbol=="EUR/USD" else 0.5))
        return float(modifier)

class Strategy:
    """Example: SMA momentum + sentiment + cosmic importance -> signal generator."""
    def __init__(self):
        self.lookback = 50  # used if fetching historical data

    def compute_confidence(self, price: float, sentiment: float, cosmic: float) -> float:
        # blend deterministic components into [0,1]
        p_score = 0.5  # placeholder (if we had momentum it'd adjust this)
        s_score = 0.5 + 0.5 * sentiment  # sentiment in [-1,1]
        c_score = cosmic - 0.9  # cosmic in ~[0.94,1.12] -> normalize
        raw = (p_score*0.4) + (s_score*0.4) + (c_score*0.2)
        return float(np.clip(raw, 0.05, 0.99))

    def decide(self, price: float, sentiment: float, cosmic: float) -> Optional[Dict]:
        # Simple decision: sentiment drives side, cosmic nudges confidence
        if abs(sentiment) < 0.15:
            return None  # no clear sentiment => no signal

        side = "buy" if sentiment > 0 else "sell"
        conf = self.compute_confidence(price, sentiment, cosmic)
        reason = f"sentiment={sentiment:.2f}, cosmic={cosmic:.3f}"
        return {"side": side, "confidence": conf, "reason": reason}

class SignalEngine:
    def __init__(self, symbols=None):
        self.symbols = symbols or ["EUR/USD","GBP/USD"]
        self.market = MarketData()
        self.sent = Sentiment()
        self.cos = Cosmic()
        self.strat = Strategy()

    def generate_signal_now(self):
        # choose symbol(s) to evaluate; we return the strongest signal if any
        candidates = []
        for s in self.symbols:
            price = self.market.get_latest_price(s)
            sentiment = self.sent.get_sentiment_score(s)
            cosmic_mod = self.cos.get_cosmic_modifier(s)
            decision = self.strat.decide(price, sentiment, cosmic_mod)
            if decision:
                decision.update({"symbol": s, "price": price})
                candidates.append(decision)
        if not candidates:
            return None
        # pick highest confidence
        chosen = max(candidates, key=lambda x: x["confidence"])
        return chosen