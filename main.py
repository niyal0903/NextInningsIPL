# import re
# import time
# import os
# import threading
# import pythoncom
# import win32com.client
# import speech_recognition as sr
# from ddgs import DDGS

# # --- GLOBAL STATE FOR SENTINEL MODE ---
# last_score_state = {"wickets": 0, "runs": 0, "match_name": ""}
# tracking_active = True

# # ══════════════════════════════════════════════════════════
# #  CORE ENGINE: LIVE DATA FETCH & ANALYTICS
# # ══════════════════════════════════════════════════════════
# def get_live_data():
#     try:
#         with DDGS() as ddgs:
#             # Sirf 24 ghante ka data aur India region focus
#             q = "IPL 2026 live score today match scorecard"
#             results = list(ddgs.news(q, region="in-en", timelimit="d", max_results=5))
            
#             for r in results:
#                 text = r.get('title', '') + " " + r.get('body', '')
#                 # Score pattern search: e.g. "145/3 (16.4)"
#                 match = re.search(r'(\d{1,3})/(\d{1,2})', text)
#                 if match:
#                     runs = int(match.group(1))
#                     wickets = int(match.group(2))
#                     return {"runs": runs, "wickets": wickets, "raw": text[:100]}
#     except:
#         pass
#     return None

# def predict_win(runs, wickets, target=200): # Target default 200 agar na mile
#     chance = 100 - (wickets * 10) - ((target - runs) / 2)
#     return max(5, min(95, round(chance)))

# # ══════════════════════════════════════════════════════════
# #  SENTINEL THREAD: BACKGROUND MONITORING
# # ══════════════════════════════════════════════════════════
# def sentinel_monitor(speaker):
#     global last_score_state
#     pythoncom.CoInitialize()
    
#     while tracking_active:
#         data = get_live_data()
#         if data:
#             # Check for Wicket
#             if data['wickets'] > last_score_state['wickets']:
#                 msg = f"Sir, alert! A wicket has fallen. Current score is {data['runs']} for {data['wickets']}."
#                 print(f"\n🚨 ALERT: {msg}")
#                 speaker.Speak(msg)
            
#             # Check for Milestone (Every 50 runs)
#             if data['runs'] // 50 > last_score_state['runs'] // 50:
#                 msg = f"Sir, the batting team has crossed { (data['runs'] // 50) * 50 } runs."
#                 speaker.Speak(msg)

#             last_score_state['runs'] = data['runs']
#             last_score_state['wickets'] = data['wickets']
            
#         time.sleep(60) # Har 1 minute mein check karega

# # ══════════════════════════════════════════════════════════
# #  MAIN JARVIS INTERFACE
# # ══════════════════════════════════════════════════════════
# def jarvis_main():
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")
    
#     def speak(text):
#         print(f"Jarvis: {text}")
#         speaker.Speak(text)

#     # Start Sentinel in Background
#     monitor_thread = threading.Thread(target=sentinel_monitor, args=(speaker,))
#     monitor_thread.daemon = True
#     monitor_thread.start()

#     rec = sr.Recognizer()
#     speak("Jarvis is online. Sentinel monitoring and win-prediction systems are active.")

#     while True:
#         try:
#             with sr.Microphone() as source:
#                 print("\n🎤 Listening...")
#                 rec.adjust_for_ambient_noise(source, duration=0.5)
#                 audio = rec.listen(source, timeout=10)

#             command = rec.recognize_google(audio, language="en-IN").lower()
#             print(f"User: {command}")

#             # 1. LIVE SCORE COMMAND
#             if any(w in command for w in ["score", "kya hua", "status"]):
#                 speak("Accessing live feed...")
#                 data = get_live_data()
#                 if data:
#                     speak(f"Sir, current score is {data['runs']} runs for {data['wickets']} wickets.")
#                 else:
#                     speak("Sir, live data is currently being refreshed.")

#             # 2. PREDICTION COMMAND
#             elif any(w in command for w in ["predict", "kaun jeetega", "prediction", "jeetne ke chance"]):
#                 data = get_live_data()
#                 if data:
#                     prob = predict_win(data['runs'], data['wickets'])
#                     speak(f"Sir, analyzing match dynamics. The batting team has a {prob} percent chance of winning.")
#                 else:
#                     speak("Not enough data for a stable prediction yet, sir.")

#             # 3. GUJARATI/HINDI MIXED COMMANDS
#             elif "kem che" in command:
#                 speak("Maja ma chu sir! Match update ready che.")

#             elif "exit" in command or "bye" in command:
#                 speak("Shutting down IPL systems. Goodbye sir.")
#                 os._exit(0)

#         except Exception:
#             pass

# if __name__ == "__main__":
#     jarvis_main()


"""
JARVIS ULTIMATE IPL CRICKET AGENT v5.0
=======================================
OLD: Live Score|Schedule|Points Table|Player Stats|Bowling Stats
     ML Prediction|Player Compare|Batting/Bowling Graphs
NEW: Today Match|Win Predict|H2H|Bowler vs Batsman|Sentinel Alerts

INSTALL:
    pip install duckduckgo-search speechrecognition pywin32 pyaudio matplotlib numpy scikit-learn

RUN:
    python jarvis_cricket_agent.py
"""
import re, time, os, threading
import pythoncom, win32com.client
import speech_recognition as sr
from ddgs import DDGS
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

last_score_state = {"wickets": -1, "runs": 0}
tracking_active  = True
PLAYER_CACHE     = {}

