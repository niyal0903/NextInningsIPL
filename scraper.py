"""
DATA SCRAPER - IPL 2026 Fresh Data Engine
==========================================
DDGS-based scraper with smart parsing.
No browser automation needed — pure search API.
"""
import re
import time
from ddgs import DDGS
from ml_brain import extract_scores_from_text, extract_wickets_from_text


# ══════════════════════════════════════════════════════════
#  JUNK DETECTION
# ══════════════════════════════════════════════════════════
JUNK_WORDS = [
    "cricbuzz","cricinfo","espncricinfo","ndtv","hindustantimes",
    "timesofindia","view the","click here","read more","subscribe",
    "sign up","get ipl","explore","stay updated","find out","mykhel",
    "check out","ipl points table 2026","complete schedule",
]
LIVE_WORDS     = ["live score","live cricket","live update","toss result",
                  "playing 11","match preview","dream11","fantasy","ball by ball"]
RESULT_WORDS   = ["won","beat","defeated","won by","victory","chase","bowled out"]
HIGHLIGHT_WORDS= ["highlights","crush","beat","win","lost","defeated","thrash",
                  "stars","century","wicket haul","clinch","seal","qualify"]

GLUED_RE = re.compile(
    r'(?:teamsin|racethe|tablein|pointsin|seasonin|matchin|playoffrace|'
    r'topteam|leaguein|playersin|wicketin|runsin|scorein|overin|ballin)',
    re.IGNORECASE
)

def is_junk(line: str) -> bool:
    ll = line.lower()
    if any(jw in ll for jw in JUNK_WORDS): return True
    if GLUED_RE.search(line): return True
    # CamelCase glued detection
    for w in line.split():
        wa = re.sub(r'[^a-zA-Z]', '', w)
        if len(re.findall(r'[a-z][A-Z]', wa)) >= 2:
            return True
    if re.match(r'^[\d\s\-/:]+$', line): return True
    return False

