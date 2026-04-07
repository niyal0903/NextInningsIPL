"""
ML BRAIN - IPL 2026 Prediction Engine
======================================
Linear Regression + trend analysis for batting and bowling
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import re


# ══════════════════════════════════════════════════════════
#  BATTING SCORE PREDICTOR
# ══════════════════════════════════════════════════════════
def predict_future_score(last_scores: list) -> dict:
    """
    Predict next innings score using ML trend analysis.
    Returns full report dict.
    """
    if not last_scores or len(last_scores) < 3:
        return {"predicted": None, "trend": "unknown", "confidence": "low", "insight": "Not enough data"}

    scores = np.array(last_scores[-10:])  # Use last 10 max
    n = len(scores)
    X = np.arange(n).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, scores)

    predicted = int(max(0, round(model.predict([[n]])[0])))

    # Trend analysis
    slope = model.coef_[0]
    avg   = float(np.mean(scores))
    std   = float(np.std(scores))

    if slope > 3:
        trend = "strongly improving"
    elif slope > 1:
        trend = "improving"
    elif slope > -1:
        trend = "consistent"
    elif slope > -3:
        trend = "declining"
    else:
        trend = "poor form"

    # Confidence based on consistency
    cv = (std / avg * 100) if avg > 0 else 100
    if cv < 30:
        confidence = "high"
    elif cv < 60:
        confidence = "medium"
    else:
        confidence = "low"

    # Recent form (last 3)
    recent = scores[-3:].tolist()
    recent_avg = round(float(np.mean(recent)), 1)

    # Peak and floor
    peak  = int(max(scores))
    floor = int(min(scores))

    return {
        "predicted":    predicted,
        "trend":        trend,
        "confidence":   confidence,
        "average":      round(avg, 1),
        "recent_avg":   recent_avg,
        "peak":         peak,
        "floor":        floor,
        "slope":        round(float(slope), 2),
        "scores_used":  scores.tolist(),
    }


# ══════════════════════════════════════════════════════════
#  BOWLING WICKET PREDICTOR
# ══════════════════════════════════════════════════════════
def predict_future_wickets(last_wickets: list, last_economies: list = None) -> dict:
    """
    Predict next match wickets using bowling history.
    """
    if not last_wickets or len(last_wickets) < 3:
        return {"predicted": None, "trend": "unknown", "confidence": "low"}

    wkts = np.array(last_wickets[-10:])
    n    = len(wkts)
    X    = np.arange(n).reshape(-1, 1)

    model = LinearRegression()
    model.fit(X, wkts)
    predicted = int(max(0, round(model.predict([[n]])[0])))

    slope = model.coef_[0]
    avg   = float(np.mean(wkts))
    std   = float(np.std(wkts))

    trend = ("improving" if slope > 0.1 else
             "declining" if slope < -0.1 else "consistent")

    cv = (std / avg * 100) if avg > 0 else 100
    confidence = "high" if cv < 50 else "medium" if cv < 80 else "low"

    result = {
        "predicted":  predicted,
        "trend":      trend,
        "confidence": confidence,
        "average":    round(avg, 1),
        "peak":       int(max(wkts)),
    }

    # Economy analysis
    if last_economies and len(last_economies) >= 3:
        ecos = np.array(last_economies[-10:])
        eco_avg = round(float(np.mean(ecos)), 2)
        eco_model = LinearRegression()
        eco_model.fit(np.arange(len(ecos)).reshape(-1, 1), ecos)
        eco_pred = round(float(eco_model.predict([[len(ecos)]])[0]), 2)
        result["economy_avg"]       = eco_avg
        result["economy_predicted"] = max(4.0, eco_pred)
        result["economy_trend"]     = ("improving" if eco_model.coef_[0] < -0.1 else
                                       "worsening" if eco_model.coef_[0] > 0.1 else "stable")

    return result


# ══════════════════════════════════════════════════════════
#  WIN PROBABILITY CALCULATOR
# ══════════════════════════════════════════════════════════
def calculate_win_probability(runs: int, wickets: int, overs: float,
                               target: int = 0, venue_avg: int = 170) -> dict:
    """
    Advanced win probability using multiple factors.
    """
    balls_done = int(overs) * 6 + round((overs % 1) * 10)
    balls_left = max(1, 120 - balls_done)
    curr_rr    = round(runs / overs, 2) if overs > 0 else 0

    if target > 0:
        # Chasing
        runs_needed = max(1, target - runs)
        req_rr      = round(runs_needed / balls_left * 6, 2)
        rr_gap      = curr_rr - req_rr

        base_chance  = 50 + rr_gap * 6
        wicket_pen   = wickets * 7
        ball_factor  = (balls_left / 120) * 5
        chance       = base_chance - wicket_pen + ball_factor

        status = ("comfortable" if rr_gap > 1 else
                  "close"       if rr_gap > -1 else
                  "difficult"   if rr_gap > -3 else "very difficult")

        return {
            "win_percent":  max(5, min(95, round(chance))),
            "status":       status,
            "req_rr":       req_rr,
            "curr_rr":      curr_rr,
            "runs_needed":  runs_needed,
            "balls_left":   balls_left,
        }
    else:
        # Batting first — project and compare to venue avg
        remaining    = max(1, 20 - overs)
        wkt_factor   = max(0.55, 1 - wickets * 0.06)
        proj         = int(round(runs + curr_rr * remaining * wkt_factor))
        chance       = 50 + (proj - venue_avg) * 0.8 - wickets * 3
        return {
            "win_percent":   max(5, min(95, round(chance))),
            "projected":     proj,
            "venue_avg":     venue_avg,
            "curr_rr":       curr_rr,
        }


# ══════════════════════════════════════════════════════════
#  EXTRACT SCORES FROM TEXT
# ══════════════════════════════════════════════════════════
def extract_scores_from_text(text: str, max_val: int = 180) -> list:
    """Extract plausible cricket scores from raw text."""
    scores = []
    # Pattern: "scored 67", "made 45 off", "hit 83", "struck 109"
    for h in re.findall(r'(?:scored|made|hit|smashed|struck|notched)\s+(\d{1,3})',
                        text, re.IGNORECASE):
        v = int(h)
        if 0 < v < max_val:
            scores.append(v)
    # Pattern: "67 off 43 balls"
    for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', text):
        v = int(h)
        if 0 < v < max_val:
            scores.append(v)
    return list(dict.fromkeys(scores))


def extract_wickets_from_text(text: str) -> tuple:
    """Extract bowling figures (wickets, economy) from text."""
    wickets = []
    economies = []
    for w, r in re.findall(r'\b([0-5])/(\d{1,3})\b', text):
        wv, rv = int(w), int(r)
        if rv < 80:
            wickets.append(wv)
            economies.append(round(rv / 4, 1))
    return wickets, economies