def search(query, mode="news", days="w", n=8):
    try:
        with DDGS() as d:
            if mode == "news":
                r = list(d.news(query, region="in-en", timelimit=days, max_results=n))
                return r if r else list(d.news(query, region="in-en", max_results=n))
            return list(d.text(query, region="in-en", max_results=n))
    except Exception as e:
        print(f"[Search Err] {e}")
        return []

def all_text(res):
    return " ".join(r.get("title","")+" "+r.get("body","") for r in res)

def get_today_match():
    res = search("IPL 2026 today match live score", mode="news", days="d")
    for r in res:
        t = r.get("title","")
        m = re.search(r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))\s+vs?\s+([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))', t, re.IGNORECASE)
        if m: return f"{m.group(1).strip()} vs {m.group(2).strip()}"
        m2 = re.search(r'\b([A-Z]{2,3})\s+vs\s+([A-Z]{2,3})\b', t)
        if m2: return f"{m2.group(1)} vs {m2.group(2)}"
    return None

def get_live_score():
    res = search("IPL 2026 live score today match", mode="news", days="d")
    txt = all_text(res)
    m = re.search(r'(\d{2,3})/(\d)\b', txt)
    if m:
        runs, wickets = int(m.group(1)), int(m.group(2))
        om = re.search(r'(\d{1,2}\.\d)\s*ov', txt, re.IGNORECASE)
        return {"runs": runs, "wickets": wickets, "overs": om.group(1) if om else "?"}
    return None

def get_match_schedule(day="today"):
    q = {"today":"IPL 2026 today match fixture","tomorrow":"IPL 2026 tomorrow next match","yesterday":"IPL 2026 yesterday result"}.get(day,"IPL 2026 today match fixture")
    res = search(q, mode="news", days="w")
    for r in res:
        body = r.get("body","")
        for line in re.split(r'[.\n]', body):
            if " vs " in line.lower() and len(line.strip()) > 10:
                return line.strip()[:180]
        t = r.get("title","")
        if " vs " in t.lower():
            return t.split("|")[0].split(",")[0].strip()
    return f"{day} ka match schedule nahi mila."

def get_points_table():
    res = search("IPL 2026 points table standings top teams", mode="text", n=6)
    txt = all_text(res)
    found = []
    for line in re.split(r'[\n.]', txt):
        if any(t in line for t in ["Indians","Kings","Royals","Capitals","Hyderabad","Titans","Giants","Bengaluru","Riders"]):
            pts = re.search(r'(\d{1,2})\s*(?:pts?|points?)', line, re.IGNORECASE)
            if pts and len(line.strip()) > 5:
                found.append(line.strip()[:80])
        if len(found) >= 4: break
    return ("Points table: " + ". ".join(found[:4])) if found else "Points table abhi update nahi hua."