def clean(text: str) -> str:
    text = re.sub(r'\b\d+\s+(?:hours?|minutes?|days?)\s+ago\b', '', text, flags=re.IGNORECASE)
    text = re.sub(
        r'(Cricbuzz|Cricinfo|ESPNcricinfo|NDTV|Hindustan\s*Times|Times\s*of\s*India'
        r'|IPL\s*2026\s*[Ss]chedule|View\s+the|Click\s+here|Read\s+more'
        r'|Get\s+IPL|Explore|Stay\s+updated|myKhel|check\s+out)',
        '', text, flags=re.IGNORECASE
    )
    text = re.sub(r'^[-–\s]+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ══════════════════════════════════════════════════════════
#  SEARCH ENGINE
# ══════════════════════════════════════════════════════════
def search(query: str, mode: str = "news", days: str = "w",
           n: int = 8, retries: int = 3) -> list:
    for attempt in range(retries):
        try:
            with DDGS() as d:
                if mode == "news":
                    r = list(d.news(query, region="in-en", timelimit=days, max_results=n))
                    return r if r else list(d.news(query, region="in-en", max_results=n))
                return list(d.text(query, region="in-en", max_results=n))
        except Exception as e:
            err = str(e)
            if "DecodeError" in err or "Body collection" in err:
                wait = 2 * (attempt + 1)
                print(f"  [Retry {attempt+1}/{retries}] waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [Search] {err[:60]}")
                break
    return []

def all_text(res: list) -> str:
    return " ".join(r.get("title", "") + " " + r.get("body", "") for r in res)

def best_sentences(results: list, keywords: list,
                   count: int = 2, min_len: int = 20, max_len: int = 250) -> list:
    found = []
    for r in results:
        for src in [r.get("body", ""), r.get("title", "")]:
            for line in re.split(r'[.\n]', src):
                line = line.strip()
                if not (min_len < len(line) < max_len): continue
                if is_junk(line): continue
                for kw in keywords:
                    if kw.lower() in line.lower():
                        cl = clean(line)
                        if cl and cl not in found:
                            found.append(cl)
                        break
        if len(found) >= count:
            break
    return found


# ══════════════════════════════════════════════════════════
#  LIVE SCORECARD
# ══════════════════════════════════════════════════════════
def get_live_scorecard() -> dict | None:
    queries = [
        "IPL 2026 live score today match batting overs wickets",
        "IPL 2026 live scorecard today innings runs",
        "IPL 2026 today match score update live",
    ]
    for q in queries:
        res = search(q, mode="news", days="d", n=12)
        sources = [r.get("title", "") + " " + r.get("body", "") for r in res]
        txt = " ".join(sources)
        if not txt:
            continue

        data = {}
        m = (re.search(r'(\d{2,3})/(\d)\b', txt) or
             re.search(r'(\d{2,3})\s+for\s+(\d)\b', txt))
        if m:
            data["runs"]    = int(m.group(1))
            data["wickets"] = int(m.group(2))

        for pat in [r'(\d{1,2}\.\d)\s*(?:ov|overs?)',
                    r'after\s+(\d{1,2}\.?\d?)\s*overs?']:
            om = re.search(pat, txt, re.IGNORECASE)
            if om:
                try: data["overs"] = float(om.group(1)); break
                except: pass

        if data.get("runs") and data.get("overs", 0) > 0:
            data["run_rate"] = round(data["runs"] / data["overs"], 2)

        for pat, key in [
            (r'(?:required|RRR)[:\s]*(\d{1,2}\.\d{1,2})', "req_rate"),
            (r'target[:\s]+(\d{2,3})',                      "target"),
            (r'need[s]?\s+(\d{1,3})\s+(?:more\s+)?runs?',  "runs_needed"),
            (r'partnership[:\s]+(\d{1,3})',                  "partnership"),
            (r'(\d{1,3})\s+balls?\s+(?:remaining|left)',    "balls_left"),
        ]:
            mm = re.search(pat, txt, re.IGNORECASE)
            if mm:
                try: data[key] = int(mm.group(1))
                except: pass

        tm = re.search(
            r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|'
            r'Hyderabad|Titans|Giants|Bengaluru|Bangalore))'
            r'\s+vs?\s+'
            r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|'
            r'Hyderabad|Titans|Giants|Bengaluru|Bangalore))',
            txt, re.IGNORECASE)
        if tm:
            data["team1"] = tm.group(1).strip()
            data["team2"] = tm.group(2).strip()

        if data.get("runs"):
            return data
    return None


# ══════════════════════════════════════════════════════════
#  TODAY'S MATCH
# ══════════════════════════════════════════════════════════
def get_today_match() -> str | None:
    for q in ["IPL 2026 today match playing teams live",
              "IPL 2026 live match today"]:
        res = search(q, mode="news", days="d")
        for r in res:
            t = r.get("title", "")
            m = re.search(
                r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|'
                r'Hyderabad|Titans|Giants|Bengaluru|Bangalore))'
                r'\s+vs?\s+'
                r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|'
                r'Hyderabad|Titans|Giants|Bengaluru|Bangalore))',
                t, re.IGNORECASE)
            if m:
                return f"{m.group(1).strip()} vs {m.group(2).strip()}"
            m2 = re.search(r'\b([A-Z]{2,3})\s+vs\s+([A-Z]{2,3})\b', t)
            if m2:
                return f"{m2.group(1)} vs {m2.group(2)}"
    return None


# ══════════════════════════════════════════════════════════
#  SCHEDULE
# ══════════════════════════════════════════════════════════
def get_schedule(day: str = "today") -> str:
    day_queries = {
        "today":     ["IPL 2026 today match fixture teams playing",
                      "IPL 2026 today game who is playing",
                      "IPL 2026 today match date venue"],
        "tomorrow":  ["IPL 2026 tomorrow next match vs fixture",
                      "IPL 2026 next match upcoming date teams",
                      "IPL 2026 schedule upcoming next game"],
        "yesterday": ["IPL 2026 yesterday match result winner",
                      "IPL 2026 last match result score who won",
                      "IPL 2026 Match 11 12 13 result"],
    }
    for q in day_queries.get(day, day_queries["today"]):
        res = search(q, mode="news", days="w")
        for r in res:
            title = r.get("title", "")
            body  = r.get("body", "")
            title_l = title.lower()

            if day == "tomorrow":
                if any(w in title_l for w in LIVE_WORDS + HIGHLIGHT_WORDS + ["live"]):
                    continue
            if day == "yesterday":
                has_result = any(w in title_l for w in RESULT_WORDS)
                is_live    = any(w in title_l for w in LIVE_WORDS + ["toss", "playing 11", "live"])
                if is_live or not has_result:
                    continue

            for line in re.split(r'[.\n|]', body):
                line = line.strip()
                if " vs " not in line.lower(): continue
                if not (10 < len(line) < 200): continue
                if is_junk(line): continue
                line_l = line.lower()
                if day == "tomorrow" and any(w in line_l for w in LIVE_WORDS + ["live", "toss"]): continue
                if day == "yesterday" and not any(w in line_l for w in RESULT_WORDS): continue
                return clean(line)

            if " vs " in title_l:
                if day == "tomorrow" and any(w in title_l for w in LIVE_WORDS + HIGHLIGHT_WORDS + ["live"]): continue
                part = title.split("|")[0].split(",")[0]
                c = clean(part)
                if len(c) > 8 and not is_junk(c):
                    return c
    return f"Sir, {day} ka schedule abhi available nahi."


# ══════════════════════════════════════════════════════════
#  POINTS TABLE
# ══════════════════════════════════════════════════════════
TEAM_WORDS   = ["Indians", "Kings", "Royals", "Capitals", "Hyderabad",
                "Titans", "Giants", "Bengaluru", "Riders", "Super Kings"]
REJECT_WORDS = ["defending", "champion", "all-time", "history", "debut",
                "enter ipl", "2025", "2024", "2023", "last season"]

def get_points_table() -> str:
    queries = [
        "IPL 2026 points table standings team wins losses",
        "IPL 2026 which team leads table top standings",
        "IPL 2026 playoff race standings teams",
    ]
    found = []
    for q in queries:
        res = search(q, mode="text", n=8)
        for r in res:
            body = r.get("body", "")
            for line in re.split(r'[\n.]', body):
                line = line.strip()
                if is_junk(line) or not (8 < len(line) < 150): continue
                line_l = line.lower()
                if any(rw in line_l for rw in REJECT_WORDS): continue
                if not any(t in line for t in TEAM_WORDS): continue
                has_pts = bool(re.search(r'\b\d{1,2}\s*(?:pts?|points?|wins?)', line, re.IGNORECASE))
                if has_pts:
                    cl = clean(line)
                    if cl and cl not in found:
                        found.append(cl)
            if len(found) >= 5: break
        if len(found) >= 3: break

    if found:
        return "Sir, IPL 2026 standings: " + ". ".join(found[:5])

    # Fallback
    res = search("IPL 2026 table topper leading team playoff", mode="news", days="w", n=6)
    sents = best_sentences(res, ["lead", "top", "first", "table", "points", "ahead"])
    return ("Sir, " + sents[0]) if sents else "Sir, points table updating. Try again shortly."


# ══════════════════════════════════════════════════════════
#  ORANGE / PURPLE CAP
# ══════════════════════════════════════════════════════════
HISTORY_REJECT = ["all-time", "all time", "history", "2008", "2009", "2010",
                  "2011", "2012", "2013", "2014", "2015", "2016", "2017",
                  "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025",
                  "winner list", "past seasons"]
# ══════════════════════════════════════════════════════════════════════
#  TEAM → HOME VENUE MAPPING
# ══════════════════════════════════════════════════════════════════════
TEAM_VENUE = {
    "Mumbai Indians":                "Wankhede Stadium, Mumbai",
    "Chennai Super Kings":           "MA Chidambaram Stadium, Chennai",
    "Royal Challengers Bengaluru":   "M Chinnaswamy Stadium, Bengaluru",
    "Kolkata Knight Riders":         "Eden Gardens, Kolkata",
    "Delhi Capitals":                "Arun Jaitley Stadium, Delhi",
    "Punjab Kings":                  "New Punjab Cricket Association Stadium, Mohali",
    "Rajasthan Royals":              "Sawai Mansingh Stadium, Jaipur",
    "Sunrisers Hyderabad":           "Rajiv Gandhi International Stadium, Hyderabad",
    "Lucknow Super Giants":          "Ekana Cricket Stadium, Lucknow",
    "Gujarat Titans":                "Narendra Modi Stadium, Ahmedabad",
}
TEAM_CITY = {
    "mumbai":"Mumbai","mi":"Mumbai","chennai":"Chennai","csk":"Chennai",
    "rcb":"Bengaluru","bangalore":"Bengaluru","bengaluru":"Bengaluru",
    "kkr":"Kolkata","kolkata":"Kolkata","delhi":"Delhi","dc":"Delhi",
    "punjab":"Mohali","pbks":"Mohali","rajasthan":"Jaipur","rr":"Jaipur",
    "hyderabad":"Hyderabad","srh":"Hyderabad","sunrisers":"Hyderabad",
    "lucknow":"Lucknow","lsg":"Lucknow","gujarat":"Ahmedabad","gt":"Ahmedabad",
}



def get_orange_cap() -> str:
    queries = [
        "IPL 2026 orange cap leader most runs 2026 season",
        "IPL 2026 Sameer Rizvi orange cap runs leader",
        "IPL 2026 who leads orange cap runs list",
    ]
    for q in queries:
        res = search(q, mode="text", n=8)
        # Scan ALL sentences, track previous sentence for context
        for r in res:
            body   = r.get("body", "")
            sents  = re.split(r'[.\n]', body)
            for i, line in enumerate(sents):
                line = line.strip()
                if is_junk(line) or not (10 < len(line) < 250): continue
                if any(rj in line.lower() for rj in HISTORY_REJECT): continue

                # Pattern 1: "NAME leads/tops with NNN runs"
                m = re.search(
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:leads?|tops?|is leading).*?(\d{2,4})\s+runs?',
                    line, re.IGNORECASE)
                if m:
                    name = clean(m.group(1)).strip()
                    if 3 < len(name) < 35 and not is_junk(name):
                        return f"Sir, orange cap: {name} leads with {m.group(2)} runs."

                # Pattern 2: "NNN runs" in line + name nearby
                if re.search(r'\d{3,4}\s+runs?', line, re.IGNORECASE):
                    name_m = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', line)
                    runs_m = re.search(r'(\d{3,4})\s+runs?', line, re.IGNORECASE)
                    if name_m and runs_m:
                        name = clean(name_m.group(1))
                        if not is_junk(name):
                            return f"Sir, orange cap: {name} with {runs_m.group(1)} runs."

                # Pattern 3: "orange cap" keyword with runs
                if "orange cap" in line.lower() or "most runs" in line.lower():
                    runs_m = re.search(r'(\d{2,4})\s+runs?', line, re.IGNORECASE)
                    if runs_m:
                        # Try to find name in this or adjacent sentences
                        for ctx in [line] + ([sents[i-1].strip()] if i > 0 else []):
                            nm = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', ctx)
                            if nm and not is_junk(nm.group(1)):
                                return f"Sir, orange cap leader: {clean(nm.group(1))} with {runs_m.group(1)} runs."
                        return f"Sir, {clean(line)[:180]}"

    return "Sir, IPL 2026 orange cap data not available right now."

