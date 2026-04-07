"""
LLM EXPERT - Local AI Cricket Analyst
=======================================
Uses Ollama (Mistral/Llama3) for intelligent expert commentary.
No API key needed - runs fully local.

SETUP:
  1. Install Ollama: https://ollama.com
  2. Run: ollama pull mistral
  3. Start: ollama serve
"""
import ollama
import re


# ══════════════════════════════════════════════════════════
#  MODEL CONFIG
# ══════════════════════════════════════════════════════════
PREFERRED_MODELS  = ["mistral", "llama3", "llama3.2", "gemma2", "phi3"]
ACTIVE_MODEL      = None
OLLAMA_OFFLINE    = False   # Set True after first failure - stops spam
OLLAMA_RETRY_AT   = 0       # epoch time when to retry

SYSTEM_PROMPT = """You are JARVIS, an elite IPL 2026 cricket intelligence agent.
You speak in a professional, slightly futuristic tone. Always start with 'Sir,'.
Be concise (2-3 lines max). Give actionable insights, not generic facts.
Focus on: form trends, match impact, strategic decisions, key matchups."""


def get_available_model() -> str | None:
    """Find first available Ollama model. Suppress repeated errors."""
    global ACTIVE_MODEL, OLLAMA_OFFLINE, OLLAMA_RETRY_AT
    import time as _time
    if ACTIVE_MODEL:
        return ACTIVE_MODEL
    # Offline cache - don't spam errors, retry every 10 min
    if OLLAMA_OFFLINE and _time.time() < OLLAMA_RETRY_AT:
        return None
    try:
        models = ollama.list()
        available = [m["name"].split(":")[0] for m in models.get("models", [])]
        for preferred in PREFERRED_MODELS:
            if preferred in available:
                ACTIVE_MODEL   = preferred
                OLLAMA_OFFLINE = False
                print(f"[LLM] Online: {preferred}")
                return preferred
        if available:
            ACTIVE_MODEL = available[0]
            return available[0]
    except Exception:
        if not OLLAMA_OFFLINE:
            print("[LLM] Offline - using rule-based fallback (silent from now on)")
        OLLAMA_OFFLINE  = True
        OLLAMA_RETRY_AT = _time.time() + 600  # retry in 10 min
    return None


def llm_query(prompt: str, max_tokens: int = 200) -> str | None:
    """
    Send query to local LLM. Returns None if Ollama offline.
    """
    model = get_available_model()
    if not model:
        return None
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            options={"num_predict": max_tokens, "temperature": 0.7},
        )
        text = response["message"]["content"].strip()
        # Clean up
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return None


# ══════════════════════════════════════════════════════════
#  EXPERT ANALYSIS FUNCTIONS
# ══════════════════════════════════════════════════════════
def get_expert_analysis(player_name: str, stats: list,
                         predicted_score: int, bowling: bool = False) -> str:
    """
    Full expert analysis on a player using LLM.
    Falls back to rule-based if Ollama offline.
    """
    if bowling:
        prompt = (f"IPL 2026 bowler analysis. Player: {player_name}. "
                  f"Recent wickets per match: {stats}. "
                  f"ML predicts {predicted_score} wickets next match. "
                  f"Give 2-line expert bowling assessment.")
    else:
        prompt = (f"IPL 2026 batsman analysis. Player: {player_name}. "
                  f"Recent innings scores: {stats}. "
                  f"ML predicts {predicted_score} runs next match. "
                  f"Give 2-line expert batting assessment and fantasy recommendation.")

    result = llm_query(prompt)
    if result:
        return result

    # Fallback: rule-based analysis
    return _rule_based_analysis(player_name, stats, predicted_score, bowling)


def get_match_insight(match: str, score_data: dict) -> str:
    """Expert match situation commentary."""
    runs     = score_data.get("runs", 0)
    wickets  = score_data.get("wickets", 0)
    overs    = score_data.get("overs", 0)
    target   = score_data.get("target", 0)
    win_pct  = score_data.get("win_percent", 50)

    prompt = (f"IPL 2026 match: {match}. "
              f"Score: {runs}/{wickets} in {overs} overs. "
              f"{'Target: ' + str(target) + '.' if target else 'First innings.'} "
              f"Win probability: {win_pct}%. "
              f"Give 2-line strategic insight on match situation.")

    result = llm_query(prompt)
    return result or _rule_based_match(runs, wickets, overs, target, win_pct)