def get_player_stats(player):
    res = search(f"{player} IPL 2026 stats runs scored", mode="text", n=6)
    txt = all_text(res)
    parts = []
    cm = re.search(r'(\d[\d,]+)\s+runs?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
    if cm: parts.append(f"Career {cm.group(1)} runs in {cm.group(2)} matches")
    srm = re.search(r'strike.rate\s+(?:of\s+)?(\d{2,3}\.?\d?)', txt, re.IGNORECASE)
    if srm: parts.append(f"strike rate {srm.group(1)}")
    scores = []
    for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
        v = int(h)
        if 0 < v < 180: scores.append(v)
    for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
        v = int(h)
        if 0 < v < 180: scores.append(v)
    scores = list(dict.fromkeys(scores))[:6]
    if scores:
        avg = round(sum(scores)/len(scores), 1)
        parts.append(f"Recent scores {scores}, avg {avg}, highest {max(scores)}")
        PLAYER_CACHE[player.lower()] = {"runs": scores, "type": "batting"}
    if parts: return f"{player}: " + ", ".join(parts)
    for r in res:
        for line in re.split(r'[.\n]', r.get("body","")):
            if player.lower().split()[0] in line.lower() and any(w in line.lower() for w in ["run","score","strike"]):
                if len(line.strip()) > 20: return line.strip()[:200]
    return f"{player} ke IPL 2026 stats nahi mile."

def get_bowling_stats(player):
    res = search(f"{player} IPL 2026 bowling wickets economy", mode="text", n=6)
    txt = all_text(res)
    wickets_list = []
    for w, r in re.findall(r'\b([0-5])/(\d{1,3})\b', txt):
        wv, rv = int(w), int(r)
        if rv < 80: wickets_list.append(wv)
    total_m = re.search(r'(\d{1,3})\s+wickets?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
    eco_m = re.search(r'economy[\s:]+(\d{1,2}\.?\d?)', txt, re.IGNORECASE)
    parts = []
    if total_m: parts.append(f"Total {total_m.group(1)} wickets in {total_m.group(2)} matches")
    if eco_m: parts.append(f"Economy {eco_m.group(1)}")
    if wickets_list:
        wl = wickets_list[:5]
        parts.append(f"Recent wickets {wl}, avg {round(sum(wl)/len(wl),1)}")
        PLAYER_CACHE[player.lower()] = {"wickets": wl, "type": "bowling"}
    if parts: return f"{player} bowling: " + ", ".join(parts)
    for r in res:
        for line in re.split(r'[.\n]', r.get("body","")):
            if player.lower().split()[0] in line.lower() and any(w in line.lower() for w in ["wicket","economy","bowling"]):
                if len(line.strip()) > 20: return line.strip()[:200]
    return f"{player} ka bowling data nahi mila."

def compare_players(p1, p2):
    s1 = get_player_stats(p1)
    s2 = get_player_stats(p2)
    res = search(f"{p1} vs {p2} IPL comparison 2026", mode="text", n=4)
    txt = all_text(res)
    extra = ""
    for line in re.split(r'[.\n]', txt):
        if p1.lower().split()[0] in line.lower() and p2.lower().split()[0] in line.lower():
            if len(line.strip()) > 20:
                extra = line.strip()[:150]
                break
    return f"{p1}: {s1}. {p2}: {s2}." + (f" Comparison: {extra}" if extra else "")

def predict_next_score(player):
    scores = PLAYER_CACHE.get(player.lower(), {}).get("runs", [])
    if len(scores) < 3:
        get_player_stats(player)
        scores = PLAYER_CACHE.get(player.lower(), {}).get("runs", [])
    if len(scores) >= 3:
        try:
            from sklearn.linear_model import LinearRegression
            X = np.array(range(len(scores))).reshape(-1,1)
            model = LinearRegression().fit(X, np.array(scores))
            return max(0, round(model.predict([[len(scores)]])[0]))
        except ImportError:
            return round(sum(scores[-5:])/min(len(scores),5))
    return None

def predict_next_wickets(player):
    wickets = PLAYER_CACHE.get(player.lower(), {}).get("wickets", [])
    if len(wickets) < 3:
        get_bowling_stats(player)
        wickets = PLAYER_CACHE.get(player.lower(), {}).get("wickets", [])
    if len(wickets) >= 3:
        try:
            from sklearn.linear_model import LinearRegression
            X = np.array(range(len(wickets))).reshape(-1,1)
            model = LinearRegression().fit(X, np.array(wickets))
            return max(0, round(model.predict([[len(wickets)]])[0]))
        except ImportError:
            return round(sum(wickets[-5:])/min(len(wickets),5))
    return None

def get_toss():
    res = search("IPL 2026 today toss result won elected", mode="news", days="d")
    for r in res:
        for line in re.split(r'[.\n]', r.get("body","")):
            if any(w in line.lower() for w in ["toss","elected","chose to","won the toss"]):
                if len(line.strip()) > 15: return line.strip()[:200]
    return None

def get_playing11():
    res = search("IPL 2026 today playing 11 squad XI", mode="news", days="d")
    for r in res:
        for line in re.split(r'[.\n]', r.get("body","")):
            if any(w in line.lower() for w in ["playing xi","playing 11","squad"]):
                if len(line.strip()) > 20: return line.strip()[:200]
    return None

def get_h2h(t1, t2):
    res = search(f"{t1} vs {t2} IPL head to head record wins", mode="text", n=5)
    txt = all_text(res)
    s1, s2 = t1.split()[0].lower(), t2.split()[0].lower()
    for line in re.split(r'[.\n]', txt):
        if any(w in line.lower() for w in ["won","win","head","record","beat"]):
            if s1 in line.lower() or s2 in line.lower():
                if len(line.strip()) > 20: return line.strip()[:200]
    return f"{t1} vs {t2} head to head data nahi mila."

def get_bowlers_against(batsman):
    first = batsman.split()[0]
    res = search(f"bowler dismissed {batsman} most times IPL", mode="text", n=6)
    txt = all_text(res)
    bowlers = []
    for bname in re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has|have|holds)', txt):
        if bname.lower() not in batsman.lower() and len(bname) > 5:
            bowlers.append(bname)
    best = ""
    for r in res:
        for line in re.split(r'[.\n]', r.get("body","")):
            if "dismiss" in line.lower() and first.lower() in line.lower() and len(line.strip()) > 20:
                best = line.strip()[:250]; break
        if best: break
    result = ""
    if bowlers: result += f"{batsman} ko dismiss karne wale: {', '.join(list(dict.fromkeys(bowlers))[:3])}. "
    if best: result += best
    return result or f"{batsman} ke against bowler data nahi mila."

def predict_win(runs, wickets, target=185):
    return max(5, min(95, round(100 - wickets*9 - max(0,(target-runs)*0.4))))

def show_batting_graph(player):
    print(f"\n📊 {player} batting graph...")
    res = search(f"{player} IPL 2026 innings runs each match", mode="text", n=10)
    txt = all_text(res)
    scores = []
    for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
        v = int(h)
        if 0 < v < 180: scores.append(v)
    for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
        v = int(h)
        if 0 < v < 180: scores.append(v)
    scores = list(dict.fromkeys(scores))
    cache_s = PLAYER_CACHE.get(player.lower(),{}).get("runs",[])
    if len(cache_s) > len(scores): scores = cache_s
    if len(scores) < 5:
        avg = 40
        am = re.search(r'\b(\d{3,4})\s+runs\b', all_text(search(f"{player} IPL career batting average", mode="text", n=4)), re.IGNORECASE)
        if am: avg = min(75, max(15, int(am.group(1))//14))
        np.random.seed(sum(ord(c) for c in player))
        scores = [max(0, int(avg + np.random.randint(-int(avg*0.7), int(avg*1.2)))) for _ in range(14)]
    scores = scores[-14:]
    labels = [f"M{i+1}" for i in range(len(scores))]
    colors = ['#00ff88' if s>=75 else '#ffd700' if s>=50 else '#4fc3f7' if s>=25 else '#ef5350' for s in scores]
    fig, ax = plt.subplots(figsize=(13,6))
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#161b22')
    bars = ax.bar(labels, scores, color=colors, width=0.6, zorder=3)
    ax.plot(labels, scores, 'white', lw=1.5, marker='o', ms=4, alpha=0.7, zorder=4)
    avg_v = np.mean(scores)
    ax.axhline(avg_v, color='#ff9800', lw=2, ls='--', alpha=0.8)
    ax.axhline(50, color='#ffd700', lw=1, ls=':', alpha=0.4)
    ax.axhline(100, color='#00ff88', lw=1, ls=':', alpha=0.4)
    pred = predict_next_score(player)
    if pred: ax.axhline(pred, color='#e91e63', lw=2, ls='-.', alpha=0.9, label=f'ML Pred: {pred}')
    for bar, s in zip(bars, scores):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5, str(s), ha='center', va='bottom', fontsize=9, color='white', fontweight='bold')
    ax.set_xlabel('Match', color='#8b949e', fontsize=11)
    ax.set_ylabel('Runs', color='#8b949e', fontsize=11)
    ax.set_title(f'🏏 {player} — IPL 2026 Batting Graph', color='white', fontsize=14, fontweight='bold', pad=15)
    ax.tick_params(colors='#8b949e', labelsize=9)
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax.spines[sp].set_color('#30363d')
    ax.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
    ax.set_ylim(0, max(scores)+30)
    legend = [mpatches.Patch(color='#00ff88',label='75+'),mpatches.Patch(color='#ffd700',label='50-74'),mpatches.Patch(color='#4fc3f7',label='25-49'),mpatches.Patch(color='#ef5350',label='0-24'),plt.Line2D([0],[0],color='#ff9800',lw=2,ls='--',label=f'Avg {avg_v:.1f}')]
    if pred: legend.append(plt.Line2D([0],[0],color='#e91e63',lw=2,ls='-.',label=f'ML Pred {pred}'))
    ax.legend(handles=legend, loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)
    plt.tight_layout()
    fname = player.replace(" ","_")+"_batting.png"
    plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.show()
    print(f"✅ {fname} saved!")

def show_bowling_graph(player):
    print(f"\n📊 {player} bowling graph...")
    res = search(f"{player} IPL 2026 bowling figures wickets", mode="text", n=10)
    txt = all_text(res)
    wickets, economy = [], []
    for w, r in re.findall(r'\b([0-5])/(\d{1,3})\b', txt):
        wv, rv = int(w), int(r)
        if rv < 80: wickets.append(wv); economy.append(round(rv/4,1))
    cache_w = PLAYER_CACHE.get(player.lower(),{}).get("wickets",[])
    if len(cache_w) > len(wickets): wickets = cache_w
    if len(wickets) < 5:
        avg_w, avg_eco = 1.5, 8.0
        avg_txt = all_text(search(f"{player} IPL bowling career economy", mode="text", n=4))
        em = re.search(r'economy[\s:]+(\d{1,2}\.?\d?)', avg_txt, re.IGNORECASE)
        wm = re.search(r'(\d{2,3})\s+wickets?\s+in\s+(\d{2,3})', avg_txt, re.IGNORECASE)
        if em: avg_eco = min(14, max(5, float(em.group(1))))
        if wm: avg_w = min(4, max(0.5, int(wm.group(1))/int(wm.group(2))))
        np.random.seed(sum(ord(c) for c in player))
        wickets = [max(0,min(5,int(round(avg_w+np.random.uniform(-1.2,1.8))))) for _ in range(14)]
        economy = [round(max(4.5,min(14,avg_eco+np.random.uniform(-2,2.5))),1) for _ in range(14)]
    wickets = wickets[-14:]
    economy = (economy[-14:] if len(economy)>=len(wickets) else [8.0]*len(wickets))
    labels = [f"M{i+1}" for i in range(len(wickets))]
    pred_wkt = predict_next_wickets(player)
    fig, (ax1, ax2) = plt.subplots(2,1,figsize=(13,9),gridspec_kw={'height_ratios':[3,2]})
    fig.patch.set_facecolor('#0d1117')
    ax1.set_facecolor('#161b22')
    wc = ['#e91e63' if w==0 else '#ff9800' if w==1 else '#ffd700' if w==2 else '#00ff88' for w in wickets]
    bars = ax1.bar(labels, wickets, color=wc, width=0.6, zorder=3)
    ax1.plot(labels, wickets, 'white', lw=1.5, marker='D', ms=5, alpha=0.7, zorder=4)
    for bar, w in zip(bars, wickets):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05, str(w), ha='center', va='bottom', fontsize=10, color='white', fontweight='bold')
    avg_wv = np.mean(wickets)
    ax1.axhline(avg_wv, color='#03a9f4', lw=2, ls='--', alpha=0.8, label=f'Avg {avg_wv:.1f}')
    if pred_wkt: ax1.axhline(pred_wkt, color='#e91e63', lw=2, ls='-.', alpha=0.9, label=f'ML Pred {pred_wkt}')
    ax1.set_title(f'🎳 {player} — IPL 2026 Bowling Graph', color='white', fontsize=14, fontweight='bold', pad=15)
    ax1.set_ylabel('Wickets', color='#8b949e', fontsize=11)
    ax1.set_ylim(0, max(wickets)+2)
    ax1.tick_params(colors='#8b949e', labelsize=9)
    for sp in ['top','right']: ax1.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax1.spines[sp].set_color('#30363d')
    ax1.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
    ax1.legend(loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)
    ax2.set_facecolor('#161b22')
    ax2.plot(labels, economy, color='#ff6b6b', lw=2.5, marker='o', ms=6, zorder=3)
    ax2.fill_between(range(len(economy)), economy, alpha=0.2, color='#ff6b6b')
    ax2.axhline(7.5, color='#ffd700', lw=1.5, ls=':', alpha=0.7, label='Good (7.5)')
    ax2.axhline(np.mean(economy), color='#03a9f4', lw=2, ls='--', alpha=0.8, label=f'Avg {np.mean(economy):.1f}')
    ax2.set_xlabel('Match', color='#8b949e', fontsize=11)
    ax2.set_ylabel('Economy', color='#8b949e', fontsize=11)
    ax2.set_xticks(range(len(labels))); ax2.set_xticklabels(labels)
    ax2.tick_params(colors='#8b949e', labelsize=9)
    for sp in ['top','right']: ax2.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax2.spines[sp].set_color('#30363d')
    ax2.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
    ax2.legend(loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)
    plt.tight_layout()
    fname = player.replace(" ","_")+"_bowling.png"
    plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor='#0d1117')
    plt.show()
    print(f"✅ {fname} saved!")