def get_purple_cap() -> str:
    queries = [
        "IPL 2026 purple cap leader most wickets 2026 season",
        "IPL 2026 Ravi Bishnoi purple cap wickets leader",
        "IPL 2026 who leads purple cap wicket taker list",
    ]
    for q in queries:
        res = search(q, mode="text", n=8)
        for r in res:
            body  = r.get("body", "")
            sents = re.split(r'[.\n]', body)
            for i, line in enumerate(sents):
                line = line.strip()
                if is_junk(line) or not (10 < len(line) < 250): continue
                if any(rj in line.lower() for rj in HISTORY_REJECT): continue
                m = re.search(
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+.*?(\d{1,2})\s+wickets?',
                    line, re.IGNORECASE)
                if m:
                    name = clean(m.group(1)).strip()
                    if 3 < len(name) < 35 and not is_junk(name):
                        return f"Sir, purple cap: {name} leads with {m.group(2)} wickets."
                if any(w in line.lower() for w in ["purple cap","most wickets","top wicket"]):
                    wm = re.search(r'(\d{1,2})\s+wickets?', line, re.IGNORECASE)
                    if wm:
                        for ctx in [line] + ([sents[i-1].strip()] if i > 0 else []):
                            nm = re.search(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', ctx)
                            if nm and not is_junk(nm.group(1)):
                                return f"Sir, purple cap leader: {clean(nm.group(1))} with {wm.group(1)} wickets."
                        return f"Sir, {clean(line)[:180]}"
    return "Sir, IPL 2026 purple cap data not available right now."


# ══════════════════════════════════════════════════════════
#  PLAYER DATA
# ══════════════════════════════════════════════════════════
def get_player_raw_data(player: str) -> dict:
    """Fetch player batting + bowling raw data for ML."""
    # Try news first (cleaner text), then text search
    res1 = search(f"{player} IPL 2026 scored runs innings today match", mode="news", days="w", n=8)
    res2 = search(f"{player} IPL 2026 batting stats form runs", mode="text", n=6)
    res  = res1 + res2
    txt  = all_text(res)
    scores   = extract_scores_from_text(txt)[:10]
    wickets, economies = extract_wickets_from_text(txt)

    # Career stats
    cm  = re.search(r'(\d[\d,]+)\s+runs?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
    srm = re.search(r'strike.rate\s+(?:of\s+)?(\d{2,3}\.?\d?)', txt, re.IGNORECASE)
    eco = re.search(r'economy[\s:]+(\d{1,2}\.?\d?)', txt, re.IGNORECASE)

    return {
        "scores":        scores,
        "wickets":       wickets[:10],
        "economies":     economies[:10],
        "career_runs":   cm.group(1).replace(",","") if cm else None,
        "career_matches":cm.group(2) if cm else None,
        "strike_rate":   srm.group(1) if srm else None,
        "economy":       eco.group(1) if eco else None,
        "raw_text":      txt[:2000],
    }


# ══════════════════════════════════════════════════════════
#  MISC
# ══════════════════════════════════════════════════════════
def get_toss() -> str | None:
    res = search("IPL 2026 today toss result won elected bat bowl", mode="news", days="d")
    for r in res:
        for line in re.split(r'[.\n]', r.get("body", "")):
            if any(w in line.lower() for w in ["toss", "elected", "chose to", "won the toss"]):
                cl = clean(line.strip())
                if len(cl) > 15 and not is_junk(cl):
                    return cl[:200]
    return None

def get_playing11() -> str | None:
    res = search("IPL 2026 today playing 11 squad XI announced", mode="news", days="d")
    for r in res:
        for line in re.split(r'[.\n]', r.get("body", "")):
            if any(w in line.lower() for w in ["playing xi", "playing 11", "squad"]):
                cl = clean(line.strip())
                if len(cl) > 20 and not is_junk(cl):
                    return cl[:200]
    return None

def get_injury_news(team: str = None) -> str:
    q   = f"{team} IPL 2026 injury ruled out fitness" if team else "IPL 2026 player injury ruled out update"
    res = search(q, mode="news", days="w", n=8)
    injuries = []
    for r in res:
        title = r.get("title", "")
        if any(w in title.lower() for w in ["injur", "ruled out", "doubtful", "fitness", "unavailable"]):
            ct = clean(title.split("|")[0])
            if len(ct) > 10 and not is_junk(ct) and ct not in injuries:
                injuries.append(ct)
        sents = best_sentences([r], ["injur", "ruled out", "doubtful", "unavailable"])
        for s in sents:
            if s not in injuries: injuries.append(s)
        if len(injuries) >= 3: break
    return ("Sir, injury updates: " + ". ".join(list(dict.fromkeys(injuries))[:3])
            if injuries else "Sir, no major injury concerns.")

def get_ipl_news() -> str:
    res = search("IPL 2026 latest news today highlights cricket", mode="news", days="d", n=8)
    items = []
    for r in res:
        ct = clean(r.get("title", "").split("|")[0])
        if len(ct) > 15 and not is_junk(ct) and ct not in items:
            items.append(ct)
        if len(items) >= 4: break
    return ("Sir, IPL 2026 news: " + ". ".join(items)
            if items else "Sir, no fresh news right now.")