def get_fantasy_insight(match: str, players: list, pitch: str = "") -> str:
    """Fantasy team expert recommendation."""
    prompt = (f"IPL 2026 fantasy team for {match}. "
              f"In-form players available: {', '.join(players[:8])}. "
              f"{'Pitch: ' + pitch if pitch else ''} "
              f"Recommend captain, vice-captain and 2 differentials in 2 lines.")

    result = llm_query(prompt)
    return result or f"Sir, from the available players, focus on top-order batsmen and death-over specialists for {match}."


def get_h2h_insight(team1: str, team2: str, h2h_data: str) -> str:
    """Head to head strategic insight."""
    prompt = (f"IPL 2026 match: {team1} vs {team2}. "
              f"Head to head history: {h2h_data}. "
              f"Give 2-line strategic assessment of this rivalry and today's edge.")

    result = llm_query(prompt)
    return result or f"Sir, {team1} and {team2} have a competitive history. Current form will be the decisive factor today."


def get_pitch_insight(venue: str, pitch_data: str) -> str:
    """Strategic pitch analysis."""
    prompt = (f"IPL 2026 venue: {venue}. Pitch conditions: {pitch_data}. "
              f"Give 2-line strategic advice on batting order and bowling strategy.")

    result = llm_query(prompt)
    return result or f"Sir, {venue} surface favors the team that adapts quickly. Toss winner has a strategic advantage."


def get_toss_insight(toss_result: str, pitch: str, weather: str) -> str:
    """Toss decision strategic analysis."""
    prompt = (f"IPL 2026 toss: {toss_result}. "
              f"Pitch: {pitch[:100] if pitch else 'unknown'}. "
              f"Weather: {weather[:80] if weather else 'clear'}. "
              f"Analyze the toss decision in 2 lines.")

    result = llm_query(prompt)
    return result or f"Sir, {toss_result}. The toss decision aligns with current conditions."


# ══════════════════════════════════════════════════════════
#  RULE-BASED FALLBACKS (when Ollama offline)
# ══════════════════════════════════════════════════════════
def _rule_based_analysis(player: str, stats: list, predicted: int,
                          bowling: bool = False) -> str:
    if not stats:
        return f"Sir, {player} data insufficient for analysis."

    avg = sum(stats) / len(stats)

    if bowling:
        avg_wkts = round(avg, 1)
        if avg_wkts >= 2.5:
            return (f"Sir, {player} is in excellent bowling form averaging {avg_wkts} wickets. "
                    f"ML projects {predicted} wickets next match. Strong fantasy pick.")
        elif avg_wkts >= 1.5:
            return (f"Sir, {player} is contributing consistently with {avg_wkts} wickets on average. "
                    f"Reliable option. ML prediction: {predicted} wickets.")
        else:
            return (f"Sir, {player} has been below par with {avg_wkts} average wickets. "
                    f"ML projects {predicted}. Monitor conditions before picking.")
    else:
        if avg >= 50:
            return (f"Sir, {player} is in exceptional form averaging {round(avg,1)}. "
                    f"ML projects {predicted} runs. Priority pick for fantasy and betting.")
        elif avg >= 30:
            return (f"Sir, {player} is showing solid form at {round(avg,1)} average. "
                    f"ML projects {predicted} runs. Good fantasy option.")
        else:
            return (f"Sir, {player} has been inconsistent averaging {round(avg,1)}. "
                    f"ML projects {predicted} runs. High risk, potential reward.")


def _rule_based_match(runs: int, wickets: int, overs: float,
                       target: int, win_pct: int) -> str:
    if target:
        needed = target - runs
        return (f"Sir, {win_pct}% win probability. "
                f"Need {needed} more runs. "
                f"{'Strong position' if win_pct > 60 else 'Uphill task' if win_pct < 40 else 'Balanced contest'}.")
    else:
        return (f"Sir, first innings in progress. "
                f"{runs}/{wickets} in {overs} overs. "
                f"{'Strong platform' if wickets <= 2 else 'Need rebuilding' if wickets >= 5 else 'Steady progress'}.")


# ══════════════════════════════════════════════════════════
#  STATUS CHECK
# ══════════════════════════════════════════════════════════
def check_llm_status() -> str:
    model = get_available_model()
    if model:
        return f"LLM online: {model}"
    return "LLM offline — using rule-based fallback"