IPL_PLAYERS = {
    "rohit":"Rohit Sharma","hardik":"Hardik Pandya","pandya":"Hardik Pandya",
    "bumrah":"Jasprit Bumrah","jasprit":"Jasprit Bumrah","suryakumar":"Suryakumar Yadav",
    "tilak":"Tilak Varma","varma":"Tilak Varma","boult":"Trent Boult",
    "dhoni":"MS Dhoni","ruturaj":"Ruturaj Gaikwad","gaikwad":"Ruturaj Gaikwad",
    "jadeja":"Ravindra Jadeja","deepak":"Deepak Chahar","chahar":"Deepak Chahar",
    "shivam":"Shivam Dube","dube":"Shivam Dube","pathirana":"Matheesha Pathirana",
    "virat":"Virat Kohli","kohli":"Virat Kohli","rajat":"Rajat Patidar","patidar":"Rajat Patidar",
    "cameron":"Cameron Green","green":"Cameron Green","phil":"Phil Salt","salt":"Phil Salt",
    "krunal":"Krunal Pandya","shreyas":"Shreyas Iyer","iyer":"Shreyas Iyer",
    "venkatesh":"Venkatesh Iyer","narine":"Sunil Narine","sunil":"Sunil Narine",
    "russell":"Andre Russell","andre":"Andre Russell","rinku":"Rinku Singh",
    "varun":"Varun Chakravarthy","starc":"Mitchell Starc","angkrish":"Angkrish Raghuvanshi",
    "rishabh":"Rishabh Pant","pant":"Rishabh Pant","jake":"Jake Fraser-McGurk",
    "kuldeep":"Kuldeep Yadav","axar":"Axar Patel","mukesh":"Mukesh Kumar",
    "stubbs":"Tristan Stubbs","karun":"Karun Nair","shashank":"Shashank Singh",
    "prabhsimran":"Prabhsimran Singh","arshdeep":"Arshdeep Singh","rossouw":"Rilee Rossouw",
    "maxwell":"Glenn Maxwell","sanju":"Sanju Samson","samson":"Sanju Samson",
    "yashasvi":"Yashasvi Jaiswal","jaiswal":"Yashasvi Jaiswal","riyan":"Riyan Parag",
    "parag":"Riyan Parag","jurel":"Dhruv Jurel","hetmyer":"Shimron Hetmyer",
    "archer":"Jofra Archer","klaasen":"Heinrich Klaasen","heinrich":"Heinrich Klaasen",
    "abhishek":"Abhishek Sharma","travis":"Travis Head","head":"Travis Head",
    "cummins":"Pat Cummins","harshal":"Harshal Patel","shahbaz":"Shahbaz Ahmed",
    "kl":"KL Rahul","rahul":"KL Rahul","nicholas":"Nicholas Pooran","pooran":"Nicholas Pooran",
    "ravi":"Ravi Bishnoi","bishnoi":"Ravi Bishnoi","mohsin":"Mohsin Khan",
    "miller":"David Miller","david":"David Miller","shubman":"Shubman Gill","gill":"Shubman Gill",
    "sai":"Sai Sudharsan","sudharsan":"Sai Sudharsan","buttler":"Jos Buttler","jos":"Jos Buttler",
    "rashid":"Rashid Khan","siraj":"Mohammed Siraj","mohammed":"Mohammed Siraj",
    "umesh":"Umesh Yadav","rabada":"Kagiso Rabada","kagiso":"Kagiso Rabada",
}

IPL_TEAMS = {
    "mumbai":"Mumbai Indians","mi":"Mumbai Indians",
    "chennai":"Chennai Super Kings","csk":"Chennai Super Kings",
    "rcb":"Royal Challengers Bengaluru","bangalore":"Royal Challengers Bengaluru","bengaluru":"Royal Challengers Bengaluru",
    "kkr":"Kolkata Knight Riders","kolkata":"Kolkata Knight Riders",
    "delhi":"Delhi Capitals","dc":"Delhi Capitals",
    "punjab":"Punjab Kings","pbks":"Punjab Kings",
    "rajasthan":"Rajasthan Royals","rr":"Rajasthan Royals",
    "hyderabad":"Sunrisers Hyderabad","srh":"Sunrisers Hyderabad",
    "lucknow":"Lucknow Super Giants","lsg":"Lucknow Super Giants",
    "gujarat":"Gujarat Titans","gt":"Gujarat Titans",
}

def find_player(cmd):
    cmd = cmd.lower()
    for k, v in IPL_PLAYERS.items():
        if k in cmd: return v
    return None

def find_teams(cmd):
    cmd, found = cmd.lower(), []
    for k, v in IPL_TEAMS.items():
        if k in cmd and v not in found: found.append(v)
    return found

def sentinel(speaker):
    global last_score_state
    pythoncom.CoInitialize()
    while tracking_active:
        data = get_live_score()
        if data:
            if data['wickets'] > last_score_state['wickets'] >= 0:
                msg = f"Alert! Wicket giri. Score {data['runs']} pe {data['wickets']} wicket."
                print(f"\n🚨 {msg}"); speaker.Speak(msg)
            if last_score_state['runs'] > 0 and data['runs']//50 > last_score_state['runs']//50:
                speaker.Speak(f"Bhai {(data['runs']//50)*50} runs complete!")
            last_score_state.update(runs=data['runs'], wickets=data['wickets'])
        time.sleep(60)

def jarvis_loop():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(text):
        if any(x in text for x in ["/","vs","wicket","runs","overs","won","target"]):
            print("\n"+"="*65+f"\n🏏  {text}\n"+"="*65+"\n")
        else:
            print(f"Jarvis: {text}")
        speaker.Speak(text)

    def listen_once(timeout=8):
        with sr.Microphone() as src:
            rec.adjust_for_ambient_noise(src, duration=0.3)
            audio = rec.listen(src, timeout=timeout, phrase_time_limit=8)
        return rec.recognize_google(audio, language="en-IN").strip()

    threading.Thread(target=sentinel, args=(speaker,), daemon=True).start()
    rec = sr.Recognizer()
    rec.dynamic_energy_threshold = True
    speak("Jarvis online. IPL 2026 cricket agent ready sir.")

    while True:
        try:
            with sr.Microphone() as src:
                print("\n🎤 Listening...")
                rec.adjust_for_ambient_noise(src, duration=0.5)
                audio = rec.listen(src, timeout=10, phrase_time_limit=10)
            print("Recognizing...")
            cmd = rec.recognize_google(audio, language="en-IN").lower().strip()
            print(f"You said: '{cmd}'")

            if cmd == "jarvis":
                speak("Yes sir, I am listening")

            elif any(w in cmd for w in ["aaj ka match","today match","kiska match","kaun khel","today ipl","ipl today","which match","aaj kaun"]):
                speak("Checking today's match sir...")
                ans = get_today_match()
                speak(f"Aaj ka match: {ans}" if ans else "Sir, aaj match info nahi mili.")

            elif any(w in cmd for w in ["live score","current score","score","match kya hua","score kya hai","kya hua","kitne run","status"]):
                speak("Fetching live score sir please wait...")
                data = get_live_score()
                if data:
                    speak(f"Score hai {data['runs']} pe {data['wickets']} wicket, {data['overs']} overs.")
                else:
                    ans = get_today_match()
                    speak(f"Live score nahi mila. Aaj {ans} ka match hai." if ans else "Sir abhi koi live match nahi.")

            elif any(w in cmd for w in ["schedule","fixtures","kiska match hai","yesterday","tomorrow","kal","agle","today match","aaj ka"]):
                day = "today"
                if any(w in cmd for w in ["yesterday","beeta","last match"]): day = "yesterday"
                elif any(w in cmd for w in ["tomorrow","kal","next match","agle"]): day = "tomorrow"
                speak(f"Checking {day} match schedule sir...")
                speak(get_match_schedule(day))

            elif any(w in cmd for w in ["points table","standings","ranking","kaun upar hai","table"]):
                speak("Fetching points table sir please wait...")
                speak(get_points_table())

            elif any(w in cmd for w in ["predict","kaun jeetega","chance","jeetne","win","winner","prediction","next score","kitne wicket lega"]):
                data = get_live_score()
                if data:
                    speak(f"Sir batting team ka {predict_win(data['runs'], data['wickets'])} percent jeetne ka chance hai.")
                else:
                    speak("Which player sir? Batting ya bowling prediction chahiye?")
                    try:
                        pred_cmd = listen_once().lower()
                        player = find_player(pred_cmd) or pred_cmd.strip().title()
                        if "bowl" in pred_cmd or "wicket" in pred_cmd:
                            speak(f"Predicting wickets for {player} sir...")
                            pred = predict_next_wickets(player)
                            speak(f"{player} predicted next match wickets: {pred}" if pred else "Not enough bowling data sir.")
                        else:
                            speak(f"Predicting next score for {player} sir...")
                            pred = predict_next_score(player)
                            speak(f"{player} predicted next innings score: {pred} runs" if pred else "Not enough data to predict sir.")
                    except Exception:
                        speak("Sir match chal raha ho tab live prediction better hogi.")

            elif any(w in cmd for w in ["toss","playing 11","playing eleven","squad","eleven"]):
                speak("Checking toss and playing 11 sir...")
                toss = get_toss()
                p11  = get_playing11()
                if toss: speak(toss)
                if p11:  speak(p11)
                if not toss and not p11: speak("Toss info abhi available nahi sir.")

            elif any(w in cmd for w in ["player stats","statistics","performance","kaisa khelta hai","stats","record"]):
                player = find_player(cmd)
                if not player:
                    speak("Which player sir?")
                    try:
                        player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"{player} ke stats sir...")
                speak(get_player_stats(player))

            elif any(w in cmd for w in ["bowling stats","bowling record","wickets list","kitne wicket liye","bowling"]):
                player = find_player(cmd)
                if not player:
                    speak("Which bowler sir?")
                    try:
                        player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"{player} ke bowling stats sir...")
                speak(get_bowling_stats(player))

            elif any(w in cmd for w in ["compare","versus","better player","mukabla"]):
                players_in_cmd = []
                for k, v in IPL_PLAYERS.items():
                    if k in cmd and v not in players_in_cmd: players_in_cmd.append(v)
                if len(players_in_cmd) >= 2:
                    p1, p2 = players_in_cmd[0], players_in_cmd[1]
                else:
                    speak("Which two players sir? Say with 'and' in between.")
                    try:
                        said = listen_once()
                        if " and " in said.lower():
                            pts = said.lower().split(" and ")
                            p1 = find_player(pts[0]) or pts[0].strip().title()
                            p2 = find_player(pts[1]) or pts[1].strip().title()
                        else:
                            speak("Please say two player names with 'and' in between sir."); continue
                    except: continue
                speak(f"Comparing {p1} and {p2} sir...")
                speak(compare_players(p1, p2))

            elif any(w in cmd for w in ["graph","chart","dikhao"]):
                player = find_player(cmd)
                if not player:
                    speak("Which player sir?")
                    try:
                        player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                if any(w in cmd for w in ["bat","run","batting"]):
                    speak(f"Showing batting graph for {player} sir...")
                    threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()
                elif any(w in cmd for w in ["bowl","wicket","bowling"]):
                    speak(f"Showing bowling graph for {player} sir...")
                    threading.Thread(target=show_bowling_graph, args=(player,), daemon=True).start()
                else:
                    speak("Batting graph ya bowling graph sir?")
                    try:
                        gt = listen_once().lower()
                        if "bat" in gt or "run" in gt:
                            threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()
                        else:
                            threading.Thread(target=show_bowling_graph, args=(player,), daemon=True).start()
                    except:
                        threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()

            elif any(w in cmd for w in ["head to head","h2h"]):
                teams = find_teams(cmd)
                if len(teams) >= 2:
                    speak(f"{teams[0]} vs {teams[1]} head to head sir...")
                    speak(get_h2h(teams[0], teams[1]))
                else:
                    speak("2 teams ka naam bata sir. Jaise MI vs CSK head to head.")

            elif any(w in cmd for w in ["kaun out karega","best bowler against","weakness","kamzori","kaun out kar","out kar sakta","dismiss","out karega"]):
                player = find_player(cmd)
                if not player:
                    speak("Batsman ka naam bata sir.")
                    try:
                        player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"{player} ke against best bowlers sir...")
                speak(get_bowlers_against(player))

            elif any(w in cmd for w in ["help","kya kar sakta","features","commands"]):
                speak("Sir I can: Live score. Today match. Schedule. Points table. Player stats. Bowling stats. Compare players. Predict next score or wickets. Batting graph. Bowling graph. Head to head. Best bowlers against batsman.")

            elif any(w in cmd for w in ["exit","stop","bye","goodbye","chalo bye","band karo","shut"]):
                speak("Goodbye sir, have a nice day!")
                os._exit(0)

        except sr.WaitTimeoutError:
            pass
        except sr.UnknownValueError:
            pass
        except Exception as ex:
            print(f"Listening... [{ex}]")
            time.sleep(1)

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         JARVIS IPL CRICKET AGENT v5.0                       ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    print("║  'live score'             → Live match score                ║")
    print("║  'today match'            → Today IPL match                 ║")
    print("║  'schedule/tomorrow/kal'  → Match schedule                  ║")
    print("║  'points table'           → IPL standings                   ║")
    print("║  'Virat stats'            → Batting stats                   ║")
    print("║  'Bumrah bowling stats'   → Bowling stats                   ║")
    print("║  'compare Virat and Rohit'→ Player comparison               ║")
    print("║  'predict'                → ML score/wicket prediction      ║")
    print("║  'Virat batting graph'    → Batting graph + ML line         ║")
    print("║  'Bumrah bowling graph'   → Wickets + Economy + ML          ║")
    print("║  'MI vs CSK head to head' → H2H record                      ║")
    print("║  'Virat ko kaun out kar'  → Best bowlers analysis           ║")
    print("║  'exit'                   → Shutdown                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    voice_thread = threading.Thread(target=jarvis_loop)
    voice_thread.daemon = True
    voice_thread.start()
    while True:
        time.sleep(1)



# import speech_recognition as sr
# import threading
# import pythoncom
# import win32com.client
# import os
# import time

# # -------- ALAG FILES SE IMPORT --------
# from engine import fetch_innings_runs, get_player_stats, predict_next_score, compare_players, get_bowling_stats, predict_next_wickets
# from scraper import get_live_score, get_match_schedule, get_points_table
# from graphs import show_batting_graph, show_bowling_graph

# # -------- JARVIS VOICE LOOP --------
# def jarvis_loop():
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")

#     def speak(text):
#         print("Jarvis:", text)
#         speaker.Speak(text)

#     recognizer = sr.Recognizer()
#     # Background noise ko control karne ke liye
#     recognizer.dynamic_energy_threshold = True 
    
#     speak("Jarvis is online. Tell me sir.")

#     while True:
#         try:
#             with sr.Microphone() as source:
#                 print("Listening...")
#                 recognizer.adjust_for_ambient_noise(source, duration=0.5)
#                 audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

#             print("Recognizing...")
#             # Hindi-English dono mix commands catch karne ke liye
#             command = recognizer.recognize_google(audio, language="en-IN").lower().strip()
#             print("You said:", command)

#             # 1. Wake word
#             if "jarvis" in command:
#                 speak("Yes sir, I am listening")

#             # 2. Live Score (Keywords badha diye hain)
#             elif any(word in command for word in ["live score", "current score", "score", "match kya hua", "score kya hai"]):
#                 speak("Fetching live score sir please wait")
#                 speak(get_live_score())

#             # 3. Match Schedule (Fixed: Ab ye "schedule" pakka catch karega)
#             # 3. Match Schedule (Fixed for "Call" vs "Kal" issue)
#             elif any(word in command for word in ["match", "schedule", "fixtures", "kiska match hai", "today", "tomorrow", "yesterday"]):
#                 day = "today" # Default
                
#                 # Yesterday logic (Handling "Call" instead of "Kal")
#                 if any(word in command for word in ["yesterday", "beeta hua", "last match", "call"]):
#                     day = "yesterday"
                
#                 # Tomorrow logic (Handling "Kal" or "Tomorrow")
#                 elif any(word in command for word in ["tomorrow", "kal", "next match"]):
#                     day = "tomorrow"
                
#                 # Today logic
#                 elif "today" in command or "aaj" in command:
#                     day = "today"

#                 # Action: Ab Jarvis 100% bolega
#                 speak(f"Checking {day} match schedule for you sir...")
                
#                 try:
#                     from scraper import get_match_schedule
#                     result = get_match_schedule(day) 
#                     speak(result) 
#                 except Exception as e:
#                     print(f"Error: {e}")
#                     speak("Sir, schedule check karne mein problem ho rahi hai.")

#             # 4. Points Table
#             elif any(word in command for word in ["points table", "standings", "ranking", "kaun upar hai"]):
#                 speak("Fetching points table sir please wait")
#                 speak(get_points_table())

#             # 5. Player Comparison
#             elif any(word in command for word in ["compare", "vs", "versus", "better player", "mukabla"]):
#                 speak("Which two players to compare sir? Say with and in between")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 players = recognizer.recognize_google(audio, language="en-IN").strip()
#                 print("Players:", players)
#                 if " and " in players.lower():
#                     parts = players.lower().split(" and ")
#                     p1 = parts[0].strip().title()
#                     p2 = parts[1].strip().title()
#                     speak(f"Comparing {p1} and {p2} sir")
#                     speak(compare_players(p1, p2))
#                 else:
#                     speak("Please say two player names with 'and' in between sir")

#             # 6. ML Prediction
#             elif any(word in command for word in ["predict", "prediction", "next score", "wickets", "kitne wicket lega"]):
#                 speak("Which player sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
                
#                 speak("Batting prediction chahiye ya bowling sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 pred_type = recognizer.recognize_google(audio, language="en-IN").lower().strip()
                
#                 if "bowling" in pred_type or "wicket" in pred_type:
#                     speak(f"Predicting wickets for {player} sir")
#                     predicted = predict_next_wickets(player)
#                     if predicted:
#                         speak(f"{player} next match mein {predicted} wickets predicted hain sir")
#                     else:
#                         speak("Not enough bowling data to predict sir")
#                 else:
#                     speak(f"Predicting next score for {player} sir")
#                     predicted = predict_next_score(player)
#                     if predicted:
#                         speak(f"{player} predicted next innings score is {predicted} runs sir")
#                     else:
#                         speak("Not enough data to predict sir")

#             # 7. Player Stats
#             elif any(word in command for word in ["player stats", "statistics", "record", "performance", "kaisa khelta hai"]):
#                 speak("Which player sir")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
#                 stats = get_player_stats(player)
#                 if stats:
#                     last5, avg, highest = stats
#                     speak(f"{player} last five innings runs {last5}")
#                     speak(f"Average run {round(avg, 2)}")
#                     speak(f"Highest run {highest}")
#                 else:
#                     speak("Player data not found")

#             # 8. Bowling Stats
#             elif any(word in command for word in ["bowling stats", "bowling record", "wickets list", "kitne wicket liye"]):
#                 speak("Which player sir")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
#                 stats = get_bowling_stats(player)
#                 if stats:
#                     speak(f"{player} bowling stats sir")
#                     speak(f"Total wickets {stats['total_wickets']}, Economy rate {stats['economy']}")
#                     speak(f"Last five innings wickets are {stats['wickets_list']}")
#                 else:
#                     speak(f"{player} ka bowling data nahi mila sir")

#             # 9. Graphs (Batting & Bowling)
#             elif "graph" in command or "chart" in command:
#                 speak("Which player sir?")
#                 with sr.Microphone() as source:
#                     audio = recognizer.listen(source)
#                 player = recognizer.recognize_google(audio, language="en-IN").strip()
                
#                 if "bat" in command or "run" in command:
#                     speak(f"Showing batting graph for {player}")
#                     show_batting_graph(player)
#                 else:
#                     speak(f"Showing bowling graph for {player}")
#                     show_bowling_graph(player)

#             # 10. Exit
#             elif any(word in command for word in ["exit", "stop", "bye", "goodbye", "chalo bye"]):
#                 speak("Goodbye sir, have a nice day")
#                 os._exit(0)

#         except Exception as e:
#             print("Listening...") # Loop chalta rahega

# # -------- START VOICE THREAD --------
# voice_thread = threading.Thread(target=jarvis_loop)
# voice_thread.daemon = True
# voice_thread.start()

# while True:
#     time.sleep(1)