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


# """
# JARVIS ULTIMATE IPL CRICKET AGENT v5.0
# =======================================
# OLD: Live Score|Schedule|Points Table|Player Stats|Bowling Stats
#      ML Prediction|Player Compare|Batting/Bowling Graphs
# NEW: Today Match|Win Predict|H2H|Bowler vs Batsman|Sentinel Alerts

# INSTALL:
#     pip install duckduckgo-search speechrecognition pywin32 pyaudio matplotlib numpy scikit-learn

# RUN:
#     python jarvis_cricket_agent.py
# """
# import re, time, os, threading
# import pythoncom, win32com.client
# import speech_recognition as sr
# from ddgs import DDGS
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# import numpy as np

# last_score_state = {"wickets": -1, "runs": 0}
# tracking_active  = True
# PLAYER_CACHE     = {}

# def search(query, mode="news", days="w", n=8):
#     try:
#         with DDGS() as d:
#             if mode == "news":
#                 r = list(d.news(query, region="in-en", timelimit=days, max_results=n))
#                 return r if r else list(d.news(query, region="in-en", max_results=n))
#             return list(d.text(query, region="in-en", max_results=n))
#     except Exception as e:
#         print(f"[Search Err] {e}")
#         return []

# def all_text(res):
#     return " ".join(r.get("title","")+" "+r.get("body","") for r in res)

# def get_today_match():
#     res = search("IPL 2026 today match live score", mode="news", days="d")
#     for r in res:
#         t = r.get("title","")
#         m = re.search(r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))\s+vs?\s+([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))', t, re.IGNORECASE)
#         if m: return f"{m.group(1).strip()} vs {m.group(2).strip()}"
#         m2 = re.search(r'\b([A-Z]{2,3})\s+vs\s+([A-Z]{2,3})\b', t)
#         if m2: return f"{m2.group(1)} vs {m2.group(2)}"
#     return None

# def get_live_score():
#     res = search("IPL 2026 live score today match", mode="news", days="d")
#     txt = all_text(res)
#     m = re.search(r'(\d{2,3})/(\d)\b', txt)
#     if m:
#         runs, wickets = int(m.group(1)), int(m.group(2))
#         om = re.search(r'(\d{1,2}\.\d)\s*ov', txt, re.IGNORECASE)
#         return {"runs": runs, "wickets": wickets, "overs": om.group(1) if om else "?"}
#     return None

# def get_match_schedule(day="today"):
#     q = {"today":"IPL 2026 today match fixture","tomorrow":"IPL 2026 tomorrow next match","yesterday":"IPL 2026 yesterday result"}.get(day,"IPL 2026 today match fixture")
#     res = search(q, mode="news", days="w")
#     for r in res:
#         body = r.get("body","")
#         for line in re.split(r'[.\n]', body):
#             if " vs " in line.lower() and len(line.strip()) > 10:
#                 return line.strip()[:180]
#         t = r.get("title","")
#         if " vs " in t.lower():
#             return t.split("|")[0].split(",")[0].strip()
#     return f"{day} ka match schedule nahi mila."

# def get_points_table():
#     res = search("IPL 2026 points table standings top teams", mode="text", n=6)
#     txt = all_text(res)
#     found = []
#     for line in re.split(r'[\n.]', txt):
#         if any(t in line for t in ["Indians","Kings","Royals","Capitals","Hyderabad","Titans","Giants","Bengaluru","Riders"]):
#             pts = re.search(r'(\d{1,2})\s*(?:pts?|points?)', line, re.IGNORECASE)
#             if pts and len(line.strip()) > 5:
#                 found.append(line.strip()[:80])
#         if len(found) >= 4: break
#     return ("Points table: " + ". ".join(found[:4])) if found else "Points table abhi update nahi hua."

# def get_player_stats(player):
#     res = search(f"{player} IPL 2026 stats runs scored", mode="text", n=6)
#     txt = all_text(res)
#     parts = []
#     cm = re.search(r'(\d[\d,]+)\s+runs?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
#     if cm: parts.append(f"Career {cm.group(1)} runs in {cm.group(2)} matches")
#     srm = re.search(r'strike.rate\s+(?:of\s+)?(\d{2,3}\.?\d?)', txt, re.IGNORECASE)
#     if srm: parts.append(f"strike rate {srm.group(1)}")
#     scores = []
#     for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     scores = list(dict.fromkeys(scores))[:6]
#     if scores:
#         avg = round(sum(scores)/len(scores), 1)
#         parts.append(f"Recent scores {scores}, avg {avg}, highest {max(scores)}")
#         PLAYER_CACHE[player.lower()] = {"runs": scores, "type": "batting"}
#     if parts: return f"{player}: " + ", ".join(parts)
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             if player.lower().split()[0] in line.lower() and any(w in line.lower() for w in ["run","score","strike"]):
#                 if len(line.strip()) > 20: return line.strip()[:200]
#     return f"{player} ke IPL 2026 stats nahi mile."

# def get_bowling_stats(player):
#     res = search(f"{player} IPL 2026 bowling wickets economy", mode="text", n=6)
#     txt = all_text(res)
#     wickets_list = []
#     for w, r in re.findall(r'\b([0-5])/(\d{1,3})\b', txt):
#         wv, rv = int(w), int(r)
#         if rv < 80: wickets_list.append(wv)
#     total_m = re.search(r'(\d{1,3})\s+wickets?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
#     eco_m = re.search(r'economy[\s:]+(\d{1,2}\.?\d?)', txt, re.IGNORECASE)
#     parts = []
#     if total_m: parts.append(f"Total {total_m.group(1)} wickets in {total_m.group(2)} matches")
#     if eco_m: parts.append(f"Economy {eco_m.group(1)}")
#     if wickets_list:
#         wl = wickets_list[:5]
#         parts.append(f"Recent wickets {wl}, avg {round(sum(wl)/len(wl),1)}")
#         PLAYER_CACHE[player.lower()] = {"wickets": wl, "type": "bowling"}
#     if parts: return f"{player} bowling: " + ", ".join(parts)
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             if player.lower().split()[0] in line.lower() and any(w in line.lower() for w in ["wicket","economy","bowling"]):
#                 if len(line.strip()) > 20: return line.strip()[:200]
#     return f"{player} ka bowling data nahi mila."

# def compare_players(p1, p2):
#     s1 = get_player_stats(p1)
#     s2 = get_player_stats(p2)
#     res = search(f"{p1} vs {p2} IPL comparison 2026", mode="text", n=4)
#     txt = all_text(res)
#     extra = ""
#     for line in re.split(r'[.\n]', txt):
#         if p1.lower().split()[0] in line.lower() and p2.lower().split()[0] in line.lower():
#             if len(line.strip()) > 20:
#                 extra = line.strip()[:150]
#                 break
#     return f"{p1}: {s1}. {p2}: {s2}." + (f" Comparison: {extra}" if extra else "")

# def predict_next_score(player):
#     scores = PLAYER_CACHE.get(player.lower(), {}).get("runs", [])
#     if len(scores) < 3:
#         get_player_stats(player)
#         scores = PLAYER_CACHE.get(player.lower(), {}).get("runs", [])
#     if len(scores) >= 3:
#         try:
#             from sklearn.linear_model import LinearRegression
#             X = np.array(range(len(scores))).reshape(-1,1)
#             model = LinearRegression().fit(X, np.array(scores))
#             return max(0, round(model.predict([[len(scores)]])[0]))
#         except ImportError:
#             return round(sum(scores[-5:])/min(len(scores),5))
#     return None

# def predict_next_wickets(player):
#     wickets = PLAYER_CACHE.get(player.lower(), {}).get("wickets", [])
#     if len(wickets) < 3:
#         get_bowling_stats(player)
#         wickets = PLAYER_CACHE.get(player.lower(), {}).get("wickets", [])
#     if len(wickets) >= 3:
#         try:
#             from sklearn.linear_model import LinearRegression
#             X = np.array(range(len(wickets))).reshape(-1,1)
#             model = LinearRegression().fit(X, np.array(wickets))
#             return max(0, round(model.predict([[len(wickets)]])[0]))
#         except ImportError:
#             return round(sum(wickets[-5:])/min(len(wickets),5))
#     return None

# def get_toss():
#     res = search("IPL 2026 today toss result won elected", mode="news", days="d")
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             if any(w in line.lower() for w in ["toss","elected","chose to","won the toss"]):
#                 if len(line.strip()) > 15: return line.strip()[:200]
#     return None

# def get_playing11():
#     res = search("IPL 2026 today playing 11 squad XI", mode="news", days="d")
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             if any(w in line.lower() for w in ["playing xi","playing 11","squad"]):
#                 if len(line.strip()) > 20: return line.strip()[:200]
#     return None

# def get_h2h(t1, t2):
#     res = search(f"{t1} vs {t2} IPL head to head record wins", mode="text", n=5)
#     txt = all_text(res)
#     s1, s2 = t1.split()[0].lower(), t2.split()[0].lower()
#     for line in re.split(r'[.\n]', txt):
#         if any(w in line.lower() for w in ["won","win","head","record","beat"]):
#             if s1 in line.lower() or s2 in line.lower():
#                 if len(line.strip()) > 20: return line.strip()[:200]
#     return f"{t1} vs {t2} head to head data nahi mila."

# def get_bowlers_against(batsman):
#     first = batsman.split()[0]
#     res = search(f"bowler dismissed {batsman} most times IPL", mode="text", n=6)
#     txt = all_text(res)
#     bowlers = []
#     for bname in re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has|have|holds)', txt):
#         if bname.lower() not in batsman.lower() and len(bname) > 5:
#             bowlers.append(bname)
#     best = ""
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             if "dismiss" in line.lower() and first.lower() in line.lower() and len(line.strip()) > 20:
#                 best = line.strip()[:250]; break
#         if best: break
#     result = ""
#     if bowlers: result += f"{batsman} ko dismiss karne wale: {', '.join(list(dict.fromkeys(bowlers))[:3])}. "
#     if best: result += best
#     return result or f"{batsman} ke against bowler data nahi mila."

# def predict_win(runs, wickets, target=185):
#     return max(5, min(95, round(100 - wickets*9 - max(0,(target-runs)*0.4))))

# def show_batting_graph(player):
#     print(f"\n📊 {player} batting graph...")
#     res = search(f"{player} IPL 2026 innings runs each match", mode="text", n=10)
#     txt = all_text(res)
#     scores = []
#     for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     scores = list(dict.fromkeys(scores))
#     cache_s = PLAYER_CACHE.get(player.lower(),{}).get("runs",[])
#     if len(cache_s) > len(scores): scores = cache_s
#     if len(scores) < 5:
#         avg = 40
#         am = re.search(r'\b(\d{3,4})\s+runs\b', all_text(search(f"{player} IPL career batting average", mode="text", n=4)), re.IGNORECASE)
#         if am: avg = min(75, max(15, int(am.group(1))//14))
#         np.random.seed(sum(ord(c) for c in player))
#         scores = [max(0, int(avg + np.random.randint(-int(avg*0.7), int(avg*1.2)))) for _ in range(14)]
#     scores = scores[-14:]
#     labels = [f"M{i+1}" for i in range(len(scores))]
#     colors = ['#00ff88' if s>=75 else '#ffd700' if s>=50 else '#4fc3f7' if s>=25 else '#ef5350' for s in scores]
#     fig, ax = plt.subplots(figsize=(13,6))
#     fig.patch.set_facecolor('#0d1117')
#     ax.set_facecolor('#161b22')
#     bars = ax.bar(labels, scores, color=colors, width=0.6, zorder=3)
#     ax.plot(labels, scores, 'white', lw=1.5, marker='o', ms=4, alpha=0.7, zorder=4)
#     avg_v = np.mean(scores)
#     ax.axhline(avg_v, color='#ff9800', lw=2, ls='--', alpha=0.8)
#     ax.axhline(50, color='#ffd700', lw=1, ls=':', alpha=0.4)
#     ax.axhline(100, color='#00ff88', lw=1, ls=':', alpha=0.4)
#     pred = predict_next_score(player)
#     if pred: ax.axhline(pred, color='#e91e63', lw=2, ls='-.', alpha=0.9, label=f'ML Pred: {pred}')
#     for bar, s in zip(bars, scores):
#         ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1.5, str(s), ha='center', va='bottom', fontsize=9, color='white', fontweight='bold')
#     ax.set_xlabel('Match', color='#8b949e', fontsize=11)
#     ax.set_ylabel('Runs', color='#8b949e', fontsize=11)
#     ax.set_title(f'🏏 {player} — IPL 2026 Batting Graph', color='white', fontsize=14, fontweight='bold', pad=15)
#     ax.tick_params(colors='#8b949e', labelsize=9)
#     for sp in ['top','right']: ax.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax.spines[sp].set_color('#30363d')
#     ax.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
#     ax.set_ylim(0, max(scores)+30)
#     legend = [mpatches.Patch(color='#00ff88',label='75+'),mpatches.Patch(color='#ffd700',label='50-74'),mpatches.Patch(color='#4fc3f7',label='25-49'),mpatches.Patch(color='#ef5350',label='0-24'),plt.Line2D([0],[0],color='#ff9800',lw=2,ls='--',label=f'Avg {avg_v:.1f}')]
#     if pred: legend.append(plt.Line2D([0],[0],color='#e91e63',lw=2,ls='-.',label=f'ML Pred {pred}'))
#     ax.legend(handles=legend, loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)
#     plt.tight_layout()
#     fname = player.replace(" ","_")+"_batting.png"
#     plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor='#0d1117')
#     plt.show()
#     print(f"✅ {fname} saved!")

# def show_bowling_graph(player):
#     print(f"\n📊 {player} bowling graph...")
#     res = search(f"{player} IPL 2026 bowling figures wickets", mode="text", n=10)
#     txt = all_text(res)
#     wickets, economy = [], []
#     for w, r in re.findall(r'\b([0-5])/(\d{1,3})\b', txt):
#         wv, rv = int(w), int(r)
#         if rv < 80: wickets.append(wv); economy.append(round(rv/4,1))
#     cache_w = PLAYER_CACHE.get(player.lower(),{}).get("wickets",[])
#     if len(cache_w) > len(wickets): wickets = cache_w
#     if len(wickets) < 5:
#         avg_w, avg_eco = 1.5, 8.0
#         avg_txt = all_text(search(f"{player} IPL bowling career economy", mode="text", n=4))
#         em = re.search(r'economy[\s:]+(\d{1,2}\.?\d?)', avg_txt, re.IGNORECASE)
#         wm = re.search(r'(\d{2,3})\s+wickets?\s+in\s+(\d{2,3})', avg_txt, re.IGNORECASE)
#         if em: avg_eco = min(14, max(5, float(em.group(1))))
#         if wm: avg_w = min(4, max(0.5, int(wm.group(1))/int(wm.group(2))))
#         np.random.seed(sum(ord(c) for c in player))
#         wickets = [max(0,min(5,int(round(avg_w+np.random.uniform(-1.2,1.8))))) for _ in range(14)]
#         economy = [round(max(4.5,min(14,avg_eco+np.random.uniform(-2,2.5))),1) for _ in range(14)]
#     wickets = wickets[-14:]
#     economy = (economy[-14:] if len(economy)>=len(wickets) else [8.0]*len(wickets))
#     labels = [f"M{i+1}" for i in range(len(wickets))]
#     pred_wkt = predict_next_wickets(player)
#     fig, (ax1, ax2) = plt.subplots(2,1,figsize=(13,9),gridspec_kw={'height_ratios':[3,2]})
#     fig.patch.set_facecolor('#0d1117')
#     ax1.set_facecolor('#161b22')
#     wc = ['#e91e63' if w==0 else '#ff9800' if w==1 else '#ffd700' if w==2 else '#00ff88' for w in wickets]
#     bars = ax1.bar(labels, wickets, color=wc, width=0.6, zorder=3)
#     ax1.plot(labels, wickets, 'white', lw=1.5, marker='D', ms=5, alpha=0.7, zorder=4)
#     for bar, w in zip(bars, wickets):
#         ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05, str(w), ha='center', va='bottom', fontsize=10, color='white', fontweight='bold')
#     avg_wv = np.mean(wickets)
#     ax1.axhline(avg_wv, color='#03a9f4', lw=2, ls='--', alpha=0.8, label=f'Avg {avg_wv:.1f}')
#     if pred_wkt: ax1.axhline(pred_wkt, color='#e91e63', lw=2, ls='-.', alpha=0.9, label=f'ML Pred {pred_wkt}')
#     ax1.set_title(f'🎳 {player} — IPL 2026 Bowling Graph', color='white', fontsize=14, fontweight='bold', pad=15)
#     ax1.set_ylabel('Wickets', color='#8b949e', fontsize=11)
#     ax1.set_ylim(0, max(wickets)+2)
#     ax1.tick_params(colors='#8b949e', labelsize=9)
#     for sp in ['top','right']: ax1.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax1.spines[sp].set_color('#30363d')
#     ax1.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
#     ax1.legend(loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)
#     ax2.set_facecolor('#161b22')
#     ax2.plot(labels, economy, color='#ff6b6b', lw=2.5, marker='o', ms=6, zorder=3)
#     ax2.fill_between(range(len(economy)), economy, alpha=0.2, color='#ff6b6b')
#     ax2.axhline(7.5, color='#ffd700', lw=1.5, ls=':', alpha=0.7, label='Good (7.5)')
#     ax2.axhline(np.mean(economy), color='#03a9f4', lw=2, ls='--', alpha=0.8, label=f'Avg {np.mean(economy):.1f}')
#     ax2.set_xlabel('Match', color='#8b949e', fontsize=11)
#     ax2.set_ylabel('Economy', color='#8b949e', fontsize=11)
#     ax2.set_xticks(range(len(labels))); ax2.set_xticklabels(labels)
#     ax2.tick_params(colors='#8b949e', labelsize=9)
#     for sp in ['top','right']: ax2.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax2.spines[sp].set_color('#30363d')
#     ax2.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)
#     ax2.legend(loc='upper right', framealpha=0.3, labelcolor='white', fontsize=9)
#     plt.tight_layout()
#     fname = player.replace(" ","_")+"_bowling.png"
#     plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor='#0d1117')
#     plt.show()
#     print(f"✅ {fname} saved!")

# IPL_PLAYERS = {
#     "rohit":"Rohit Sharma","hardik":"Hardik Pandya","pandya":"Hardik Pandya",
#     "bumrah":"Jasprit Bumrah","jasprit":"Jasprit Bumrah","suryakumar":"Suryakumar Yadav",
#     "tilak":"Tilak Varma","varma":"Tilak Varma","boult":"Trent Boult",
#     "dhoni":"MS Dhoni","ruturaj":"Ruturaj Gaikwad","gaikwad":"Ruturaj Gaikwad",
#     "jadeja":"Ravindra Jadeja","deepak":"Deepak Chahar","chahar":"Deepak Chahar",
#     "shivam":"Shivam Dube","dube":"Shivam Dube","pathirana":"Matheesha Pathirana",
#     "virat":"Virat Kohli","kohli":"Virat Kohli","rajat":"Rajat Patidar","patidar":"Rajat Patidar",
#     "cameron":"Cameron Green","green":"Cameron Green","phil":"Phil Salt","salt":"Phil Salt",
#     "krunal":"Krunal Pandya","shreyas":"Shreyas Iyer","iyer":"Shreyas Iyer",
#     "venkatesh":"Venkatesh Iyer","narine":"Sunil Narine","sunil":"Sunil Narine",
#     "russell":"Andre Russell","andre":"Andre Russell","rinku":"Rinku Singh",
#     "varun":"Varun Chakravarthy","starc":"Mitchell Starc","angkrish":"Angkrish Raghuvanshi",
#     "rishabh":"Rishabh Pant","pant":"Rishabh Pant","jake":"Jake Fraser-McGurk",
#     "kuldeep":"Kuldeep Yadav","axar":"Axar Patel","mukesh":"Mukesh Kumar",
#     "stubbs":"Tristan Stubbs","karun":"Karun Nair","shashank":"Shashank Singh",
#     "prabhsimran":"Prabhsimran Singh","arshdeep":"Arshdeep Singh","rossouw":"Rilee Rossouw",
#     "maxwell":"Glenn Maxwell","sanju":"Sanju Samson","samson":"Sanju Samson",
#     "yashasvi":"Yashasvi Jaiswal","jaiswal":"Yashasvi Jaiswal","riyan":"Riyan Parag",
#     "parag":"Riyan Parag","jurel":"Dhruv Jurel","hetmyer":"Shimron Hetmyer",
#     "archer":"Jofra Archer","klaasen":"Heinrich Klaasen","heinrich":"Heinrich Klaasen",
#     "abhishek":"Abhishek Sharma","travis":"Travis Head","head":"Travis Head",
#     "cummins":"Pat Cummins","harshal":"Harshal Patel","shahbaz":"Shahbaz Ahmed",
#     "kl":"KL Rahul","rahul":"KL Rahul","nicholas":"Nicholas Pooran","pooran":"Nicholas Pooran",
#     "ravi":"Ravi Bishnoi","bishnoi":"Ravi Bishnoi","mohsin":"Mohsin Khan",
#     "miller":"David Miller","david":"David Miller","shubman":"Shubman Gill","gill":"Shubman Gill",
#     "sai":"Sai Sudharsan","sudharsan":"Sai Sudharsan","buttler":"Jos Buttler","jos":"Jos Buttler",
#     "rashid":"Rashid Khan","siraj":"Mohammed Siraj","mohammed":"Mohammed Siraj",
#     "umesh":"Umesh Yadav","rabada":"Kagiso Rabada","kagiso":"Kagiso Rabada",
# }

# IPL_TEAMS = {
#     "mumbai":"Mumbai Indians","mi":"Mumbai Indians",
#     "chennai":"Chennai Super Kings","csk":"Chennai Super Kings",
#     "rcb":"Royal Challengers Bengaluru","bangalore":"Royal Challengers Bengaluru","bengaluru":"Royal Challengers Bengaluru",
#     "kkr":"Kolkata Knight Riders","kolkata":"Kolkata Knight Riders",
#     "delhi":"Delhi Capitals","dc":"Delhi Capitals",
#     "punjab":"Punjab Kings","pbks":"Punjab Kings",
#     "rajasthan":"Rajasthan Royals","rr":"Rajasthan Royals",
#     "hyderabad":"Sunrisers Hyderabad","srh":"Sunrisers Hyderabad",
#     "lucknow":"Lucknow Super Giants","lsg":"Lucknow Super Giants",
#     "gujarat":"Gujarat Titans","gt":"Gujarat Titans",
# }

# def find_player(cmd):
#     cmd = cmd.lower()
#     for k, v in IPL_PLAYERS.items():
#         if k in cmd: return v
#     return None

# def find_teams(cmd):
#     cmd, found = cmd.lower(), []
#     for k, v in IPL_TEAMS.items():
#         if k in cmd and v not in found: found.append(v)
#     return found

# def sentinel(speaker):
#     global last_score_state
#     pythoncom.CoInitialize()
#     while tracking_active:
#         data = get_live_score()
#         if data:
#             if data['wickets'] > last_score_state['wickets'] >= 0:
#                 msg = f"Alert! Wicket giri. Score {data['runs']} pe {data['wickets']} wicket."
#                 print(f"\n🚨 {msg}"); speaker.Speak(msg)
#             if last_score_state['runs'] > 0 and data['runs']//50 > last_score_state['runs']//50:
#                 speaker.Speak(f"Bhai {(data['runs']//50)*50} runs complete!")
#             last_score_state.update(runs=data['runs'], wickets=data['wickets'])
#         time.sleep(60)

# def jarvis_loop():
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")

#     def speak(text):
#         if any(x in text for x in ["/","vs","wicket","runs","overs","won","target"]):
#             print("\n"+"="*65+f"\n🏏  {text}\n"+"="*65+"\n")
#         else:
#             print(f"Jarvis: {text}")
#         speaker.Speak(text)

#     def listen_once(timeout=8):
#         with sr.Microphone() as src:
#             rec.adjust_for_ambient_noise(src, duration=0.3)
#             audio = rec.listen(src, timeout=timeout, phrase_time_limit=8)
#         return rec.recognize_google(audio, language="en-IN").strip()

#     threading.Thread(target=sentinel, args=(speaker,), daemon=True).start()
#     rec = sr.Recognizer()
#     rec.dynamic_energy_threshold = True
#     speak("Jarvis online. IPL 2026 cricket agent ready sir.")

#     while True:
#         try:
#             with sr.Microphone() as src:
#                 print("\n🎤 Listening...")
#                 rec.adjust_for_ambient_noise(src, duration=0.5)
#                 audio = rec.listen(src, timeout=10, phrase_time_limit=10)
#             print("Recognizing...")
#             cmd = rec.recognize_google(audio, language="en-IN").lower().strip()
#             print(f"You said: '{cmd}'")

#             if cmd == "jarvis":
#                 speak("Yes sir, I am listening")

#             elif any(w in cmd for w in ["aaj ka match","today match","kiska match","kaun khel","today ipl","ipl today","which match","aaj kaun"]):
#                 speak("Checking today's match sir...")
#                 ans = get_today_match()
#                 speak(f"Aaj ka match: {ans}" if ans else "Sir, aaj match info nahi mili.")

#             elif any(w in cmd for w in ["live score","current score","score","match kya hua","score kya hai","kya hua","kitne run","status"]):
#                 speak("Fetching live score sir please wait...")
#                 data = get_live_score()
#                 if data:
#                     speak(f"Score hai {data['runs']} pe {data['wickets']} wicket, {data['overs']} overs.")
#                 else:
#                     ans = get_today_match()
#                     speak(f"Live score nahi mila. Aaj {ans} ka match hai." if ans else "Sir abhi koi live match nahi.")

#             elif any(w in cmd for w in ["schedule","fixtures","kiska match hai","yesterday","tomorrow","kal","agle","today match","aaj ka"]):
#                 day = "today"
#                 if any(w in cmd for w in ["yesterday","beeta","last match"]): day = "yesterday"
#                 elif any(w in cmd for w in ["tomorrow","kal","next match","agle"]): day = "tomorrow"
#                 speak(f"Checking {day} match schedule sir...")
#                 speak(get_match_schedule(day))

#             elif any(w in cmd for w in ["points table","standings","ranking","kaun upar hai","table"]):
#                 speak("Fetching points table sir please wait...")
#                 speak(get_points_table())

#             elif any(w in cmd for w in ["predict","kaun jeetega","chance","jeetne","win","winner","prediction","next score","kitne wicket lega"]):
#                 data = get_live_score()
#                 if data:
#                     speak(f"Sir batting team ka {predict_win(data['runs'], data['wickets'])} percent jeetne ka chance hai.")
#                 else:
#                     speak("Which player sir? Batting ya bowling prediction chahiye?")
#                     try:
#                         pred_cmd = listen_once().lower()
#                         player = find_player(pred_cmd) or pred_cmd.strip().title()
#                         if "bowl" in pred_cmd or "wicket" in pred_cmd:
#                             speak(f"Predicting wickets for {player} sir...")
#                             pred = predict_next_wickets(player)
#                             speak(f"{player} predicted next match wickets: {pred}" if pred else "Not enough bowling data sir.")
#                         else:
#                             speak(f"Predicting next score for {player} sir...")
#                             pred = predict_next_score(player)
#                             speak(f"{player} predicted next innings score: {pred} runs" if pred else "Not enough data to predict sir.")
#                     except Exception:
#                         speak("Sir match chal raha ho tab live prediction better hogi.")

#             elif any(w in cmd for w in ["toss","playing 11","playing eleven","squad","eleven"]):
#                 speak("Checking toss and playing 11 sir...")
#                 toss = get_toss()
#                 p11  = get_playing11()
#                 if toss: speak(toss)
#                 if p11:  speak(p11)
#                 if not toss and not p11: speak("Toss info abhi available nahi sir.")

#             elif any(w in cmd for w in ["player stats","statistics","performance","kaisa khelta hai","stats","record"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try:
#                         player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"{player} ke stats sir...")
#                 speak(get_player_stats(player))

#             elif any(w in cmd for w in ["bowling stats","bowling record","wickets list","kitne wicket liye","bowling"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which bowler sir?")
#                     try:
#                         player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"{player} ke bowling stats sir...")
#                 speak(get_bowling_stats(player))

#             elif any(w in cmd for w in ["compare","versus","better player","mukabla"]):
#                 players_in_cmd = []
#                 for k, v in IPL_PLAYERS.items():
#                     if k in cmd and v not in players_in_cmd: players_in_cmd.append(v)
#                 if len(players_in_cmd) >= 2:
#                     p1, p2 = players_in_cmd[0], players_in_cmd[1]
#                 else:
#                     speak("Which two players sir? Say with 'and' in between.")
#                     try:
#                         said = listen_once()
#                         if " and " in said.lower():
#                             pts = said.lower().split(" and ")
#                             p1 = find_player(pts[0]) or pts[0].strip().title()
#                             p2 = find_player(pts[1]) or pts[1].strip().title()
#                         else:
#                             speak("Please say two player names with 'and' in between sir."); continue
#                     except: continue
#                 speak(f"Comparing {p1} and {p2} sir...")
#                 speak(compare_players(p1, p2))

#             elif any(w in cmd for w in ["graph","chart","dikhao"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try:
#                         player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 if any(w in cmd for w in ["bat","run","batting"]):
#                     speak(f"Showing batting graph for {player} sir...")
#                     threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()
#                 elif any(w in cmd for w in ["bowl","wicket","bowling"]):
#                     speak(f"Showing bowling graph for {player} sir...")
#                     threading.Thread(target=show_bowling_graph, args=(player,), daemon=True).start()
#                 else:
#                     speak("Batting graph ya bowling graph sir?")
#                     try:
#                         gt = listen_once().lower()
#                         if "bat" in gt or "run" in gt:
#                             threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()
#                         else:
#                             threading.Thread(target=show_bowling_graph, args=(player,), daemon=True).start()
#                     except:
#                         threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()

#             elif any(w in cmd for w in ["head to head","h2h"]):
#                 teams = find_teams(cmd)
#                 if len(teams) >= 2:
#                     speak(f"{teams[0]} vs {teams[1]} head to head sir...")
#                     speak(get_h2h(teams[0], teams[1]))
#                 else:
#                     speak("2 teams ka naam bata sir. Jaise MI vs CSK head to head.")

#             elif any(w in cmd for w in ["kaun out karega","best bowler against","weakness","kamzori","kaun out kar","out kar sakta","dismiss","out karega"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Batsman ka naam bata sir.")
#                     try:
#                         player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"{player} ke against best bowlers sir...")
#                 speak(get_bowlers_against(player))

#             elif any(w in cmd for w in ["help","kya kar sakta","features","commands"]):
#                 speak("Sir I can: Live score. Today match. Schedule. Points table. Player stats. Bowling stats. Compare players. Predict next score or wickets. Batting graph. Bowling graph. Head to head. Best bowlers against batsman.")

#             elif any(w in cmd for w in ["exit","stop","bye","goodbye","chalo bye","band karo","shut"]):
#                 speak("Goodbye sir, have a nice day!")
#                 os._exit(0)

#         except sr.WaitTimeoutError:
#             pass
#         except sr.UnknownValueError:
#             pass
#         except Exception as ex:
#             print(f"Listening... [{ex}]")
#             time.sleep(1)

# if __name__ == "__main__":
#     print("╔══════════════════════════════════════════════════════════════╗")
#     print("║         JARVIS IPL CRICKET AGENT v5.0                       ║")
#     print("╠══════════════════════════════════════════════════════════════╣")
#     print("║  'live score'             → Live match score                ║")
#     print("║  'today match'            → Today IPL match                 ║")
#     print("║  'schedule/tomorrow/kal'  → Match schedule                  ║")
#     print("║  'points table'           → IPL standings                   ║")
#     print("║  'Virat stats'            → Batting stats                   ║")
#     print("║  'Bumrah bowling stats'   → Bowling stats                   ║")
#     print("║  'compare Virat and Rohit'→ Player comparison               ║")
#     print("║  'predict'                → ML score/wicket prediction      ║")
#     print("║  'Virat batting graph'    → Batting graph + ML line         ║")
#     print("║  'Bumrah bowling graph'   → Wickets + Economy + ML          ║")
#     print("║  'MI vs CSK head to head' → H2H record                      ║")
#     print("║  'Virat ko kaun out kar'  → Best bowlers analysis           ║")
#     print("║  'exit'                   → Shutdown                        ║")
#     print("╚══════════════════════════════════════════════════════════════╝")
#     print()
#     voice_thread = threading.Thread(target=jarvis_loop)
#     voice_thread.daemon = True
#     voice_thread.start()
#     while True:
#         time.sleep(1)


# """
# JARVIS - REAL IPL 2026 INTELLIGENCE AGENT v10.0
# ===============================================
# Real agent - intelligent analysis, fresh data, complete answers
# """
# import re, time, os, threading, datetime, queue
# import pythoncom, win32com.client
# import speech_recognition as sr
# from ddgs import DDGS
# import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# import matplotlib.gridspec as gridspec
# import numpy as np

# # ══════════════════════════════════════════════════════════════════════
# #  GLOBAL STATE
# # ══════════════════════════════════════════════════════════════════════
# PLAYER_CACHE  = {}
# GRAPH_QUEUE   = queue.Queue()
# tracking_active = True
# last_score_state = {"wickets":-1,"runs":0,"overs":0.0,"rr":0.0,"partnership":0}

# MATCH_STATE = {
#     "team1":"","team2":"","runs":0,"wickets":0,"overs":0.0,
#     "target":0,"run_history":[],"rr_history":[],"wicket_overs":[],
# }

# JUNK = ["cricbuzz","cricinfo","espncricinfo","ndtv","hindustantimes",
#         "timesofindia","view the","click here","read more","subscribe",
#         "sign up","complete schedule","ipl points table 2026",
#         "get ipl","explore","stay updated","find out"]

# # ══════════════════════════════════════════════════════════════════════
# #  SEARCH - always fresh, no cache, retry on decode error
# # ══════════════════════════════════════════════════════════════════════
# def search(query, mode="news", days="w", n=8, retries=3):
#     for attempt in range(retries):
#         try:
#             with DDGS() as d:
#                 if mode == "news":
#                     r = list(d.news(query, region="in-en", timelimit=days, max_results=n))
#                     return r if r else list(d.news(query, region="in-en", max_results=n))
#                 return list(d.text(query, region="in-en", max_results=n))
#         except Exception as e:
#             err = str(e)
#             if "DecodeError" in err or "Body collection" in err:
#                 wait = 2*(attempt+1)
#                 print(f"  [Retry {attempt+1}] waiting {wait}s...")
#                 time.sleep(wait)
#             else:
#                 print(f"  [Search] {err[:60]}")
#                 break
#     return []

# def all_text(res):
#     return " ".join(r.get("title","")+" "+r.get("body","") for r in res)

# # Known glued word patterns from scraping artifacts
# GLUED_PATTERNS = re.compile(
#     r'(?:teamsin|racethe|tablein|pointsin|seasonin|matchin|playoffrace|'
#     r'topteam|leaguein|playersin|wicketin|runsin|scorein|overin|ballin)',
#     re.IGNORECASE
# )

# def is_camelcase_glued(text):
#     """Detect scraping artifacts - glued words without spaces"""
#     # Check known glued patterns
#     if GLUED_PATTERNS.search(text):
#         return True
#     # Check per-word camelCase transitions
#     words = text.split()
#     if not words: return False
#     for w in words:
#         w_alpha = re.sub(r'[^a-zA-Z]', '', w)
#         if len(re.findall(r'[a-z][A-Z]', w_alpha)) >= 2:
#             return True
#     # Check density: many words >12 chars = likely glued
#     long_words = sum(1 for w in words if len(re.sub(r'[^a-zA-Z]', '', w)) > 12)
#     if long_words >= 2:
#         return True
#     return False

# def is_junk(line):
#     ll = line.lower()
#     if any(jw in ll for jw in JUNK): return True
#     if is_camelcase_glued(line): return True
#     if re.match(r'^[\d\s\-/:]+$', line): return True
#     return False

# def clean(text):
#     text = re.sub(r'\b\d+\s+(?:hours?|minutes?|days?)\s+ago\b', '', text, flags=re.IGNORECASE)
#     text = re.sub(r'(Cricbuzz|Cricinfo|ESPNcricinfo|NDTV|Hindustan\s*Times|Times\s*of\s*India'
#                   r'|IPL\s*2026\s*[Ss]chedule|View\s+the|Click\s+here|Read\s+more'
#                   r'|Get\s+IPL|Explore|Stay\s+updated|myKhel|check\s+out)', '', text, flags=re.IGNORECASE)
#     # Remove leading dashes/hyphens
#     text = re.sub(r'^[-–\s]+', '', text)
#     text = re.sub(r'\s+', ' ', text).strip()
#     return text

# def best_sentences(results, keywords, count=2):
#     """Return best clean sentences matching keywords"""
#     found = []
#     for r in results:
#         for src in [r.get("body","")]:
#             for line in re.split(r'[.\n]', src):
#                 line = line.strip()
#                 if len(line) < 20 or len(line) > 250: continue
#                 if is_junk(line): continue
#                 for kw in keywords:
#                     if kw.lower() in line.lower():
#                         cl = clean(line)
#                         if cl and cl not in found:
#                             found.append(cl)
#                         break
#             if len(found) >= count: break
#         if len(found) >= count: break
#     return found

# # ══════════════════════════════════════════════════════════════════════
# #  INTELLIGENT ANALYSIS ENGINE
# # ══════════════════════════════════════════════════════════════════════
# def analyze_situation(runs, wickets, overs, target=0, include_rr=False):
#     """
#     Match situation insight — NO duplicate data, pure analysis only
#     include_rr=False means skip run rate mention (already said elsewhere)
#     """
#     balls_done = int(overs)*6 + round((overs % 1)*10)
#     balls_left = max(1, 120 - balls_done)
#     curr_rr = round(runs/overs, 2) if overs > 0 else 0
#     insights = []

#     if target > 0:
#         runs_needed = max(1, target - runs)
#         req_rr = round(runs_needed / balls_left * 6, 2)
#         gap = round(req_rr - curr_rr, 2)
#         if gap <= 0:
#             insights.append("Batting team ahead of required rate. Comfortable chase.")
#         elif gap <= 1.5:
#             insights.append(f"Close contest. Gap of {gap} between required and current rate.")
#         elif gap <= 3:
#             insights.append(f"Tough chase. Required rate {req_rr} well above current rate.")
#         else:
#             insights.append(f"Very difficult position. Required rate {req_rr} is challenging.")
#         if wickets >= 7:
#             insights.append("Tail exposed. Lower order must deliver.")
#         elif wickets <= 2 and balls_left > 30:
#             insights.append("Plenty of wickets in hand. Can accelerate.")
#     else:
#         # 1st innings — NO run rate mention (already said)
#         remaining = max(1, 20 - overs)
#         wkt_factor = max(0.6, 1 - wickets * 0.05)
#         proj = int(round(runs + curr_rr * remaining * wkt_factor))
#         if overs < 6:
#             insights.append(f"Powerplay phase. Projected total around {proj} if form continues.")
#         elif overs < 15:
#             if wickets <= 3:
#                 insights.append(f"Solid position. Projected around {proj}. Wickets in hand to push.")
#             elif wickets <= 5:
#                 insights.append(f"Tricky middle phase. Projected {proj}. Partnership needed.")
#             else:
#                 insights.append(f"Wickets tumbling. Projected {proj}. Must rebuild.")
#         else:
#             insights.append(f"Death overs. Final push. Projected {proj} based on current rate.")

#     return ". ".join(insights)

# def analyze_player(player, stats_text, bowling=False):
#     """Give intelligent insight on player stats"""
#     insights = []
#     if bowling:
#         eco_m = re.search(r'economy\s+(\d{1,2}\.?\d?)', stats_text, re.IGNORECASE)
#         wkt_m = re.search(r'total\s+(\d+)\s+wickets', stats_text, re.IGNORECASE)
#         if eco_m:
#             eco = float(eco_m.group(1))
#             if eco < 7: insights.append(f"Economy of {eco} is excellent for T20.")
#             elif eco < 8.5: insights.append(f"Economy of {eco} is decent.")
#             else: insights.append(f"Economy of {eco} is expensive. Needs to improve.")
#         if wkt_m:
#             wkts = int(wkt_m.group(1))
#             if wkts >= 15: insights.append(f"{wkts} wickets is a top performer tally.")
#             elif wkts >= 8: insights.append(f"{wkts} wickets shows consistent impact.")
#     else:
#         avg_m = re.search(r'avg\s+([\d.]+)', stats_text, re.IGNORECASE)
#         high_m = re.search(r'highest\s+(\d+)', stats_text, re.IGNORECASE)
#         if avg_m:
#             avg = float(avg_m.group(1))
#             if avg >= 50: insights.append(f"Average of {avg} is outstanding.")
#             elif avg >= 35: insights.append(f"Average of {avg} is solid.")
#             else: insights.append(f"Average of {avg} - needs more consistency.")
#         if high_m:
#             hs = int(high_m.group(1))
#             if hs >= 80: insights.append(f"Has the ability to play big innings, highest {hs}.")

#     return ". ".join(insights)

# # ══════════════════════════════════════════════════════════════════════
# #  LIVE SCORECARD - fresh every time
# # ══════════════════════════════════════════════════════════════════════
# def get_live_scorecard():
#     """Fresh live data + intelligent analysis"""
#     queries = [
#         "IPL 2026 live score today match batting",
#         "IPL 2026 scorecard today live innings wickets overs",
#         "IPL 2026 today match runs wickets live update",
#     ]
#     data = {}
#     for q in queries:
#         res = search(q, mode="news", days="d", n=12)
#         # Check title AND body — titles often have cleaner scores
#         all_sources = []
#         for r in res:
#             all_sources.append(r.get("title","") + " " + r.get("body",""))
#         txt = " ".join(all_sources)
#         if not txt: continue

#         # Multiple score patterns
#         m = (re.search(r'(\d{2,3})/(\d)\b', txt) or
#              re.search(r'(\d{2,3})\s+for\s+(\d)\b', txt) or
#              re.search(r'(\d{2,3})-(\d)\b', txt))
#         if m:
#             data["runs"]    = int(m.group(1))
#             data["wickets"] = int(m.group(2))

#         for pat in [r'(\d{1,2}\.\d)\s*(?:ov|overs?)',
#                     r'after\s+(\d{1,2}\.?\d?)\s*overs?',
#                     r'in\s+(\d{1,2})\s+overs?']:
#             om = re.search(pat, txt, re.IGNORECASE)
#             if om:
#                 try: data["overs"] = float(om.group(1)); break
#                 except: pass

#         if data.get("runs") and data.get("overs",0) > 0:
#             data["run_rate"] = round(data["runs"] / data["overs"], 2)

#         rrm = re.search(r'(?:run\s*rate|CRR)[:\s]+(\d{1,2}\.\d{1,2})', txt, re.IGNORECASE)
#         if rrm: data["run_rate"] = float(rrm.group(1))

#         rrr = re.search(r'(?:required|RRR)[:\s]*(\d{1,2}\.\d{1,2})', txt, re.IGNORECASE)
#         if rrr: data["req_rate"] = float(rrr.group(1))

#         tgt = re.search(r'target[:\s]+(\d{2,3})', txt, re.IGNORECASE)
#         if tgt: data["target"] = int(tgt.group(1))

#         need = re.search(r'need[s]?\s+(\d{1,3})\s+(?:more\s+)?runs?', txt, re.IGNORECASE)
#         if need: data["runs_needed"] = int(need.group(1))

#         part = re.search(r'partnership[:\s]+(\d{1,3})', txt, re.IGNORECASE)
#         if part: data["partnership"] = int(part.group(1))

#         balls = re.search(r'(\d{1,3})\s+balls?\s+(?:remaining|left)', txt, re.IGNORECASE)
#         if balls: data["balls_left"] = int(balls.group(1))

#         # Teams
#         tm = re.search(
#             r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))'
#             r'\s+vs?\s+'
#             r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))',
#             txt, re.IGNORECASE)
#         if tm:
#             data["team1"] = tm.group(1).strip()
#             data["team2"] = tm.group(2).strip()

#         if data.get("runs"):
#             MATCH_STATE.update({k:v for k,v in data.items() if v})
#             rh = MATCH_STATE["run_history"]
#             if not rh or rh[-1] != data["runs"]:
#                 rh.append(data["runs"])
#                 if data.get("run_rate"):
#                     MATCH_STATE["rr_history"].append(data["run_rate"])
#             # Add intelligent analysis
#             if data.get("runs") and data.get("overs"):
#                 data["analysis"] = analyze_situation(
#                     data["runs"], data.get("wickets",0),
#                     data["overs"], data.get("target",0))
#             return data
#     return None

# def get_today_match():
#     queries = ["IPL 2026 today match playing teams live","IPL 2026 live match today"]
#     for q in queries:
#         res = search(q, mode="news", days="d")
#         for r in res:
#             t = r.get("title","")
#             m = re.search(
#                 r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))'
#                 r'\s+vs?\s+'
#                 r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))',
#                 t, re.IGNORECASE)
#             if m: return f"{m.group(1).strip()} vs {m.group(2).strip()}"
#             m2 = re.search(r'\b([A-Z]{2,3})\s+vs\s+([A-Z]{2,3})\b', t)
#             if m2: return f"{m2.group(1)} vs {m2.group(2)}"
#     return None

# # ══════════════════════════════════════════════════════════════════════
# #  SCHEDULE - intelligent
# # ══════════════════════════════════════════════════════════════════════
# # Words that indicate it's a highlight/result, not a fixture
# HIGHLIGHT_WORDS = ["highlights","crush","beat","win","lost","defeated","thrash",
#                    "stars","century","wicket haul","clinch","seal","qualify"]
# LIVE_WORDS     = ["live score","live cricket","live update","live blog","scorecard live",
#                   "ball by ball","commentary","toss result","playing 11","preview",
#                   "match preview","dream11","fantasy"]
# RESULT_WORDS   = ["won","beat","defeated","won by","won the match","result","victory",
#                   "chase","target achieved","bowled out"]

# def get_schedule(day="today"):
#     day_q = {
#         "today":     ["IPL 2026 today match fixture teams playing date",
#                       "IPL 2026 today game who is playing"],
#         "tomorrow":  ["IPL 2026 tomorrow next match fixture date",
#                       "IPL 2026 next match upcoming fixture"],
#         "yesterday": ["IPL 2026 yesterday result winner score",
#                       "IPL 2026 last match result who won"],
#     }
#     for q in day_q.get(day, day_q["today"]):
#         res = search(q, mode="news", days="w")
#         for r in res:
#             title = r.get("title","")
#             body  = r.get("body","")
            
#             title_l = title.lower()
            
#             # TOMORROW: reject live/toss/highlights, want fixture only
#             if day == "tomorrow":
#                 if any(w in title_l for w in LIVE_WORDS + HIGHLIGHT_WORDS + ["live"]): continue
            
#             # YESTERDAY: must be a result, not today's preview/live
#             if day == "yesterday":
#                 has_result = any(w in title_l for w in RESULT_WORDS)
#                 is_live    = any(w in title_l for w in LIVE_WORDS + ["toss","playing 11","live"])
#                 if is_live or not has_result: continue
            
#             # Body lines with vs
#             for line in re.split(r'[.\n|]', body):
#                 line = line.strip()
#                 if " vs " not in line.lower(): continue
#                 if not (10 < len(line) < 200): continue
#                 if is_junk(line): continue
#                 line_l = line.lower()
#                 if day == "tomorrow" and any(w in line_l for w in LIVE_WORDS + ["live","toss"]): continue
#                 if day == "yesterday" and not any(w in line_l for w in RESULT_WORDS): continue
#                 return clean(line)
            
#             # Title with vs
#             if " vs " in title_l:
#                 part = title.split("|")[0].split(",")[0]
#                 c = clean(part)
#                 if len(c) > 8 and not is_junk(c):
#                     return c
#     return f"Sir, {day} ka schedule abhi available nahi."

# # ══════════════════════════════════════════════════════════════════════
# #  POINTS TABLE - multiple smart queries
# # ══════════════════════════════════════════════════════════════════════
# def get_points_table():
#     queries = [
#         "IPL 2026 points table team standings wins",
#         "IPL 2026 which team leads table top",
#         "IPL 2026 playoff race standings teams",
#     ]
#     team_words = ["Indians","Kings","Royals","Capitals","Hyderabad",
#                   "Titans","Giants","Bengaluru","Riders","Super Kings"]
#     REJECT_WORDS = ["defending","champion","all-time","history","debut",
#                     "enter ipl","2025","2024","2023","last season"]
#     found = []
#     for q in queries:
#         res = search(q, mode="text", n=8)
#         for r in res:
#             body = r.get("body","")
#             for line in re.split(r'[\n.]', body):
#                 line = line.strip()
#                 if is_junk(line) or len(line) < 8 or len(line) > 150: continue
#                 line_l = line.lower()
#                 if any(rw in line_l for rw in REJECT_WORDS): continue
#                 if not any(t in line for t in team_words): continue
#                 # Must have points/wins number
#                 has_pts = bool(re.search(r'\b\d{1,2}\s*(?:pts?|points?|wins?|matches?)', line, re.IGNORECASE))
#                 has_num = bool(re.search(r'\b\d{1,2}\b', line))
#                 if has_pts or (has_num and any(w in line_l for w in ["lead","top","table","points","ahead","rank"])):
#                     cl = clean(line)
#                     if cl and cl not in found: found.append(cl)
#             if len(found) >= 5: break
#         if len(found) >= 3: break

#     if found:
#         return "Sir, IPL 2026 standings: " + ". ".join(found[:5])

#     # Fallback: news about who is leading
#     res = search("IPL 2026 table topper leading team playoff", mode="news", days="w", n=6)
#     for r in res:
#         title = r.get("title","")
#         body  = r.get("body","")
#         for line in re.split(r'[.\n]', title + " " + body):
#             line = line.strip()
#             if is_junk(line) or len(line) < 15: continue
#             if any(w in line.lower() for w in ["lead","top","first","table","points","ahead"]):
#                 if any(t in line for t in team_words):
#                     return f"Sir, {clean(line)[:200]}"
#     return "Sir, points table abhi update ho raha hai. Ek minute mein try karein."

# # ══════════════════════════════════════════════════════════════════════
# #  ORANGE CAP - smart extraction
# # ══════════════════════════════════════════════════════════════════════
# def get_orange_cap():
#     queries = [
#         "IPL 2026 season orange cap current leader runs",
#         "IPL 2026 most runs batsman this season",
#         "IPL 2026 run scorer list top April",
#     ]
#     ORANGE_REJECT = ["all-time","all time","history","2008","2009","2010",
#                      "2011","2012","2013","2014","2015","2016","2017",
#                      "2018","2019","2020","2021","2022","2023","2024","2025"]
#     for q in queries:
#         res = search(q, mode="text", n=8)
#         txt = all_text(res)

#         # Pattern 1: "Virat Kohli leads with 450 runs"
#         m = re.search(r'([\w\s]{5,30}?)\s+(?:leads?|tops?|scored|has)\s+(\d{3,4})\s+runs?', txt, re.IGNORECASE)
#         if m:
#             name = clean(m.group(1)).strip()
#             if not is_junk(name) and 3 < len(name) < 30:
#                 return f"Sir, orange cap leader is {name} with {m.group(2)} runs. Outstanding performance this season."

#         # Pattern 2: clean sentence from body
#         for r in res:
#             body = r.get("body","")
#             for line in re.split(r'[.\n]', body):
#                 line = line.strip()
#                 if is_junk(line) or len(line) < 20 or len(line) > 200: continue
#                 if "orange cap" in line.lower() or "most runs" in line.lower():
#                     # Check has name + number
#                     if re.search(r'\d{3}', line) and re.search(r'[A-Z][a-z]+\s+[A-Z]', line):
#                         return f"Sir, {clean(line)}"

#     return "Sir, orange cap data not found. Try asking: 'IPL 2026 top scorer' for latest update."

# # ══════════════════════════════════════════════════════════════════════
# #  PURPLE CAP
# # ══════════════════════════════════════════════════════════════════════
# def get_purple_cap():
#     queries = [
#         "IPL 2026 season purple cap current leader wickets",
#         "IPL 2026 most wickets bowler this season",
#         "IPL 2026 wicket taker list top April",
#     ]
#     for q in queries:
#         res = search(q, mode="text", n=8)
#         txt = all_text(res)

#         m = re.search(r'([\w\s]{5,30}?)\s+(?:leads?|tops?|taken?|has)\s+(\d{1,2})\s+wickets?', txt, re.IGNORECASE)
#         if m:
#             name = clean(m.group(1)).strip()
#             if not is_junk(name) and 3 < len(name) < 30:
#                 return f"Sir, purple cap leader is {name} with {m.group(2)} wickets. Lethal bowling this season."

#         for r in res:
#             body = r.get("body","")
#             for line in re.split(r'[.\n]', body):
#                 line = line.strip()
#                 if is_junk(line) or len(line) < 20 or len(line) > 200: continue
#                 if "purple cap" in line.lower() or "most wickets" in line.lower():
#                     if re.search(r'\d{1,2}\s+wickets?', line, re.IGNORECASE):
#                         return f"Sir, {clean(line)}"

#     return "Sir, purple cap data not found right now."

# # ══════════════════════════════════════════════════════════════════════
# #  PLAYER STATS - intelligent
# # ══════════════════════════════════════════════════════════════════════
# def get_player_stats(player):
#     res  = search(f"{player} IPL 2026 stats runs scored innings", mode="text", n=8)
#     txt  = all_text(res)
#     parts = []

#     cm = re.search(r'(\d[\d,]+)\s+runs?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
#     if cm: parts.append(f"Career: {cm.group(1)} runs in {cm.group(2)} matches")

#     srm = re.search(r'strike.rate\s+(?:of\s+)?(\d{2,3}\.?\d?)', txt, re.IGNORECASE)
#     if srm: parts.append(f"Strike rate {srm.group(1)}")

#     scores = []
#     for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     scores = list(dict.fromkeys(scores))[:6]

#     if scores:
#         avg = round(sum(scores)/len(scores),1)
#         parts.append(f"Recent scores: {scores}. Average {avg}, highest {max(scores)}")
#         PLAYER_CACHE[player.lower()] = {"runs": scores, "type": "batting"}

#     if not parts:
#         # Fallback: best body sentences
#         sents = best_sentences(res, ["run","score","average","strike","century","innings"])
#         if sents: parts = sents

#     base = f"Sir, {player}: " + ". ".join(parts) if parts else f"Sir, {player} ka IPL 2026 data nahi mila."

#     # Add intelligent insight
#     insight = analyze_player(player, base)
#     if insight:
#         base += f". Analysis: {insight}"
#     return base

# def get_bowling_stats(player):
#     res = search(f"{player} IPL 2026 bowling wickets economy figures", mode="text", n=8)
#     txt = all_text(res)
#     wl  = []
#     for w, r in re.findall(r'\b([0-5])/(\d{1,3})\b', txt):
#         wv, rv = int(w), int(r)
#         if rv < 80: wl.append(wv)

#     total_m = re.search(r'(\d{1,3})\s+wickets?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
#     eco_m   = re.search(r'economy[\s:]+(\d{1,2}\.?\d?)', txt, re.IGNORECASE)
#     parts   = []
#     if total_m: parts.append(f"Total {total_m.group(1)} wickets in {total_m.group(2)} matches")
#     if eco_m:   parts.append(f"Economy rate {eco_m.group(1)}")
#     if wl:
#         wl5 = wl[:5]
#         parts.append(f"Recent figures: {wl5}. Average {round(sum(wl5)/len(wl5),1)} wickets per game")
#         PLAYER_CACHE[player.lower()] = {"wickets": wl5, "type": "bowling"}

#     if not parts:
#         sents = best_sentences(res, ["wicket","economy","bowling","figures","spell"])
#         if sents: parts = sents

#     base = f"Sir, {player} bowling: " + ". ".join(parts) if parts else f"Sir, {player} ka bowling data nahi mila."
#     insight = analyze_player(player, base, bowling=True)
#     if insight: base += f". Analysis: {insight}"
#     return base

# def compare_players(p1, p2):
#     s1 = get_player_stats(p1)
#     s2 = get_player_stats(p2)
#     res = search(f"{p1} vs {p2} IPL 2026 comparison better", mode="text", n=4)
#     sents = best_sentences(res, [p1.split()[0], p2.split()[0]])
#     result = f"{s1}. {s2}."
#     if sents: result += f" Head to head: {'. '.join(sents)}"
#     return result

# # ══════════════════════════════════════════════════════════════════════
# #  PITCH / WEATHER / TOSS / PLAYING 11
# # ══════════════════════════════════════════════════════════════════════
# VENUE_DB = {
#     "wankhede":      "High-scoring venue. Fast outfield. Average score 185. Dew is a major factor in second innings.",
#     "eden gardens":  "Spin-friendly track. Slower surface. Average score around 165. Home crowd advantage for KKR.",
#     "chinnaswamy":   "Batsman's paradise. Thin air aids sixes. Highest scoring IPL venue. Average 190 plus.",
#     "chepauk":       "Spin-friendly. Low and slow. Batsmen struggle early. Average 155-165.",
#     "narendra modi": "Flat pitch. Largest ground reduces scoring. Average 170-180.",
#     "arun jaitley":  "Batting friendly. Some early swing. Dew factor at night.",
#     "rajiv gandhi":  "Good batting track. Scores tend to be high. Pacers get movement initially.",
#     "sawai mansingh":"Spin-friendly. Dry surface. Good for leg spinners.",
#     "ekana":         "Balanced pitch. Home advantage for LSG. Scores around 165-175.",
# }

# def get_pitch_report():
#     match = get_today_match() or "IPL 2026"
#     res = search(f"{match} IPL 2026 pitch report venue stadium surface", mode="news", days="d", n=8)
#     txt = all_text(res)

#     venue_m = re.search(r'(?:at|in|venue[:\s]+)([\w\s]+(?:Stadium|Ground|Oval|Park|Arena|Gardens))', txt, re.IGNORECASE)
#     venue = venue_m.group(1).strip() if venue_m else ""

#     # Smart venue DB lookup
#     for key, info in VENUE_DB.items():
#         if key in (venue + txt).lower():
#             return f"Sir, pitch report for {venue or 'today'}: {info}"

#     # Clean body sentences
#     sents = best_sentences(res, ["pitch","surface","batting","spin","pace","bounce","assist","flat"])
#     if sents:
#         return f"Sir, pitch report: " + ". ".join(sents)
#     return f"Sir, today's pitch: Expected good batting conditions. Spinners may assist in later overs. Dew could be a factor."

# def get_weather():
#     match = get_today_match() or "IPL 2026"
#     cities = ["Mumbai","Chennai","Kolkata","Delhi","Bangalore","Bengaluru",
#               "Hyderabad","Ahmedabad","Jaipur","Lucknow","Mohali","Pune","Dharamsala"]
#     res_v = search(f"{match} IPL 2026 venue city location", mode="news", days="d", n=5)
#     vtxt  = all_text(res_v)
#     city  = next((c for c in cities if c.lower() in vtxt.lower()), "Mumbai")

#     res = search(f"{city} weather today cricket rain temperature dew", mode="news", days="d", n=6)
#     sents = best_sentences(res, ["weather","rain","temperature","dew","humid","clear","cloud","forecast"])
#     if sents:
#         return f"Sir, {city} weather: " + ". ".join(sents)
#     return f"Sir, {city}: Clear skies expected. Dew factor likely in second innings. Humidity moderate."

# def get_toss():
#     res = search("IPL 2026 today toss result won elected bat bowl", mode="news", days="d")
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             if any(w in line.lower() for w in ["toss","elected","chose to","won the toss"]):
#                 cl = clean(line.strip())
#                 if len(cl) > 15 and not is_junk(cl): return cl[:200]
#     return None

# def get_playing11():
#     res = search("IPL 2026 today playing 11 squad XI announced", mode="news", days="d")
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             if any(w in line.lower() for w in ["playing xi","playing 11","squad"]):
#                 cl = clean(line.strip())
#                 if len(cl) > 20 and not is_junk(cl): return cl[:200]
#     return None

# def get_injury_news(team=None):
#     q = f"{team} IPL 2026 injury ruled out fitness" if team else "IPL 2026 player injury ruled out update"
#     res = search(q, mode="news", days="w", n=8)
#     injuries = []
#     for r in res:
#         title = r.get("title","")
#         if any(w in title.lower() for w in ["injur","ruled out","doubtful","fitness","unavailable"]):
#             ct = clean(title.split("|")[0])
#             if len(ct) > 10 and not is_junk(ct) and ct not in injuries:
#                 injuries.append(ct)
#         sents = best_sentences([r], ["injur","ruled out","doubtful","unavailable","fitness"])
#         for s in sents:
#             if s not in injuries: injuries.append(s)
#         if len(injuries) >= 3: break
#     if injuries:
#         return "Sir, injury updates: " + ". ".join(list(dict.fromkeys(injuries))[:3])
#     return "Sir, no major injury concerns at the moment."

# def get_ipl_news():
#     res = search("IPL 2026 latest news today highlights cricket", mode="news", days="d", n=8)
#     items = []
#     for r in res:
#         title = r.get("title","")
#         ct = clean(title.split("|")[0])
#         if len(ct) > 15 and not is_junk(ct) and ct not in items:
#             items.append(ct)
#         if len(items) >= 4: break
#     return "Sir, IPL 2026 news: " + ". ".join(items) if items else "Sir, no fresh news right now."

# def get_fantasy_xi():
#     match = get_today_match()
#     if not match: return "Sir, today's match not found."
#     res = search(f"{match} IPL 2026 fantasy team best XI captain picks today", mode="text", n=8)
#     sents = best_sentences(res, ["captain","must pick","differential","fantasy","key pick","vice captain","best player"])
#     if sents:
#         return f"Sir, fantasy picks for {match}: " + ". ".join(sents[:3])
#     # Fallback player names
#     txt = all_text(res)
#     pf = []
#     for k,v in IPL_PLAYERS.items():
#         if k in txt.lower() and v not in pf: pf.append(v)
#         if len(pf) >= 8: break
#     if pf:
#         return f"Sir, recommended players for {match}: {', '.join(pf[:8])}. Choose your captain from the top 3."
#     return "Sir, fantasy data not available yet."

# def get_player_value(player):
#     res = search(f"{player} IPL 2026 auction price crore salary bid", mode="text", n=6)
#     txt = all_text(res)
#     m = re.search(r'(\d+(?:\.\d+)?)\s*(?:crore|cr)\b', txt, re.IGNORECASE)
#     if m:
#         val = m.group(1)
#         return f"Sir, {player} IPL 2026 auction value: {val} crore. A significant investment by the franchise."
#     sents = best_sentences(res, ["crore","auction","price","sold","bid"])
#     return f"Sir, {sents[0]}" if sents else f"Sir, {player} auction data not found."

# def get_team_strength(team):
#     res = search(f"{team} IPL 2026 squad analysis strength weakness key players", mode="text", n=6)
#     t0 = team.split()[0].lower()
#     parts = []
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body","")):
#             line = line.strip()
#             if is_junk(line) or len(line) < 20 or len(line) > 200: continue
#             if t0 in line.lower():
#                 if any(w in line.lower() for w in ["strong","weak","key","squad","batting","bowling","form","win","balance","depend"]):
#                     cl = clean(line)
#                     if cl and cl not in parts: parts.append(cl)
#             if len(parts) >= 3: break
#         if len(parts) >= 3: break
#     if parts:
#         return f"Sir, {team} analysis: " + ". ".join(parts[:3])
#     return f"Sir, {team}: Balanced squad. Check injury news before finalizing your fantasy team."

# def get_commentary():
#     queries = [
#         "IPL 2026 live commentary today six four wicket boundary latest",
#         "IPL 2026 today match ball by ball update",
#     ]
#     for q in queries:
#         res = search(q, mode="news", days="d", n=8)
#         sents = best_sentences(res, ["six","four","wicket","boundary","dot","single","caught",
#                                       "bowled","lbw","pulled","driven","smashed","over"])
#         if sents:
#             return "Sir, live commentary: " + ". ".join(sents[:3])
#     d = get_live_scorecard()
#     if d:
#         msg = f"Sir, {d.get('runs','?')} for {d.get('wickets','?')} in {d.get('overs','?')} overs"
#         if d.get("run_rate"):   msg += f". Run rate {d['run_rate']}"
#         if d.get("analysis"):   msg += f". {d['analysis']}"
#         return msg
#     return "Sir, live commentary not available right now."

# def get_h2h(t1, t2):
#     res = search(f"{t1} vs {t2} IPL head to head record wins history", mode="text", n=6)
#     sents = best_sentences(res, ["won","win","head","record","beat","times","clash"])
#     if sents:
#         return f"Sir, {t1} vs {t2}: " + ". ".join(sents[:2])
#     return f"Sir, {t1} vs {t2} head to head record not found."

# def get_bowlers_against(batsman):
#     first = batsman.split()[0]
#     res = search(f"bowler dismissed {batsman} most times IPL history record", mode="text", n=8)
#     txt = all_text(res)
#     bowlers = []
#     for bname in re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has|have|holds|is)', txt):
#         if bname.lower() not in batsman.lower() and len(bname) > 5:
#             bowlers.append(bname)
#     sents = best_sentences(res, ["dismiss","wicket","out","bowler","times"])
#     result = ""
#     if bowlers:
#         uniq = list(dict.fromkeys(bowlers))[:3]
#         result += f"Sir, {batsman} ka sabse bada nemesis: {', '.join(uniq)}. "
#         result += f"These bowlers have troubled {batsman} repeatedly in IPL. "
#     if sents: result += ". ".join(sents[:2])
#     return result or f"Sir, {batsman} ke against bowler record nahi mila."

# # ══════════════════════════════════════════════════════════════════════
# #  ML PREDICTIONS
# # ══════════════════════════════════════════════════════════════════════
# def predict_score(player):
#     scores = PLAYER_CACHE.get(player.lower(), {}).get("runs", [])
#     if len(scores) < 3:
#         get_player_stats(player)
#         scores = PLAYER_CACHE.get(player.lower(), {}).get("runs", [])
#     if len(scores) >= 3:
#         try:
#             from sklearn.linear_model import LinearRegression
#             X = np.array(range(len(scores))).reshape(-1,1)
#             pred = max(0, round(LinearRegression().fit(X, np.array(scores)).predict([[len(scores)]])[0]))
#             trend = "improving" if scores[-1] > scores[0] else "declining"
#             return pred, trend
#         except ImportError:
#             return round(sum(scores[-5:])/min(len(scores),5)), "stable"
#     return None, None

# def predict_wickets(player):
#     wickets = PLAYER_CACHE.get(player.lower(), {}).get("wickets", [])
#     if len(wickets) < 3:
#         get_bowling_stats(player)
#         wickets = PLAYER_CACHE.get(player.lower(), {}).get("wickets", [])
#     if len(wickets) >= 3:
#         try:
#             from sklearn.linear_model import LinearRegression
#             X = np.array(range(len(wickets))).reshape(-1,1)
#             pred = max(0, round(LinearRegression().fit(X, np.array(wickets)).predict([[len(wickets)]])[0]))
#             return pred
#         except ImportError:
#             return round(sum(wickets[-5:])/min(len(wickets),5))
#     return None

# def predict_win(runs, wickets, overs, target=185):
#     balls_done = int(overs)*6 + round((overs%1)*10)
#     balls_left = max(1, 120-balls_done)
#     runs_needed = max(1, target-runs)
#     req_rr = runs_needed/balls_left*6
#     curr_rr = (runs/overs) if overs > 0 else 0
#     chance = 50 + (curr_rr-req_rr)*5 - wickets*8
#     return max(5, min(95, round(chance)))

# # ══════════════════════════════════════════════════════════════════════
# #  GRAPHS - main thread via queue
# # ══════════════════════════════════════════════════════════════════════
# def _draw_momentum():
#     run_hist  = MATCH_STATE.get("run_history", [])
#     rr_hist   = MATCH_STATE.get("rr_history", [])
#     wkt_overs = MATCH_STATE.get("wicket_overs", [])
#     if len(run_hist) < 5:
#         np.random.seed(42)
#         run_hist = list(np.cumsum(np.random.randint(4,12,20)))
#         wkt_overs = [3,7,11,15,18]
#     n = len(run_hist)
#     # FIX: rr_hist same length as run_hist
#     if len(rr_hist) != n:
#         rr_hist = [round(run_hist[i]/(i+1),2) for i in range(n)]
#     overs  = list(range(1, n+1))
#     target = MATCH_STATE.get("target",0) or max(run_hist)+30
#     t1 = MATCH_STATE.get("team1","Team A")
#     t2 = MATCH_STATE.get("team2","Team B")

#     fig = plt.figure(figsize=(15,10), facecolor='#0d1117')
#     gs  = gridspec.GridSpec(3,2, figure=fig, hspace=0.45, wspace=0.35)

#     ax1 = fig.add_subplot(gs[0,:])
#     ax1.set_facecolor('#161b22')
#     ax1.plot(overs, run_hist, color='#00ff88', lw=2.5, marker='o', ms=4, label='Runs', zorder=3)
#     if target: ax1.axhline(target, color='#ff4444', lw=2, ls='--', label=f'Target {target}')
#     for wo in wkt_overs:
#         if 1 <= wo <= n: ax1.axvline(wo, color='#ff6b6b', lw=1.5, ls=':', alpha=0.7)
#     ax1.fill_between(overs, run_hist, alpha=0.15, color='#00ff88')
#     ax1.set_title(f'Match Momentum: {t1} vs {t2}', color='white', fontsize=13, fontweight='bold')
#     ax1.set_xlabel('Over', color='#8b949e'); ax1.set_ylabel('Runs', color='#8b949e')
#     ax1.tick_params(colors='#8b949e', labelsize=8)
#     ax1.legend(framealpha=0.3, labelcolor='white', fontsize=9)
#     for sp in ['top','right']: ax1.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax1.spines[sp].set_color('#30363d')
#     ax1.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

#     ax2 = fig.add_subplot(gs[1,0])
#     ax2.set_facecolor('#161b22')
#     rr_colors = ['#00ff88' if r>=8 else '#ffd700' if r>=6 else '#ef5350' for r in rr_hist]
#     # FIX: ensure overs and rr_hist same length
#     ax2.bar(overs[:len(rr_hist)], rr_hist, color=rr_colors[:len(rr_hist)], width=0.7, zorder=3)
#     avg_rr = np.mean(rr_hist)
#     ax2.axhline(avg_rr, color='#ff9800', lw=2, ls='--', alpha=0.8, label=f'Avg {avg_rr:.1f}')
#     ax2.set_title('Run Rate Per Over', color='white', fontsize=11, fontweight='bold')
#     ax2.set_xlabel('Over', color='#8b949e'); ax2.set_ylabel('RR', color='#8b949e')
#     ax2.tick_params(colors='#8b949e', labelsize=8)
#     ax2.legend(framealpha=0.3, labelcolor='white', fontsize=9)
#     for sp in ['top','right']: ax2.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax2.spines[sp].set_color('#30363d')
#     ax2.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

#     ax3 = fig.add_subplot(gs[1,1])
#     ax3.set_facecolor('#161b22')
#     pp_r  = run_hist[min(5,n-1)]
#     mid_r = max(0,(run_hist[min(14,n-1)]-run_hist[min(5,n-1)])) if n>6 else 0
#     dth_r = max(0,(run_hist[-1]-run_hist[min(14,n-1)])) if n>15 else 0
#     bars3 = ax3.bar(['Powerplay\n(1-6)','Middle\n(7-15)','Death\n(16-20)'],
#                     [pp_r,mid_r,dth_r], color=['#4fc3f7','#ffd700','#ff6b6b'], width=0.5, zorder=3)
#     for bar,val in zip(bars3,[pp_r,mid_r,dth_r]):
#         ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, str(val),
#                  ha='center', va='bottom', fontsize=10, color='white', fontweight='bold')
#     ax3.set_title('Runs by Phase', color='white', fontsize=11, fontweight='bold')
#     ax3.set_ylabel('Runs', color='#8b949e')
#     ax3.tick_params(colors='#8b949e', labelsize=9)
#     for sp in ['top','right']: ax3.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax3.spines[sp].set_color('#30363d')
#     ax3.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

#     ax4 = fig.add_subplot(gs[2,:])
#     ax4.set_facecolor('#161b22')
#     win_probs = []
#     for i,r in enumerate(run_hist):
#         ov  = i+1
#         wkt = sum(1 for wo in wkt_overs if wo<=ov)
#         win_probs.append(predict_win(r, wkt, float(ov), target))
#     ax4.plot(overs, win_probs, color='#e91e63', lw=2.5, marker='o', ms=3, zorder=3)
#     ax4.fill_between(overs, win_probs, 50, where=[w>=50 for w in win_probs],
#                      alpha=0.2, color='#00ff88', label='Batting ahead')
#     ax4.fill_between(overs, win_probs, 50, where=[w<50 for w in win_probs],
#                      alpha=0.2, color='#ef5350', label='Bowling ahead')
#     ax4.axhline(50, color='white', lw=1, ls='-', alpha=0.3)
#     ax4.set_title('Win Probability', color='white', fontsize=11, fontweight='bold')
#     ax4.set_xlabel('Over', color='#8b949e'); ax4.set_ylabel('Win %', color='#8b949e')
#     ax4.set_ylim(0,100)
#     ax4.tick_params(colors='#8b949e', labelsize=8)
#     ax4.legend(framealpha=0.3, labelcolor='white', fontsize=9)
#     for sp in ['top','right']: ax4.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax4.spines[sp].set_color('#30363d')
#     ax4.yaxis.grid(True, color='#21262d', lw=0.8, zorder=0)

#     plt.suptitle('JARVIS IPL ANALYTICS v10.0', color='#8b949e', fontsize=10, y=0.98)
#     plt.tight_layout()
#     plt.savefig('momentum_dashboard.png', dpi=150, bbox_inches='tight', facecolor='#0d1117')
#     plt.show()
#     print("Momentum dashboard saved!")

# def _draw_batting(player):
#     res = search(f"{player} IPL 2026 innings runs each match scorecard", mode="text", n=10)
#     txt = all_text(res)
#     scores = []
#     for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
#         v=int(h)
#         if 0<v<180: scores.append(v)
#     for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
#         v=int(h)
#         if 0<v<180: scores.append(v)
#     scores=list(dict.fromkeys(scores))
#     cs=PLAYER_CACHE.get(player.lower(),{}).get("runs",[])
#     if len(cs)>len(scores): scores=cs
#     if len(scores)<5:
#         avg=40
#         am=re.search(r'\b(\d{3,4})\s+runs\b', all_text(search(f"{player} IPL career runs",mode="text",n=4)), re.IGNORECASE)
#         if am: avg=min(75,max(15,int(am.group(1))//14))
#         np.random.seed(sum(ord(c) for c in player))
#         scores=[max(0,int(avg+np.random.randint(-int(avg*0.7),int(avg*1.2)))) for _ in range(14)]
#     scores=scores[-14:]; labels=[f"M{i+1}" for i in range(len(scores))]
#     colors=['#00ff88' if s>=75 else '#ffd700' if s>=50 else '#4fc3f7' if s>=25 else '#ef5350' for s in scores]
#     avg_v=np.mean(scores)
#     pred, trend = predict_score(player)

#     fig,ax=plt.subplots(figsize=(13,6))
#     fig.patch.set_facecolor('#0d1117'); ax.set_facecolor('#161b22')
#     bars=ax.bar(labels,scores,color=colors,width=0.6,zorder=3)
#     ax.plot(labels,scores,'white',lw=1.5,marker='o',ms=4,alpha=0.7,zorder=4)
#     ax.axhline(avg_v,color='#ff9800',lw=2,ls='--',alpha=0.8,label=f'Avg {avg_v:.1f}')
#     ax.axhline(50,color='#ffd700',lw=1,ls=':',alpha=0.4)
#     ax.axhline(100,color='#00ff88',lw=1,ls=':',alpha=0.4)
#     if pred: ax.axhline(pred,color='#e91e63',lw=2,ls='-.',alpha=0.9,label=f'ML Next: {pred} ({trend})')
#     for bar,s in zip(bars,scores):
#         ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1.5,str(s),
#                 ha='center',va='bottom',fontsize=9,color='white',fontweight='bold')
#     ax.set_xlabel('Match',color='#8b949e',fontsize=11)
#     ax.set_ylabel('Runs',color='#8b949e',fontsize=11)
#     ax.set_title(f'{player} - IPL 2026 Batting Analysis',color='white',fontsize=14,fontweight='bold',pad=15)
#     ax.tick_params(colors='#8b949e',labelsize=9)
#     for sp in ['top','right']: ax.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax.spines[sp].set_color('#30363d')
#     ax.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)
#     ax.set_ylim(0,max(scores)+35)
#     legend=[mpatches.Patch(color='#00ff88',label='75+ (Excellent)'),
#             mpatches.Patch(color='#ffd700',label='50-74 (Half century)'),
#             mpatches.Patch(color='#4fc3f7',label='25-49 (Decent)'),
#             mpatches.Patch(color='#ef5350',label='0-24 (Poor)'),
#             plt.Line2D([0],[0],color='#ff9800',lw=2,ls='--',label=f'Avg {avg_v:.1f}')]
#     if pred: legend.append(plt.Line2D([0],[0],color='#e91e63',lw=2,ls='-.',label=f'ML Pred {pred}'))
#     ax.legend(handles=legend,loc='upper right',framealpha=0.3,labelcolor='white',fontsize=9)
#     plt.tight_layout()
#     fname=player.replace(" ","_")+"_batting.png"
#     plt.savefig(fname,dpi=150,bbox_inches='tight',facecolor='#0d1117')
#     plt.show()
#     print(f"{fname} saved!")

# def _draw_bowling(player):
#     res=search(f"{player} IPL 2026 bowling figures wickets match",mode="text",n=10)
#     txt=all_text(res); wkts,eco=[],[]
#     for w,r in re.findall(r'\b([0-5])/(\d{1,3})\b',txt):
#         wv,rv=int(w),int(r)
#         if rv<80: wkts.append(wv); eco.append(round(rv/4,1))
#     cw=PLAYER_CACHE.get(player.lower(),{}).get("wickets",[])
#     if len(cw)>len(wkts): wkts=cw
#     if len(wkts)<5:
#         avg_w,avg_e=1.5,8.0
#         at=all_text(search(f"{player} IPL bowling career economy stats",mode="text",n=4))
#         em=re.search(r'economy[\s:]+(\d{1,2}\.?\d?)',at,re.IGNORECASE)
#         wm=re.search(r'(\d{2,3})\s+wickets?\s+in\s+(\d{2,3})',at,re.IGNORECASE)
#         if em: avg_e=min(14,max(5,float(em.group(1))))
#         if wm: avg_w=min(4,max(0.5,int(wm.group(1))/int(wm.group(2))))
#         np.random.seed(sum(ord(c) for c in player))
#         wkts=[max(0,min(5,int(round(avg_w+np.random.uniform(-1.2,1.8))))) for _ in range(14)]
#         eco=[round(max(4.5,min(14,avg_e+np.random.uniform(-2,2.5))),1) for _ in range(14)]
#     wkts=wkts[-14:]; eco=(eco[-14:] if len(eco)>=len(wkts) else [8.0]*len(wkts))
#     labels=[f"M{i+1}" for i in range(len(wkts))]; pw=predict_wickets(player)
#     fig,(ax1,ax2)=plt.subplots(2,1,figsize=(13,9),gridspec_kw={'height_ratios':[3,2]})
#     fig.patch.set_facecolor('#0d1117'); ax1.set_facecolor('#161b22')
#     wc=['#e91e63' if w==0 else '#ff9800' if w==1 else '#ffd700' if w==2 else '#00ff88' for w in wkts]
#     bars=ax1.bar(labels,wkts,color=wc,width=0.6,zorder=3)
#     ax1.plot(labels,wkts,'white',lw=1.5,marker='D',ms=5,alpha=0.7,zorder=4)
#     for bar,w in zip(bars,wkts):
#         ax1.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.05,str(w),
#                  ha='center',va='bottom',fontsize=10,color='white',fontweight='bold')
#     avg_wv=np.mean(wkts)
#     ax1.axhline(avg_wv,color='#03a9f4',lw=2,ls='--',alpha=0.8,label=f'Avg {avg_wv:.1f}')
#     if pw: ax1.axhline(pw,color='#e91e63',lw=2,ls='-.',alpha=0.9,label=f'ML Pred {pw}')
#     ax1.set_title(f'{player} - IPL 2026 Bowling Analysis',color='white',fontsize=14,fontweight='bold',pad=15)
#     ax1.set_ylabel('Wickets',color='#8b949e',fontsize=11); ax1.set_ylim(0,max(wkts)+2)
#     ax1.tick_params(colors='#8b949e',labelsize=9)
#     for sp in ['top','right']: ax1.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax1.spines[sp].set_color('#30363d')
#     ax1.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)
#     ax1.legend(loc='upper right',framealpha=0.3,labelcolor='white',fontsize=9)
#     ax2.set_facecolor('#161b22')
#     ax2.plot(labels,eco,color='#ff6b6b',lw=2.5,marker='o',ms=6,zorder=3)
#     ax2.fill_between(range(len(eco)),eco,alpha=0.2,color='#ff6b6b')
#     ax2.axhline(7.5,color='#ffd700',lw=1.5,ls=':',alpha=0.7,label='Good economy (7.5)')
#     ax2.axhline(np.mean(eco),color='#03a9f4',lw=2,ls='--',alpha=0.8,label=f'Avg {np.mean(eco):.1f}')
#     ax2.set_xlabel('Match',color='#8b949e',fontsize=11); ax2.set_ylabel('Economy',color='#8b949e',fontsize=11)
#     ax2.set_xticks(range(len(labels))); ax2.set_xticklabels(labels)
#     ax2.tick_params(colors='#8b949e',labelsize=9)
#     for sp in ['top','right']: ax2.spines[sp].set_visible(False)
#     for sp in ['bottom','left']: ax2.spines[sp].set_color('#30363d')
#     ax2.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)
#     ax2.legend(loc='upper right',framealpha=0.3,labelcolor='white',fontsize=9)
#     plt.tight_layout()
#     fname=player.replace(" ","_")+"_bowling.png"
#     plt.savefig(fname,dpi=150,bbox_inches='tight',facecolor='#0d1117')
#     plt.show()
#     print(f"{fname} saved!")

# # ══════════════════════════════════════════════════════════════════════
# #  PLAYER & TEAM MAPS
# # ══════════════════════════════════════════════════════════════════════
# IPL_PLAYERS = {
#     "rohit":"Rohit Sharma","hardik":"Hardik Pandya","pandya":"Hardik Pandya",
#     "bumrah":"Jasprit Bumrah","jasprit":"Jasprit Bumrah","suryakumar":"Suryakumar Yadav",
#     "sky":"Suryakumar Yadav","tilak":"Tilak Varma","varma":"Tilak Varma","boult":"Trent Boult",
#     "dhoni":"MS Dhoni","msd":"MS Dhoni","ruturaj":"Ruturaj Gaikwad","gaikwad":"Ruturaj Gaikwad",
#     "jadeja":"Ravindra Jadeja","deepak":"Deepak Chahar","chahar":"Deepak Chahar",
#     "shivam":"Shivam Dube","dube":"Shivam Dube","pathirana":"Matheesha Pathirana",
#     "virat":"Virat Kohli","kohli":"Virat Kohli","vk":"Virat Kohli",
#     "rajat":"Rajat Patidar","patidar":"Rajat Patidar",
#     "cameron":"Cameron Green","green":"Cameron Green","phil":"Phil Salt","salt":"Phil Salt",
#     "krunal":"Krunal Pandya","shreyas":"Shreyas Iyer","iyer":"Shreyas Iyer",
#     "venkatesh":"Venkatesh Iyer","narine":"Sunil Narine","sunil":"Sunil Narine",
#     "russell":"Andre Russell","andre":"Andre Russell","rinku":"Rinku Singh",
#     "varun":"Varun Chakravarthy","starc":"Mitchell Starc","angkrish":"Angkrish Raghuvanshi",
#     "rishabh":"Rishabh Pant","pant":"Rishabh Pant","jake":"Jake Fraser-McGurk",
#     "kuldeep":"Kuldeep Yadav","axar":"Axar Patel","mukesh":"Mukesh Kumar",
#     "stubbs":"Tristan Stubbs","karun":"Karun Nair","shashank":"Shashank Singh",
#     "prabhsimran":"Prabhsimran Singh","arshdeep":"Arshdeep Singh","rossouw":"Rilee Rossouw",
#     "maxwell":"Glenn Maxwell","sanju":"Sanju Samson","samson":"Sanju Samson",
#     "yashasvi":"Yashasvi Jaiswal","jaiswal":"Yashasvi Jaiswal","riyan":"Riyan Parag",
#     "parag":"Riyan Parag","jurel":"Dhruv Jurel","hetmyer":"Shimron Hetmyer",
#     "archer":"Jofra Archer","klaasen":"Heinrich Klaasen","heinrich":"Heinrich Klaasen",
#     "abhishek":"Abhishek Sharma","travis":"Travis Head","head":"Travis Head",
#     "cummins":"Pat Cummins","harshal":"Harshal Patel","shahbaz":"Shahbaz Ahmed",
#     "kl":"KL Rahul","rahul":"KL Rahul","nicholas":"Nicholas Pooran","pooran":"Nicholas Pooran",
#     "ravi":"Ravi Bishnoi","bishnoi":"Ravi Bishnoi","mohsin":"Mohsin Khan",
#     "miller":"David Miller","david":"David Miller","shubman":"Shubman Gill","gill":"Shubman Gill",
#     "sai":"Sai Sudharsan","sudharsan":"Sai Sudharsan","buttler":"Jos Buttler","jos":"Jos Buttler",
#     "rashid":"Rashid Khan","siraj":"Mohammed Siraj","mohammed":"Mohammed Siraj",
#     "umesh":"Umesh Yadav","rabada":"Kagiso Rabada","kagiso":"Kagiso Rabada",
# }
# IPL_TEAMS = {
#     "mumbai":"Mumbai Indians","mi":"Mumbai Indians",
#     "chennai":"Chennai Super Kings","csk":"Chennai Super Kings",
#     "rcb":"Royal Challengers Bengaluru","bangalore":"Royal Challengers Bengaluru",
#     "bengaluru":"Royal Challengers Bengaluru",
#     "kkr":"Kolkata Knight Riders","kolkata":"Kolkata Knight Riders",
#     "delhi":"Delhi Capitals","dc":"Delhi Capitals",
#     "punjab":"Punjab Kings","pbks":"Punjab Kings",
#     "rajasthan":"Rajasthan Royals","rr":"Rajasthan Royals",
#     "hyderabad":"Sunrisers Hyderabad","srh":"Sunrisers Hyderabad",
#     "sunrisers":"Sunrisers Hyderabad",
#     "lucknow":"Lucknow Super Giants","lsg":"Lucknow Super Giants",
#     "gujarat":"Gujarat Titans","gt":"Gujarat Titans",
# }
# def find_player(cmd):
#     cmd=cmd.lower()
#     for k,v in IPL_PLAYERS.items():
#         if k in cmd: return v
#     return None
# def find_teams(cmd):
#     cmd,found=cmd.lower(),[]
#     for k,v in IPL_TEAMS.items():
#         if k in cmd and v not in found: found.append(v)
#     return found


# # ══════════════════════════════════════════════════════════════════════
# #  NEW: MATCH SITUATION SUMMARY (complete broadcast-style)
# # ══════════════════════════════════════════════════════════════════════
# def get_full_match_situation():
#     """Pure data broadcast - NO news sentences, only scorecard + analysis"""
#     d = get_live_scorecard()
#     match = get_today_match()
    
#     if not d and not match:
#         return "Sir, no live match data available right now."
#     if not d:
#         return f"Sir, today's match is {match}. Live score not yet available."
    
#     runs    = d.get("runs", 0)
#     wickets = d.get("wickets", 0)
#     overs   = d.get("overs", 0.0)
#     rr      = d.get("run_rate", 0.0)
#     target  = d.get("target", 0)
#     req_rr  = d.get("req_rate", 0.0)
#     needed  = d.get("runs_needed", 0)
#     balls   = d.get("balls_left", 0)
#     part    = d.get("partnership", 0)
#     t1      = d.get("team1", MATCH_STATE.get("team1","")) or "batting team"
#     t2      = d.get("team2", MATCH_STATE.get("team2","")) or "bowling team"

#     msg = f"Sir, "

#     if target:
#         # 2nd innings chasing
#         if not needed and target and runs:
#             needed = target - runs
#         msg += f"{t1} need {needed} runs"
#         if balls: msg += f" from {balls} balls"
#         msg += f". Score: {runs} for {wickets} in {overs} overs."
#         msg += f" Current run rate {rr}."
#         if req_rr: msg += f" Required rate {req_rr}."
#         if part:   msg += f" Partnership {part} runs."
#     else:
#         # 1st innings - project wisely (factor in wickets)
#         remaining_overs = max(1, 20 - overs)
#         # Wicket-adjusted projection
#         wicket_factor = max(0.6, 1 - (wickets * 0.05))
#         proj = int(round(runs + (rr * remaining_overs * wicket_factor)))
#         msg += f"{t1}: {runs} for {wickets} in {overs} overs. "
#         msg += f"Run rate {rr}. Projected total {proj}."
#         if part: msg += f" Partnership {part} runs."

#     # Add intelligent analysis (our own logic, NOT from search)
#     analysis = analyze_situation(runs, wickets, overs, target)
#     if analysis:
#         msg += f" {analysis}"

#     return msg.strip()

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: VENUE HISTORY
# # ══════════════════════════════════════════════════════════════════════
# def get_venue_history():
#     match = get_today_match() or "IPL 2026"
#     # Get venue name first
#     res_v = search(f"{match} IPL 2026 venue stadium city", mode="news", days="d", n=5)
#     vtxt  = all_text(res_v)
#     venue_m = re.search(r'(\w[\w\s]+(?:Stadium|Ground|Oval|Park|Arena|Gardens))', vtxt, re.IGNORECASE)
#     venue = venue_m.group(1).strip() if venue_m else match.split(" vs ")[0]

#     # Smart venue DB
#     for key, info in VENUE_DB.items():
#         if key in (venue + vtxt).lower():
#             return f"Sir, {venue} history: {info}"

#     # Search venue stats
#     res = search(f"{venue} IPL T20 records average score history highest", mode="text", n=6)
#     sents = best_sentences(res, ["average","record","highest","history","venue","score","won","last"])
#     if sents:
#         return f"Sir, {venue}: " + ". ".join(sents[:2])
#     return f"Sir, {venue}: Venue data not available. Check pitch report for surface conditions."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: PLAYER FORM GUIDE (last 5 matches analysis)
# # ══════════════════════════════════════════════════════════════════════
# def get_player_form(player):
#     res = search(f"{player} IPL 2026 recent form last 5 matches performance", mode="text", n=8)
#     txt = all_text(res)
    
#     # Get scores
#     scores = []
#     for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
#         v = int(h)
#         if 0 < v < 180: scores.append(v)
#     scores = list(dict.fromkeys(scores))[:5]
    
#     sents = best_sentences(res, ["form","in form","out of form","performing","consecutive","run","innings"])
    
#     if scores:
#         avg = round(sum(scores)/len(scores), 1)
#         trend = ""
#         if len(scores) >= 3:
#             if scores[-1] > scores[0]: trend = "Form is improving."
#             elif scores[-1] < scores[0]: trend = "Form has been declining."
#             else: trend = "Form is consistent."
        
#         result = f"Sir, {player} recent form: Last scores {scores}. Average {avg}. {trend}"
#         if sents: result += " " + sents[0]
#         return result
    
#     if sents:
#         return f"Sir, {player} form: " + ". ".join(sents[:2])
#     return f"Sir, {player} ka recent form data nahi mila."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: MATCH PREDICTION (before match starts)
# # ══════════════════════════════════════════════════════════════════════
# def get_match_prediction():
#     match = get_today_match()
#     if not match:
#         return "Sir, today's match not found for prediction."
    
#     res = search(f"{match} IPL 2026 prediction who will win today analysis", mode="text", n=8)
#     sents = best_sentences(res, ["predict","favourite","win","likely","chance","advantage","stronger"])
    
#     if sents:
#         return f"Sir, match prediction for {match}: " + ". ".join(sents[:3])
    
#     # Fallback: H2H based
#     teams = match.split(" vs ")
#     if len(teams) == 2:
#         h2h = get_h2h(teams[0].strip(), teams[1].strip())
#         return f"Sir, {match} prediction based on head to head: {h2h}"
#     return f"Sir, prediction for {match} not available."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: BEST PARTNERSHIP IN MATCH
# # ══════════════════════════════════════════════════════════════════════
# def get_partnerships():
#     match = get_today_match() or "IPL 2026"
#     res = search(f"{match} IPL 2026 partnership batting pair stand today", mode="news", days="d", n=8)
#     sents = best_sentences(res, ["partnership","stand","pair","together","added","runs for","unbeaten"])
#     match_kw = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
#     for s in sents:
#         if match_kw in s.lower() or "partnership" in s.lower():
#             return "Sir, " + s
#     d = get_live_scorecard()
#     if d and d.get("partnership"):
#         return f"Sir, current partnership is {d['partnership']} runs."
#     # Fallback: mention from scorecard analysis
#     if d:
#         return f"Sir, score is {d.get('runs')} for {d.get('wickets')} in {d.get('overs')} overs. Partnership data not in feed."
#     return "Sir, partnership data not available right now."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: QUICK MATCH SUMMARY (like end of over update)
# # ══════════════════════════════════════════════════════════════════════
# def get_over_summary():
#     match = get_today_match() or "IPL 2026"
#     queries = [
#         f"{match} IPL 2026 last over runs wickets update",
#         f"IPL 2026 today last over update {match}",
#     ]
#     for q in queries:
#         res = search(q, mode="news", days="d", n=6)
#         sents = best_sentences(res, ["over","runs in the over","over ended","conceded","last over","this over"])
#         if sents:
#             # Verify it mentions today's match
#             match_team = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else ""
#             for s in sents:
#                 if not match_team or match_team in s.lower():
#                     return "Sir, over update: " + s
#     return get_full_match_situation()

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: IPL 2026 RECORDS  
# # ══════════════════════════════════════════════════════════════════════
# def get_ipl_records():
#     res = search("IPL 2026 records highest score most sixes fastest fifty century", mode="text", n=6)
#     sents = best_sentences(res, ["record","highest","most","fastest","century","six","fifty"])
#     if sents:
#         return "Sir, IPL 2026 records: " + ". ".join(sents[:3])
#     return "Sir, IPL 2026 records not available right now."


# # ══════════════════════════════════════════════════════════════════════
# #  NEW: DREAM TEAM (Best possible XI from both teams)
# # ══════════════════════════════════════════════════════════════════════
# def get_dream_team():
#     match = get_today_match()
#     if not match: return "Sir, today's match not found."
#     teams = match.split(" vs ") if " vs " in match else []
    
#     res = search(f"{match} IPL 2026 best players form in-form strongest XI today", mode="text", n=8)
#     sents = best_sentences(res, ["best","in form","key player","dangerous","threat","star","top performer"])
    
#     result = f"Sir, dream team analysis for {match}: "
#     if sents:
#         result += ". ".join(sents[:3])
#     else:
#         # Build from known players
#         players_found = []
#         txt = all_text(res)
#         for k, v in IPL_PLAYERS.items():
#             if k in txt.lower() and v not in players_found:
#                 players_found.append(v)
#             if len(players_found) >= 11: break
#         if players_found:
#             result += f"Recommended XI: {', '.join(players_found[:11])}"
#         else:
#             result += "Data not available yet."
#     return result

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: PLAYER MILESTONE TRACKER
# # ══════════════════════════════════════════════════════════════════════
# def get_player_milestones(player):
#     res = search(f"{player} IPL 2026 milestone 1000 runs 100 wickets record close to", mode="text", n=6)
#     sents = best_sentences(res, ["milestone","record","close","away from","needs","require","century",
#                                   "1000 runs","100 wickets","50 wickets"])
#     if sents:
#         return f"Sir, {player} milestone watch: " + ". ".join(sents[:2])
#     # Check career stats
#     stats = get_player_stats(player)
#     return f"Sir, {player} milestones: Check career stats. {stats}"

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: BOWLER SPELL ANALYSIS
# # ══════════════════════════════════════════════════════════════════════
# def get_bowler_spell(bowler):
#     match = get_today_match() or "IPL 2026"
#     res = search(f"{bowler} {match} IPL 2026 bowling spell today figures overs wickets", mode="news", days="d", n=6)
#     sents = best_sentences(res, ["spell","figures","overs","wickets","economy","bowled","lbw","caught"])
#     match_kw = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
#     for s in sents:
#         if bowler.split()[0].lower() in s.lower() or match_kw in s.lower():
#             return f"Sir, {bowler} today: {s}"
#     return get_bowling_stats(bowler)

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: BATTING SCORECARD (who is batting, runs, balls)
# # ══════════════════════════════════════════════════════════════════════
# def get_batting_scorecard():
#     match = get_today_match() or "IPL 2026"
#     res = search(f"{match} IPL 2026 live batting scorecard batsmen runs balls today", mode="news", days="d", n=8)
#     sents = best_sentences(res, ["batting","batsman","runs off","not out","at crease","opening","captain"])
#     match_kw = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
#     valid = [s for s in sents if match_kw in s.lower() or "batting" in s.lower()]
#     if valid:
#         return "Sir, batting update: " + ". ".join(valid[:2])
#     d = get_live_scorecard()
#     if d:
#         return f"Sir, {d.get('team1','batting team')} batting: {d.get('runs')} for {d.get('wickets')} in {d.get('overs')} overs."
#     return "Sir, batting scorecard not available right now."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: BOWLING FIGURES (who is bowling, economy)
# # ══════════════════════════════════════════════════════════════════════
# def get_bowling_scorecard():
#     match = get_today_match() or "IPL 2026"
#     res = search(f"{match} IPL 2026 live bowling figures economy wickets today", mode="news", days="d", n=8)
#     sents = best_sentences(res, ["bowling","bowler","figures","economy","spell","wickets","over"])
#     match_kw = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
#     valid = [s for s in sents if match_kw in s.lower() or "bowl" in s.lower()]
#     if valid:
#         return "Sir, bowling update: " + ". ".join(valid[:2])
#     return "Sir, bowling scorecard not available in live feed right now."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: TOSS ANALYSIS (what toss means strategically)
# # ══════════════════════════════════════════════════════════════════════
# def get_toss_analysis():
#     toss = get_toss()
#     pitch = get_pitch_report()
#     weather_data = get_weather()
    
#     if not toss:
#         return "Sir, toss not done yet."
    
#     result = f"Toss: {toss}. "
    
#     # Analyze toss decision
#     toss_l = toss.lower()
#     if "chose to bat" in toss_l or "elected to bat" in toss_l:
#         result += "Decision to bat first. Will look to post a big target."
#         if "dew" in (pitch + weather_data).lower():
#             result += " Smart choice given dew factor in second innings."
#     elif "chose to field" in toss_l or "elected to field" in toss_l:
#         result += "Decision to chase. Preference for knowing the target."
#         if "dew" in (pitch + weather_data).lower():
#             result += " Dew will assist batting in second innings."
    
#     return f"Sir, {result}"

# # ══════════════════════════════════════════════════════════════════════
# #  SENTINEL - background auto alerts
# # ══════════════════════════════════════════════════════════════════════
# def sentinel(speaker):
#     global last_score_state
#     pythoncom.CoInitialize()
#     while tracking_active:
#         try:
#             data = get_live_scorecard()
#             if data:
#                 runs    = data.get("runs",0)
#                 wickets = data.get("wickets",0)
#                 overs   = data.get("overs",0.0)
#                 rr      = data.get("run_rate",0.0)
#                 part    = data.get("partnership",0)

#                 if wickets > last_score_state['wickets'] >= 0:
#                     ov_str = f"in {overs} overs" if overs > 0 else ""
#                     msg = f"Sir, wicket has fallen. Score is {runs} for {wickets} {ov_str}."
#                     if data.get("analysis"): msg += f" {data['analysis']}"
#                     print(f"\n*** WICKET ALERT: {msg}")
#                     speaker.Speak(msg)

#                 if last_score_state['runs'] > 0:
#                     if runs//50 > last_score_state['runs']//50:
#                         speaker.Speak(f"Sir, batting team has crossed {(runs//50)*50} runs.")
#                     if part >= 100 and last_score_state.get("partnership",0) < 100:
#                         speaker.Speak("Sir, century partnership. Outstanding batting display.")
#                     if rr > 12 and last_score_state.get("rr",0) <= 12:
#                         speaker.Speak(f"Sir, exceptional run rate of {rr} right now.")

#                 last_score_state.update(runs=runs,wickets=wickets,overs=overs,rr=rr,partnership=part)
#         except Exception as e:
#             print(f"[Sentinel] {e}")
#         time.sleep(60)

# # ══════════════════════════════════════════════════════════════════════
# #  MAIN VOICE LOOP
# # ══════════════════════════════════════════════════════════════════════
# def jarvis_loop(speaker):
#     pythoncom.CoInitialize()

#     def speak(text):
#         print(f"\nJarvis: {text}")
#         speaker.Speak(text)

#     def listen_once(timeout=8):
#         with sr.Microphone() as src:
#             rec.adjust_for_ambient_noise(src, duration=0.3)
#             audio = rec.listen(src, timeout=timeout, phrase_time_limit=8)
#         return rec.recognize_google(audio, language="en-IN").strip()

#     threading.Thread(target=sentinel, args=(speaker,), daemon=True).start()
#     rec = sr.Recognizer()
#     rec.dynamic_energy_threshold = True
#     speak("Jarvis online, sir. IPL 2026 intelligence systems fully operational. How can I assist you?")

#     while True:
#         try:
#             with sr.Microphone() as src:
#                 print("\n[Listening]")
#                 rec.adjust_for_ambient_noise(src, duration=0.5)
#                 audio = rec.listen(src, timeout=10, phrase_time_limit=10)
#             print("[Recognizing]")
#             cmd = rec.recognize_google(audio, language="en-IN").lower().strip()
#             print(f"You said: '{cmd}'")

#             # WAKE
#             if cmd.strip() in ["jarvis","hey jarvis"]:
#                 speak("Yes sir, ready.")

#             # TODAY MATCH
#             elif any(w in cmd for w in ["today match","aaj ka match","kiska match","kaun khel",
#                                          "ipl today","which match","aaj kaun","kon khel raha"]):
#                 speak("Checking today's IPL match sir...")
#                 ans = get_today_match()
#                 if ans:
#                     speak(f"Sir, today's match is {ans}. Should I pull up the live score as well?")
#                 else:
#                     speak("Sir, today's match information not found right now.")

#             # FULL SCORECARD
#             elif any(w in cmd for w in ["full score","scorecard","full update","complete score","poora score"]):
#                 speak("Pulling full live scorecard sir...")
#                 d = get_live_scorecard()
#                 if d:
#                     msg = f"Sir, current score is {d.get('runs','?')} for {d.get('wickets','?')} wickets in {d.get('overs','?')} overs."
#                     if d.get("run_rate"):    msg += f" Run rate {d['run_rate']}."
#                     if d.get("target"):      msg += f" Target is {d['target']}."
#                     if d.get("req_rate"):    msg += f" Required rate {d['req_rate']}."
#                     if d.get("runs_needed"): msg += f" Need {d['runs_needed']} more runs."
#                     if d.get("partnership"): msg += f" Current partnership {d['partnership']}."
#                     if d.get("balls_left"):  msg += f" {d['balls_left']} balls remaining."
#                     if d.get("analysis"):    msg += f" Assessment: {d['analysis']}"
#                     speak(msg)
#                 else:
#                     speak("Sir, live scorecard not available at the moment.")

#             # QUICK SCORE
#             elif any(w in cmd for w in ["score","kya hua","kitne run","live","status","update","kya score","kya chal raha"]):
#                 speak("Fetching fresh score sir...")
#                 d = get_live_scorecard()
#                 if d:
#                     msg = f"Sir, {d.get('runs','?')} for {d.get('wickets','?')} in {d.get('overs','?')} overs."
#                     if d.get("run_rate"): msg += f" Run rate {d['run_rate']}."
#                     if d.get("analysis"): msg += f" {d['analysis']}"
#                     speak(msg)
#                 else:
#                     ans = get_today_match()
#                     speak(f"Sir, live score not available. Today's match is {ans}." if ans else "No live match right now sir.")

#             # RUN RATE
#             elif any(w in cmd for w in ["run rate","required rate","rrr","current rate","kitna rate","crr"]):
#                 d = get_live_scorecard()
#                 if d:
#                     msg = "Sir, "
#                     if d.get("run_rate"):   msg += f"current run rate {d['run_rate']}. "
#                     if d.get("req_rate"):   msg += f"Required rate {d['req_rate']}. "
#                     if d.get("balls_left"): msg += f"{d['balls_left']} balls remaining. "
#                     if d.get("analysis"):   msg += d['analysis']
#                     speak(msg)
#                 else:
#                     speak("Sir, no live match data available.")

#             # COMMENTARY
#             elif any(w in cmd for w in ["commentary","ball by ball","kya hua abhi","last ball","what happened just now"]):
#                 speak("Getting latest from the ground sir...")
#                 speak(get_commentary())

#             # SCHEDULE
#             elif any(w in cmd for w in ["next match","agle match","tomorrow","kal ka match","upcoming"]):
#                 speak("Checking tomorrow's fixture sir...")
#                 speak(get_schedule("tomorrow"))

#             elif any(w in cmd for w in ["last match","yesterday","kal hua","pichle match","previous match"]):
#                 speak("Checking yesterday's result sir...")
#                 speak(get_schedule("yesterday"))

#             elif any(w in cmd for w in ["schedule","fixture","kab hai","aaj ka schedule"]):
#                 speak("Checking today's schedule sir...")
#                 speak(get_schedule("today"))

#             # POINTS TABLE
#             elif any(w in cmd for w in ["points table","standings","ranking","kaun upar","table","leaderboard","playoff"]):
#                 speak("Fetching IPL 2026 standings sir...")
#                 speak(get_points_table())

#             # ORANGE CAP
#             elif any(w in cmd for w in ["orange cap","top scorer","most runs","leading batsman","batting leader","run list"]):
#                 speak("Checking orange cap standings sir...")
#                 speak(get_orange_cap())

#             # PURPLE CAP
#             elif any(w in cmd for w in ["purple cap","top wicket","most wickets","leading bowler","bowling leader","wicket list"]):
#                 speak("Checking purple cap standings sir...")
#                 speak(get_purple_cap())

#             # PITCH
#             elif any(w in cmd for w in ["pitch","pitch report","surface","ground report","wicket report"]):
#                 speak("Fetching pitch report sir...")
#                 speak(get_pitch_report())

#             # WEATHER
#             elif any(w in cmd for w in ["weather","rain","mausam","barish","temperature","dew","forecast","cloud"]):
#                 speak("Checking weather conditions sir...")
#                 speak(get_weather())

#             # INJURY
#             elif any(w in cmd for w in ["injury","injured","fit","fitness","ruled out","unavailable","kaun fit","playing or not"]):
#                 teams = find_teams(cmd)
#                 speak("Checking latest injury updates sir...")
#                 speak(get_injury_news(teams[0] if teams else None))

#             # NEWS
#             elif any(w in cmd for w in ["news","latest","highlights","headlines","kya hua aaj","updates","breaking"]):
#                 speak("Fetching latest IPL 2026 news sir...")
#                 speak(get_ipl_news())

#             # FANTASY
#             elif any(w in cmd for w in ["fantasy","dream11","best 11","fantasy team","who to pick","best pick","team suggestion"]):
#                 speak("Analyzing best fantasy picks sir...")
#                 speak(get_fantasy_xi())

#             # AUCTION VALUE
#             elif any(w in cmd for w in ["auction","price","value","crore","kitne mein","salary","worth","bought"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Checking {player} IPL value sir...")
#                 speak(get_player_value(player))

#             # TEAM STRENGTH
#             elif any(w in cmd for w in ["team strength","squad analysis","team form","team analysis","kaisi team","squad"]):
#                 teams = find_teams(cmd)
#                 if teams:
#                     speak(f"Analyzing {teams[0]} sir...")
#                     speak(get_team_strength(teams[0]))
#                 else:
#                     speak("Which team sir?")
#                     try:
#                         tc = listen_once()
#                         t = find_teams(tc)
#                         speak(get_team_strength(t[0]) if t else "Team not recognized sir.")
#                     except: continue

#             # WIN PREDICTION
#             elif any(w in cmd for w in ["predict","kaun jeetega","win","chance","jeetne","winner","win probability","who will win"]):
#                 d = get_live_scorecard()
#                 if d and d.get("runs"):
#                     prob = predict_win(d['runs'],d.get('wickets',0),d.get('overs',1),d.get('target',185))
#                     msg = f"Sir, based on current match dynamics, batting team has {prob} percent chance of winning."
#                     if d.get("analysis"): msg += f" {d['analysis']}"
#                     speak(msg)
#                 else:
#                     speak("Sir, which player prediction? Batting or bowling?")
#                     try:
#                         pred_cmd = listen_once().lower()
#                         player = find_player(pred_cmd) or pred_cmd.strip().title()
#                         if "bowl" in pred_cmd or "wicket" in pred_cmd:
#                             pred = predict_wickets(player)
#                             if pred is not None:
#                                 speak(f"Sir, {player} predicted to take {pred} wickets next match based on recent form.")
#                             else:
#                                 speak("Sir, insufficient bowling data for prediction.")
#                         else:
#                             pred, trend = predict_score(player)
#                             if pred is not None:
#                                 speak(f"Sir, {player} predicted next innings: {pred} runs. Form is {trend}.")
#                             else:
#                                 speak("Sir, insufficient batting data for prediction.")
#                     except:
#                         speak("Sir, prediction needs more data.")

#             # TOSS / PLAYING 11
#             elif any(w in cmd for w in ["toss","playing 11","playing eleven","squad","eleven","starting xi"]):
#                 speak("Checking toss and playing eleven sir...")
#                 toss = get_toss(); p11 = get_playing11()
#                 if toss: speak(toss)
#                 if p11:  speak(p11)
#                 if not toss and not p11: speak("Sir, toss information not announced yet.")

#             # PLAYER BATTING STATS
#             elif any(w in cmd for w in ["stats","performance","kaisa khelta","batting stats","runs banaye","innings"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Analyzing {player} sir...")
#                 speak(get_player_stats(player))

#             # BOWLING STATS
#             elif any(w in cmd for w in ["bowling stats","bowling record","kitne wicket","bowling figures","economy","bowling form"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which bowler sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Analyzing {player} bowling sir...")
#                 speak(get_bowling_stats(player))

#             # COMPARE
#             elif any(w in cmd for w in ["compare","versus","better","mukabla","kaun behtar"]):
#                 plist = []
#                 for k,v in IPL_PLAYERS.items():
#                     if k in cmd and v not in plist: plist.append(v)
#                 if len(plist) >= 2:
#                     p1,p2 = plist[0],plist[1]
#                 else:
#                     speak("Sir, which two players? Say both names with 'and' in between.")
#                     try:
#                         said = listen_once()
#                         if " and " in said.lower():
#                             pts = said.lower().split(" and ")
#                             p1 = find_player(pts[0]) or pts[0].strip().title()
#                             p2 = find_player(pts[1]) or pts[1].strip().title()
#                         else: speak("Please use 'and' between names sir."); continue
#                     except: continue
#                 speak(f"Comparing {p1} and {p2} sir...")
#                 speak(compare_players(p1,p2))

#             # MOMENTUM GRAPH
#             elif any(w in cmd for w in ["momentum","dashboard","analytics","match graph","full graph","match analysis"]):
#                 speak("Generating full analytics dashboard sir. Opening graph now...")
#                 GRAPH_QUEUE.put(("momentum", None))

#             # BATTING GRAPH
#             elif any(w in cmd for w in ["batting graph","run graph","batting chart","batting analysis"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which batsman sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Generating {player} batting analysis sir...")
#                 GRAPH_QUEUE.put(("batting", player))

#             # BOWLING GRAPH
#             elif any(w in cmd for w in ["bowling graph","wicket graph","bowling chart","bowling analysis"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which bowler sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Generating {player} bowling analysis sir...")
#                 GRAPH_QUEUE.put(("bowling", player))

#             # GENERIC GRAPH
#             elif any(w in cmd for w in ["graph","chart","dikhao","analysis graph"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak("Batting or bowling graph sir?")
#                 try:
#                     gt = listen_once().lower()
#                     GRAPH_QUEUE.put(("batting" if any(w in gt for w in ["bat","run"]) else "bowling", player))
#                 except:
#                     GRAPH_QUEUE.put(("batting", player))

#             # HEAD TO HEAD
#             elif any(w in cmd for w in ["head to head","h2h","history between","record between"]):
#                 teams = find_teams(cmd)
#                 if len(teams) >= 2:
#                     speak(f"Checking {teams[0]} vs {teams[1]} head to head sir...")
#                     speak(get_h2h(teams[0],teams[1]))
#                 else:
#                     speak("Sir, please name two teams. Example: MI vs CSK head to head.")

#             # BOWLERS AGAINST BATSMAN
#             elif any(w in cmd for w in ["kaun out karega","weakness","kamzori","kaun out kar","dismiss",
#                                          "out kar sakta","out karega","bowler against","enemy","nemesis"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which batsman sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Analyzing threats against {player} sir...")
#                 speak(get_bowlers_against(player))

#             # HELP
            
#             # FULL SITUATION (broadcast style)
#             elif any(w in cmd for w in ["situation","match situation","full update","poori update","full status","kya ho raha","complete update"]):
#                 speak("Getting complete match situation sir...")
#                 speak(get_full_match_situation())

#             # FORM GUIDE
#             elif any(w in cmd for w in ["form","recent form","last 5","kaise chal raha","current form","in form","out of form"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Analyzing {player} recent form sir...")
#                 speak(get_player_form(player))

#             # MATCH PREDICTION (pre-match)
#             elif any(w in cmd for w in ["match prediction","today prediction","who will win today","aaj kaun jeetega","pre match","before match"]):
#                 speak("Analyzing today's match prediction sir...")
#                 speak(get_match_prediction())

#             # VENUE HISTORY
#             elif any(w in cmd for w in ["venue history","ground history","venue record","ground record","past matches here"]):
#                 speak("Checking venue history sir...")
#                 speak(get_venue_history())

#             # PARTNERSHIP UPDATE
#             elif any(w in cmd for w in ["partnership","batting pair","stand","current pair","kaun batting"]):
#                 speak("Checking partnership update sir...")
#                 speak(get_partnerships())

#             # OVER UPDATE
#             elif any(w in cmd for w in ["last over","over update","over mein","over summary","over report","this over"]):
#                 speak("Getting over update sir...")
#                 speak(get_over_summary())

#             # IPL RECORDS
#             elif any(w in cmd for w in ["records","ipl record","highest score","most sixes","fastest","century record"]):
#                 speak("Fetching IPL 2026 records sir...")
#                 speak(get_ipl_records())

#             # DREAM TEAM
#             elif any(w in cmd for w in ["dream team","best xi","strongest xi","best playing 11","ideal team","team of the day"]):
#                 speak("Building dream team for today sir...")
#                 speak(get_dream_team())

#             # BATTING SCORECARD
#             elif any(w in cmd for w in ["who is batting","batting scorecard","batsman score","current batsman","at crease","kaun batting"]):
#                 speak("Checking batting scorecard sir...")
#                 speak(get_batting_scorecard())

#             # BOWLING SCORECARD
#             elif any(w in cmd for w in ["who is bowling","bowling scorecard","bowler figures","current bowler","kaun bowling"]):
#                 speak("Checking bowling scorecard sir...")
#                 speak(get_bowling_scorecard())

#             # BOWLER SPELL
#             elif any(w in cmd for w in ["spell","today spell","bowling today","figures today","ka spell"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which bowler sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Checking {player} spell sir...")
#                 speak(get_bowler_spell(player))

#             # MILESTONE TRACKER
#             elif any(w in cmd for w in ["milestone","record close","kitne runs chahiye","how many runs","record break","approaching"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Checking {player} milestones sir...")
#                 speak(get_player_milestones(player))

#             # TOSS ANALYSIS
#             elif any(w in cmd for w in ["toss analysis","toss ka matlab","toss decision","why bat","why field","toss impact"]):
#                 speak("Analyzing toss decision sir...")
#                 speak(get_toss_analysis())

#             # HELP
#             elif any(w in cmd for w in ["help","kya kar sakta","features","commands","capabilities","what can you do"]):
#                 speak("Sir, I am your IPL 2026 intelligence system. Commands: Score. Full scorecard. Match situation. Run rate. Commentary. Over update. Who is batting. Who is bowling. Partnership. Toss analysis. Pitch report. Venue history. Weather. Today match. Next match. Last match. Points table. Orange cap. Purple cap. Player stats. Bowling stats. Player form. Player milestone. Bowler spell today. Compare players. Win prediction. Match prediction. Fantasy team. Dream team. Auction price. Squad analysis. Injury updates. News. Head to head. Bowler vs batsman. Batting graph. Bowling graph. Momentum dashboard. IPL records.")

#             # EXIT
#             elif any(w in cmd for w in ["exit","stop","bye","goodbye","band karo","shutdown","shut down","close"]):
#                 speak("Goodbye sir. Jarvis signing off. Enjoy the cricket.")
#                 os._exit(0)

#         except sr.WaitTimeoutError: pass
#         except sr.UnknownValueError: pass
#         except Exception as ex:
#             print(f"[Loop] {ex}")
#             time.sleep(1)

# # ══════════════════════════════════════════════════════════════════════
# if __name__ == "__main__":
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")

#     print("=" * 70)
#     print("  JARVIS IPL INTELLIGENCE AGENT v11.0 REAL AGENT PRO")
#     print("=" * 70)
#     print("  LIVE    | score | full score | run rate | commentary | analysis")
#     print("  MATCH   | today match | toss | playing 11 | pitch | weather")
#     print("  INTEL   | news | injury | fantasy | orange cap | purple cap")
#     print("  STATS   | Virat stats | Bumrah bowling | compare Virat and Rohit")
#     print("  VALUE   | Virat auction price | MI squad analysis")
#     print("  PREDICT | predict | win probability | Virat next score")
#     print("  GRAPHS  | momentum | Virat batting graph | Bumrah bowling graph")
#     print("  H2H     | MI vs CSK head to head | Virat ko kaun out kar sakta")
#     print("  TABLE   | points table | next match | last match | schedule")
#     print("  AUTO    | Wicket | Milestone | Partnership | RR alerts running")
#     print("=" * 70)
#     print()
#     print("  NEW: Every answer includes INTELLIGENT ANALYSIS + INSIGHTS")
#     print("  NEW: Score is ALWAYS FRESH - no stale cache")
#     print("  NEW: Venue-specific pitch reports (Wankhede, Eden, Chinnaswamy...)")
#     print("=" * 70)
#     print()

#     vt = threading.Thread(target=jarvis_loop, args=(speaker,), daemon=True)
#     vt.start()

#     # Main thread handles graphs
#     while True:
#         try:
#             task, arg = GRAPH_QUEUE.get(timeout=1)
#             if   task == "momentum": _draw_momentum()
#             elif task == "batting":  _draw_batting(arg)
#             elif task == "bowling":  _draw_bowling(arg)
#         except queue.Empty:
#             pass
#         except Exception as e:
#             print(f"[Graph] {e}")

# """
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║         JARVIS - REAL IPL 2026 INTELLIGENCE AGENT v13.0                ║
# ║                                                                          ║
# ║  ENGINE:   ML Brain (LinearRegression) + Local LLM (Ollama/Mistral)    ║
# ║  DATA:     DDGS Live Search - Fresh every query                         ║
# ║  GRAPHS:   Batting | Bowling | Momentum Dashboard (ML-powered)          ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# INSTALL:
#     pip install duckduckgo-search speechrecognition pywin32 pyaudio
#     pip install matplotlib numpy scikit-learn ollama

# OLLAMA SETUP (for LLM features):
#     1. Download: https://ollama.com
#     2. Run: ollama pull mistral
#     3. Start: ollama serve
#     (Jarvis works without Ollama too — uses rule-based fallback)

# RUN:
#     python main.py
# """

# import re, time, os, threading, queue
# import pythoncom, win32com.client
# import speech_recognition as sr
# import numpy as np

# # ── Project modules ────────────────────────────────────────────────
# from ml_brain   import (predict_future_score, predict_future_wickets,
#                          calculate_win_probability, extract_scores_from_text,
#                          extract_wickets_from_text)
# from llm_expert import (get_expert_analysis, get_match_insight,
#                           get_fantasy_insight, get_h2h_insight,
#                           get_pitch_insight, get_toss_insight,
#                           check_llm_status)
# from scraper    import (search, all_text, best_sentences, is_junk, clean,
#                          get_live_scorecard, get_today_match, get_schedule,
#                          get_points_table, get_orange_cap, get_purple_cap,
#                          get_player_raw_data, get_toss, get_playing11,
#                          get_injury_news, get_ipl_news)
# from graphs     import (draw_batting_graph, draw_bowling_graph,
#                           draw_momentum_dashboard)

# # ══════════════════════════════════════════════════════════════════════
# #  GLOBAL STATE
# # ══════════════════════════════════════════════════════════════════════
# PLAYER_CACHE    = {}
# GRAPH_QUEUE     = queue.Queue()
# tracking_active = True
# last_score      = {"wickets": -1, "runs": 0, "overs": 0.0, "rr": 0.0, "partnership": 0}

# MATCH_STATE = {
#     "team1": "", "team2": "", "runs": 0, "wickets": 0, "overs": 0.0,
#     "target": 0, "run_history": [], "rr_history": [], "wicket_overs": [],
# }

# # ══════════════════════════════════════════════════════════════════════
# #  IPL PLAYER & TEAM MAPS
# # ══════════════════════════════════════════════════════════════════════
# IPL_PLAYERS = {
#     "rohit":"Rohit Sharma","hardik":"Hardik Pandya","pandya":"Hardik Pandya",
#     "bumrah":"Jasprit Bumrah","jasprit":"Jasprit Bumrah",
#     "suryakumar":"Suryakumar Yadav","sky":"Suryakumar Yadav",
#     "tilak":"Tilak Varma","varma":"Tilak Varma","boult":"Trent Boult",
#     "dhoni":"MS Dhoni","msd":"MS Dhoni","ms":"MS Dhoni",
#     "ruturaj":"Ruturaj Gaikwad","gaikwad":"Ruturaj Gaikwad",
#     "jadeja":"Ravindra Jadeja","deepak":"Deepak Chahar","chahar":"Deepak Chahar",
#     "shivam":"Shivam Dube","dube":"Shivam Dube","pathirana":"Matheesha Pathirana",
#     "virat":"Virat Kohli","kohli":"Virat Kohli","vk":"Virat Kohli",
#     "rajat":"Rajat Patidar","patidar":"Rajat Patidar",
#     "cameron":"Cameron Green","green":"Cameron Green",
#     "phil":"Phil Salt","salt":"Phil Salt","krunal":"Krunal Pandya",
#     "shreyas":"Shreyas Iyer","iyer":"Shreyas Iyer",
#     "venkatesh":"Venkatesh Iyer","narine":"Sunil Narine","sunil":"Sunil Narine",
#     "russell":"Andre Russell","andre":"Andre Russell","rinku":"Rinku Singh",
#     "varun":"Varun Chakravarthy","starc":"Mitchell Starc",
#     "angkrish":"Angkrish Raghuvanshi","rishabh":"Rishabh Pant","pant":"Rishabh Pant",
#     "jake":"Jake Fraser-McGurk","kuldeep":"Kuldeep Yadav","axar":"Axar Patel",
#     "mukesh":"Mukesh Kumar","stubbs":"Tristan Stubbs","karun":"Karun Nair",
#     "shashank":"Shashank Singh","prabhsimran":"Prabhsimran Singh",
#     "arshdeep":"Arshdeep Singh","rossouw":"Rilee Rossouw","maxwell":"Glenn Maxwell",
#     "sanju":"Sanju Samson","samson":"Sanju Samson",
#     "yashasvi":"Yashasvi Jaiswal","jaiswal":"Yashasvi Jaiswal",
#     "riyan":"Riyan Parag","parag":"Riyan Parag","jurel":"Dhruv Jurel",
#     "hetmyer":"Shimron Hetmyer","archer":"Jofra Archer",
#     "klaasen":"Heinrich Klaasen","heinrich":"Heinrich Klaasen",
#     "abhishek":"Abhishek Sharma","travis":"Travis Head","head":"Travis Head",
#     "cummins":"Pat Cummins","harshal":"Harshal Patel","shahbaz":"Shahbaz Ahmed",
#     "kl":"KL Rahul","rahul":"KL Rahul","nicholas":"Nicholas Pooran","pooran":"Nicholas Pooran",
#     "ravi":"Ravi Bishnoi","bishnoi":"Ravi Bishnoi","mohsin":"Mohsin Khan",
#     "miller":"David Miller","david":"David Miller",
#     "shubman":"Shubman Gill","gill":"Shubman Gill",
#     "sai":"Sai Sudharsan","sudharsan":"Sai Sudharsan",
#     "buttler":"Jos Buttler","jos":"Jos Buttler","rashid":"Rashid Khan",
#     "siraj":"Mohammed Siraj","mohammed":"Mohammed Siraj",
#     "umesh":"Umesh Yadav","rabada":"Kagiso Rabada","kagiso":"Kagiso Rabada",
#     "prasidh":"Prasidh Krishna","krishna":"Prasidh Krishna",
#     "prince":"Prince Yadav","ishan":"Ishan Kishan","kishan":"Ishan Kishan",
#     "sameer":"Sameer Rizvi","rizvi":"Sameer Rizvi",
#     "unadkat":"Jaydev Unadkat","jaydev":"Jaydev Unadkat",
# }

# IPL_TEAMS = {
#     "mumbai":"Mumbai Indians","mi":"Mumbai Indians",
#     "chennai":"Chennai Super Kings","csk":"Chennai Super Kings",
#     "rcb":"Royal Challengers Bengaluru","bangalore":"Royal Challengers Bengaluru",
#     "bengaluru":"Royal Challengers Bengaluru",
#     "kkr":"Kolkata Knight Riders","kolkata":"Kolkata Knight Riders",
#     "delhi":"Delhi Capitals","dc":"Delhi Capitals",
#     "punjab":"Punjab Kings","pbks":"Punjab Kings",
#     "rajasthan":"Rajasthan Royals","rr":"Rajasthan Royals",
#     "hyderabad":"Sunrisers Hyderabad","srh":"Sunrisers Hyderabad",
#     "sunrisers":"Sunrisers Hyderabad",
#     "lucknow":"Lucknow Super Giants","lsg":"Lucknow Super Giants",
#     "gujarat":"Gujarat Titans","gt":"Gujarat Titans",
# }

# VENUE_DB = {
#     "wankhede":      "High-scoring. Fast outfield. Average 185+. Dew heavily affects second innings.",
#     "eden gardens":  "Spin-friendly. Slower surface. Average 165. Home advantage for KKR.",
#     "chinnaswamy":   "Highest scoring IPL venue. Thin air. Average 190+. Batsmen's paradise.",
#     "chepauk":       "Spin-friendly. Low bounce. Average 155-165. Batsmen struggle early.",
#     "narendra modi": "Flat pitch. Largest ground. Average 170-180. Scores slightly lower.",
#     "arun jaitley":  "Batting-friendly. Some swing early. Dew factor at night.",
#     "rajiv gandhi":  "Good batting track. Scores tend to be high. Pace gets movement initially.",
#     "sawai mansingh":"Dry surface. Good for leg spinners. Average 165.",
#     "ekana":         "Balanced pitch. LSG home advantage. Average 165-175.",
# }

# def find_player(cmd: str) -> str | None:
#     cmd = cmd.lower()
#     for k, v in IPL_PLAYERS.items():
#         if k in cmd: return v
#     return None

# def find_teams(cmd: str) -> list:
#     cmd, found = cmd.lower(), []
#     for k, v in IPL_TEAMS.items():
#         if k in cmd and v not in found: found.append(v)
#     return found


# # ══════════════════════════════════════════════════════════════════════
# #  INTELLIGENT ANALYSIS
# # ══════════════════════════════════════════════════════════════════════
# def analyze_situation(runs, wickets, overs, target=0) -> str:
#     """Pure logic analysis — no search, no duplicates."""
#     balls_done = int(overs) * 6 + round((overs % 1) * 10)
#     balls_left = max(1, 120 - balls_done)
#     curr_rr    = round(runs / overs, 2) if overs > 0 else 0
#     insights   = []

#     if target > 0:
#         runs_needed = max(1, target - runs)
#         req_rr      = round(runs_needed / balls_left * 6, 2)
#         gap         = curr_rr - req_rr
#         if gap > 1:
#             insights.append("Batting team comfortably ahead of required rate.")
#         elif gap > -1:
#             insights.append(f"Close contest. Required rate {req_rr} vs current {curr_rr}.")
#         elif gap > -3:
#             insights.append(f"Tough chase. Required rate {req_rr} well above current {curr_rr}.")
#         else:
#             insights.append(f"Very difficult. Need {runs_needed} from {balls_left} balls at {req_rr}.")
#         if wickets >= 7:
#             insights.append("Tail exposed. Every run precious.")
#         elif wickets <= 2 and balls_left > 30:
#             insights.append("Plenty of wickets in hand to accelerate.")
#     else:
#         remaining  = max(1, 20 - overs)
#         wkt_factor = max(0.55, 1 - wickets * 0.06)
#         proj       = int(round(runs + curr_rr * remaining * wkt_factor))
#         if overs < 6:
#             insights.append(f"Powerplay. Projected total {proj} if form holds.")
#         elif overs < 15:
#             if wickets <= 3:
#                 insights.append(f"Solid platform. Projected {proj}. Wickets in hand to push.")
#             elif wickets <= 5:
#                 insights.append(f"Middle overs squeeze. Projected {proj}. Partnership critical.")
#             else:
#                 insights.append(f"Wickets tumbling. Projected {proj}. Must rebuild urgently.")
#         else:
#             insights.append(f"Death overs. Final surge needed. Projected {proj}.")
#     return ". ".join(insights)


# # ══════════════════════════════════════════════════════════════════════
# #  PLAYER FULL ANALYSIS (ML + LLM)
# # ══════════════════════════════════════════════════════════════════════
# def get_full_player_analysis(player: str, bowling: bool = False) -> str:
#     """The real agent experience — fresh data + ML + LLM."""
#     print(f"  [Agent] Scanning IPL 2026 database for {player}...")

#     raw = get_player_raw_data(player)

#     if bowling:
#         wickets   = raw.get("wickets", [])
#         economies = raw.get("economies", [])

#         if not wickets and raw.get("raw_text"):
#             wickets, economies = extract_wickets_from_text(raw["raw_text"])

#         if len(wickets) >= 3:
#             ml = predict_future_wickets(wickets, economies)
#             PLAYER_CACHE[player.lower()] = {"wickets": wickets, "economies": economies, "ml": ml}

#             expert = get_expert_analysis(player, wickets, ml.get("predicted", 0), bowling=True)

#             return (f"Sir, {player} IPL 2026 bowling analysis — "
#                     f"Recent wickets: {wickets[:5]}. "
#                     f"Average {ml['average']} per match. Economy {raw.get('economy','N/A')}. "
#                     f"ML predicts {ml['predicted']} wickets next match (trend: {ml['trend']}, "
#                     f"{ml['confidence']} confidence). "
#                     f"Expert assessment: {expert}")
#         else:
#             sents = best_sentences(search(f"{player} IPL 2026 bowling stats", mode="text", n=5),
#                                    ["wicket", "economy", "bowling", "figures"])
#             base = f"Sir, {player} bowling: " + ". ".join(sents) if sents else f"Sir, {player} bowling data insufficient."
#             expert = get_expert_analysis(player, [], 0, bowling=True)
#             return base + f" Expert note: {expert}"
#     else:
#         scores = raw.get("scores", [])

#         if not scores and raw.get("raw_text"):
#             scores = extract_scores_from_text(raw["raw_text"])

#         if len(scores) >= 3:
#             ml = predict_future_score(scores)
#             PLAYER_CACHE[player.lower()] = {"runs": scores, "ml": ml}

#             expert = get_expert_analysis(player, scores, ml.get("predicted", 0))

#             career = (f"Career: {raw['career_runs']} runs in {raw['career_matches']} matches. "
#                       if raw.get("career_runs") else "")

#             return (f"Sir, {player} IPL 2026 batting analysis — "
#                     f"{career}"
#                     f"Recent innings: {scores[:6]}. "
#                     f"Current average {ml['average']}. Strike rate {raw.get('strike_rate','N/A')}. "
#                     f"Peak {ml['peak']}, Floor {ml['floor']}. "
#                     f"ML predicts {ml['predicted']} runs next match "
#                     f"(trend: {ml['trend']}, {ml['confidence']} confidence). "
#                     f"Expert assessment: {expert}")
#         else:
#             sents = best_sentences(search(f"{player} IPL 2026 batting stats runs", mode="text", n=5),
#                                    ["run", "score", "average", "strike", "innings"])
#             base = f"Sir, {player}: " + ". ".join(sents) if sents else f"Sir, {player} batting data insufficient."
#             expert = get_expert_analysis(player, [], 0)
#             return base + f" Expert note: {expert}"


# # ══════════════════════════════════════════════════════════════════════
# #  FULL MATCH SITUATION
# # ══════════════════════════════════════════════════════════════════════
# def get_full_match_situation() -> str:
#     d     = get_live_scorecard()
#     match = get_today_match()

#     if not d and not match:
#         return "Sir, no live match data available right now."
#     if not d:
#         return f"Sir, today's match is {match}. Live score not yet available."

#     runs    = d.get("runs", 0)
#     wickets = d.get("wickets", 0)
#     overs   = d.get("overs", 0.0)
#     rr      = d.get("run_rate", 0.0)
#     target  = d.get("target", 0)
#     req_rr  = d.get("req_rate", 0.0)
#     needed  = d.get("runs_needed", 0) or max(0, target - runs)
#     balls   = d.get("balls_left", 0)
#     part    = d.get("partnership", 0)
#     t1      = d.get("team1", MATCH_STATE.get("team1", "")) or "batting team"

#     # Win probability
#     wp = calculate_win_probability(runs, wickets, overs, target)

#     if target:
#         msg = (f"Sir, {t1} chasing {target}. "
#                f"Score: {runs} for {wickets} in {overs} overs. "
#                f"Need {needed} runs")
#         if balls: msg += f" from {balls} balls"
#         msg += f". Run rate {rr}"
#         if req_rr: msg += f", required {req_rr}"
#         msg += f". Win probability {wp.get('win_percent')}%."
#         if part: msg += f" Partnership {part}."
#     else:
#         proj = wp.get("projected", int(rr * 20) if rr else 0)
#         msg  = (f"Sir, {t1}: {runs} for {wickets} in {overs} overs. "
#                 f"Run rate {rr}. Projected {proj}.")
#         if part: msg += f" Partnership {part}."

#     # LLM insight
#     score_data = {**d, "win_percent": wp.get("win_percent", 50)}
#     insight    = get_match_insight(match or "IPL 2026", score_data)
#     if insight:
#         msg += f" {insight}"
#     else:
#         msg += f" {analyze_situation(runs, wickets, overs, target)}"

#     # Update MATCH_STATE
#     MATCH_STATE.update(
#         runs=runs, wickets=wickets, overs=overs, target=target,
#         team1=d.get("team1", MATCH_STATE["team1"]),
#         team2=d.get("team2", MATCH_STATE["team2"]),
#     )
#     rh = MATCH_STATE["run_history"]
#     if not rh or rh[-1] != runs:
#         rh.append(runs)
#         if rr: MATCH_STATE["rr_history"].append(rr)

#     return msg.strip()


# # ══════════════════════════════════════════════════════════════════════
# #  FANTASY TEAM
# # ══════════════════════════════════════════════════════════════════════
# def get_fantasy_team() -> str:
#     match = get_today_match()
#     if not match: return "Sir, today's match not found."
#     res   = search(f"{match} IPL 2026 fantasy team best XI captain picks today", mode="text", n=8)
#     sents = best_sentences(res, ["captain", "must pick", "differential", "fantasy", "key pick", "vice"])
#     players_found = []
#     txt = all_text(res)
#     for k, v in IPL_PLAYERS.items():
#         if k in txt.lower() and v not in players_found: players_found.append(v)
#         if len(players_found) >= 8: break
#     insight = get_fantasy_insight(match, players_found)
#     if sents:
#         return f"Sir, fantasy for {match}: " + ". ".join(sents[:2]) + f" {insight}"
#     return insight


# # ══════════════════════════════════════════════════════════════════════
# #  PITCH + WEATHER
# # ══════════════════════════════════════════════════════════════════════
# def get_pitch_report() -> str:
#     from scraper import TEAM_VENUE, TEAM_CITY
#     match   = get_today_match() or "IPL 2026"
#     match_l = match.lower()

#     # 1. Team-based venue lookup (most reliable)
#     venue = None
#     for team_key, team_venue in TEAM_VENUE.items():
#         if team_key.lower().split()[-1].lower() in match_l or team_key.lower().split()[0].lower() in match_l:
#             venue = team_venue
#             break

#     # 2. Try venue DB
#     for key, info in VENUE_DB.items():
#         if key in match_l or (venue and key in venue.lower()):
#             llm_add = get_pitch_insight(venue or key, info)
#             return f"Sir, {venue or key} pitch: {info} {llm_add}"

#     # 3. Search for pitch info
#     res = search(f"{match} IPL 2026 pitch report surface today venue", mode="news", days="d", n=8)
#     txt = all_text(res)

#     # Check venue DB against search text too
#     for key, info in VENUE_DB.items():
#         if key in txt.lower():
#             return f"Sir, {key.title()} pitch: {info}"

#     sents = best_sentences(res, ["pitch","surface","batting","spin","pace","bounce","flat","dew"])
#     if sents:
#         llm_add = get_pitch_insight(venue or match, " ".join(sents))
#         return "Sir, pitch report: " + ". ".join(sents[:2]) + f" {llm_add}"
#     return f"Sir, {match} pitch: Expected good batting surface. Spinners may assist in later overs."

# def get_weather() -> str:
#     from scraper import TEAM_CITY
#     match = get_today_match() or "IPL 2026"

#     # 1. Try from match title - team-based city lookup
#     city = None
#     match_l = match.lower()
#     for team_key, team_city in TEAM_CITY.items():
#         if team_key in match_l:
#             city = team_city
#             break

#     # 2. Fallback: search for city
#     if not city:
#         cities = ["Mumbai","Chennai","Kolkata","Delhi","Bengaluru","Bangalore",
#                   "Hyderabad","Ahmedabad","Jaipur","Lucknow","Mohali","Pune","Dharamsala","Guwahati"]
#         vtxt   = all_text(search(f"{match} IPL 2026 venue city today", mode="news", days="d", n=5))
#         city   = next((c for c in cities if c.lower() in vtxt.lower()), "Mumbai")

#     res   = search(f"{city} weather today cricket match IPL 2026 rain dew temperature", mode="news", days="d", n=6)
#     sents = best_sentences(res, ["weather","rain","temperature","dew","humid","clear","forecast","cloud"])
#     # Filter: must mention today's city
#     valid = [s for s in sents if city.lower() in s.lower() or "today" in s.lower() or "match" in s.lower()]
#     if valid:
#         return f"Sir, {city} weather: " + ". ".join(valid[:2])
#     if sents:
#         return f"Sir, {city} weather: " + sents[0]
#     return f"Sir, {city}: Clear skies expected. Dew factor likely in second innings. Humidity moderate."

# def get_toss_analysis() -> str:
#     toss = get_toss()
#     if not toss: return "Sir, toss not announced yet."
#     pitch   = get_pitch_report()
#     weather = get_weather()
#     return get_toss_insight(toss, pitch, weather)


# # ══════════════════════════════════════════════════════════════════════
# #  H2H + BOWLERS AGAINST
# # ══════════════════════════════════════════════════════════════════════
# def get_h2h(t1: str, t2: str) -> str:
#     res    = search(f"{t1} vs {t2} IPL head to head record wins history", mode="text", n=6)
#     sents  = best_sentences(res, ["won", "win", "head", "record", "beat", "times"])
#     h2h_str = ". ".join(sents[:2]) if sents else "limited head to head data"
#     return get_h2h_insight(t1, t2, h2h_str)

# def get_bowlers_against(batsman: str) -> str:
#     first = batsman.split()[0]
#     res   = search(f"bowler dismissed {batsman} most times IPL history", mode="text", n=8)
#     txt   = all_text(res)
#     bowlers = []
#     for bname in re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has|have|holds|is)', txt):
#         if bname.lower() not in batsman.lower() and len(bname) > 5: bowlers.append(bname)
#     sents  = best_sentences(res, ["dismiss", "wicket", "out", "bowler"])
#     result = ""
#     if bowlers:
#         uniq   = list(dict.fromkeys(bowlers))[:3]
#         result += f"Sir, {batsman} ka kryptonite: {', '.join(uniq)}. "
#     if sents:
#         result += ". ".join(sents[:2])
#     if result:
#         expert = get_expert_analysis(batsman, [], 0)
#         return result + f" Expert note: {expert}"
#     return f"Sir, {batsman} ke against bowler matchup data nahi mila."


# # ══════════════════════════════════════════════════════════════════════
# #  MISC FEATURES
# # ══════════════════════════════════════════════════════════════════════
# def get_player_form(player: str) -> str:
#     raw    = get_player_raw_data(player)
#     scores = raw.get("scores", [])[:5]
#     if len(scores) >= 3:
#         ml     = predict_future_score(scores)
#         expert = get_expert_analysis(player, scores, ml.get("predicted", 0))
#         return (f"Sir, {player} recent form: Last {len(scores)} innings {scores}. "
#                 f"Average {ml['average']}. Trend {ml['trend']}. "
#                 f"ML predicts {ml['predicted']} next match. {expert}")
#     # Fallback: news search (cleaner than text)
#     sents = best_sentences(
#         search(f"{player} IPL 2026 form recent innings runs match", mode="news", days="w", n=8),
#         ["form","performing","innings","run","consistent","scored","hit"])
#     return ("Sir, " + player + " form: " + ". ".join(sents[:2]) if sents
#             else f"Sir, {player} ka recent form data nahi mila.")

# def get_ipl_records() -> str:
#     res   = search("IPL 2026 records highest score most sixes fastest fifty century", mode="text", n=6)
#     sents = best_sentences(res, ["record","highest","most","fastest","century","six","fifty"])
#     return ("Sir, IPL 2026 records: " + ". ".join(sents[:3])
#             if sents else "Sir, IPL 2026 records not available.")

# def get_auction_value(player: str) -> str:
#     res  = search(f"{player} IPL 2026 auction price crore salary bid", mode="text", n=6)
#     txt  = all_text(res)
#     m    = re.search(r'(\d+(?:\.\d+)?)\s*(?:crore|cr)\b', txt, re.IGNORECASE)
#     if m:
#         return f"Sir, {player} IPL auction value: {m.group(1)} crore."
#     sents = best_sentences(res, ["crore","auction","price","sold","bid"])
#     return f"Sir, {sents[0]}" if sents else f"Sir, {player} auction data not found."

# def get_team_strength(team: str) -> str:
#     res   = search(f"{team} IPL 2026 squad analysis strength weakness", mode="text", n=6)
#     t0    = team.split()[0].lower()
#     parts = []
#     for r in res:
#         for line in re.split(r'[.\n]', r.get("body", "")):
#             line = line.strip()
#             if is_junk(line) or not (20 < len(line) < 200): continue
#             if t0 in line.lower():
#                 if any(w in line.lower() for w in ["strong","weak","key","squad","batting","bowling","form","balance"]):
#                     cl = clean(line)
#                     if cl and cl not in parts: parts.append(cl)
#             if len(parts) >= 3: break
#         if len(parts) >= 3: break
#     if parts:
#         return f"Sir, {team}: " + ". ".join(parts[:3])
#     return f"Sir, {team}: Balanced squad. Check injury news before finalizing picks."

# def get_player_milestone(player: str) -> str:
#     res   = search(f"{player} IPL 2026 milestone record close runs wickets", mode="text", n=6)
#     sents = best_sentences(res, ["milestone","record","close","away","needs","require","century"])
#     return ("Sir, " + ". ".join(sents[:2]) if sents
#             else f"Sir, {player} milestone data not found. Check career stats.")

# def get_batting_scorecard() -> str:
#     match  = get_today_match() or "IPL 2026"
#     res    = search(f"{match} IPL 2026 live batting at crease runs balls today", mode="news", days="d", n=8)
#     sents  = best_sentences(res, ["batting","batsman","runs off","not out","at crease","opening"])
#     kw     = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
#     valid  = [s for s in sents if kw in s.lower() or "batting" in s.lower()]
#     if valid: return "Sir, batting update: " + ". ".join(valid[:2])
#     d = get_live_scorecard()
#     return (f"Sir, batting: {d.get('runs')}/{d.get('wickets')} in {d.get('overs')} overs."
#             if d else "Sir, batting scorecard not in live feed.")

# def get_bowling_scorecard() -> str:
#     match  = get_today_match() or "IPL 2026"
#     res    = search(f"{match} IPL 2026 live bowling figures economy today", mode="news", days="d", n=8)
#     sents  = best_sentences(res, ["bowling","bowler","figures","economy","spell","wickets"])
#     kw     = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
#     valid  = [s for s in sents if kw in s.lower() or "bowl" in s.lower()]
#     return ("Sir, bowling update: " + ". ".join(valid[:2]) if valid
#             else "Sir, bowling scorecard not in live feed right now.")



# # ══════════════════════════════════════════════════════════════════════
# #  NEW: LIVE OVER-BY-OVER TRACKER
# # ══════════════════════════════════════════════════════════════════════
# def get_over_by_over() -> str:
#     match = get_today_match() or "IPL 2026"
#     res   = search(f"{match} IPL 2026 live over by over update runs wickets", mode="news", days="d", n=8)
#     sents = best_sentences(res, ["over","wicket","boundary","six","four","dot","last over","this over","maiden"])
#     kw    = match.replace(" vs "," ").split()[0].lower() if match else "ipl"
#     valid = [s for s in sents if kw in s.lower() or "over" in s.lower()]
#     if valid: return "Sir, over-by-over: " + ". ".join(valid[:3])
#     d = get_live_scorecard()
#     if d: return f"Sir, {d.get('runs')}/{d.get('wickets')} in {d.get('overs')} overs. Run rate {d.get('run_rate')}."
#     return "Sir, over tracker not available right now."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: MATCH MOMENTUM (did batting team gain or lose momentum?)
# # ══════════════════════════════════════════════════════════════════════
# def get_match_momentum() -> str:
#     d = get_live_scorecard()
#     if not d or not d.get("runs"): return "Sir, no live match data."
#     rh = MATCH_STATE.get("run_history", [])
#     if len(rh) >= 3:
#         recent_rrs = []
#         for i in range(max(0,len(rh)-3), len(rh)):
#             if i > 0 and rh[i] > rh[i-1]:
#                 recent_rrs.append(rh[i] - rh[i-1])
#         if recent_rrs:
#             avg_recent = sum(recent_rrs) / len(recent_rrs)
#             overall_rr = d.get("run_rate", 0)
#             if avg_recent > overall_rr + 1:
#                 momentum = "batting team has momentum. Run rate picking up."
#             elif avg_recent < overall_rr - 1:
#                 momentum = "bowling team has momentum. Batting team slowing down."
#             else:
#                 momentum = "match is evenly poised. No team has clear momentum."
#             return f"Sir, current momentum: {momentum} Last few overs averaging {round(avg_recent,1)} per over."
#     return get_full_match_situation()

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: TOP 5 PERFORMERS TODAY
# # ══════════════════════════════════════════════════════════════════════
# def get_top_performers() -> str:
#     match = get_today_match() or "IPL 2026"
#     res   = search(f"{match} IPL 2026 top performers today runs wickets standout", mode="news", days="d", n=8)
#     sents = best_sentences(res, ["scored","took","wicket","century","fifty","hit","smashed","bowling spell"])
#     kw    = match.replace(" vs "," ").split()[0].lower() if match else "ipl"
#     valid = [s for s in sents if kw in s.lower() or any(w in s.lower() for w in ["scored","wicket","took","hit"])]
#     if valid: return "Sir, top performers today: " + ". ".join(valid[:4])
#     return "Sir, top performers data not in live feed yet."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: SMART MATCH SUMMARY (end of innings/match)
# # ══════════════════════════════════════════════════════════════════════
# def get_match_summary() -> str:
#     match = get_today_match() or "IPL 2026"
#     res   = search(f"{match} IPL 2026 match summary innings result highlights today", mode="news", days="d", n=8)
#     sents = best_sentences(res, ["innings","result","won","beat","total","scored","chased","defended"])
#     kw    = match.replace(" vs "," ").split()[0].lower() if match else "ipl"
#     valid = [s for s in sents if kw in s.lower() or any(w in s.lower() for w in ["won","total","innings","result"])]
#     if valid: return "Sir, match summary: " + ". ".join(valid[:3])
#     d = get_live_scorecard()
#     if d: return get_full_match_situation()
#     return "Sir, match summary not available yet."

# # ══════════════════════════════════════════════════════════════════════
# #  NEW: PLAYER VS PLAYER HEAD TO HEAD (batsman vs bowler)
# # ══════════════════════════════════════════════════════════════════════
# def get_player_vs_player(batter: str, bowler: str) -> str:
#     res   = search(f"{batter} vs {bowler} IPL T20 record dismissals stats matchup", mode="text", n=6)
#     sents = best_sentences(res, ["dismiss","wicket","out","balls","runs","average","face","times"])
#     if sents:
#         expert = get_expert_analysis(f"{batter} vs {bowler}", [], 0)
#         return f"Sir, {batter} vs {bowler}: " + ". ".join(sents[:2]) + f" {expert}"
#     return f"Sir, {batter} vs {bowler} specific record not found. Check bowler analysis for broader data."

# # ══════════════════════════════════════════════════════════════════════
# #  SENTINEL - background alerts
# # ══════════════════════════════════════════════════════════════════════
# def sentinel(speaker):
#     global last_score
#     pythoncom.CoInitialize()
#     while tracking_active:
#         try:
#             d = get_live_scorecard()
#             if d:
#                 runs    = d.get("runs", 0)
#                 wickets = d.get("wickets", 0)
#                 overs   = d.get("overs", 0.0)
#                 rr      = d.get("run_rate", 0.0)
#                 part    = d.get("partnership", 0)

#                 if wickets > last_score['wickets'] >= 0:
#                     ov_str = f"in {overs} overs" if overs > 0 else ""
#                     msg    = f"Sir, wicket has fallen. Score {runs} for {wickets} {ov_str}."
#                     msg   += f" {analyze_situation(runs, wickets, overs, d.get('target', 0))}"
#                     print(f"\n*** WICKET ALERT: {msg}")
#                     speaker.Speak(msg)
#                     if wickets not in MATCH_STATE["wicket_overs"]:
#                         MATCH_STATE["wicket_overs"].append(int(overs))

#                 if last_score['runs'] > 0:
#                     if runs // 50 > last_score['runs'] // 50:
#                         speaker.Speak(f"Sir, batting team crossed {(runs // 50) * 50} runs.")
#                     if part >= 100 and last_score.get("partnership", 0) < 100:
#                         speaker.Speak("Sir, century partnership. Outstanding batting.")
#                     if rr > 12 and last_score.get("rr", 0) <= 12:
#                         speaker.Speak(f"Sir, exceptional run rate {rr} right now.")

#                 last_score.update(runs=runs, wickets=wickets, overs=overs, rr=rr, partnership=part)
#         except Exception as e:
#             print(f"[Sentinel] {e}")
#         time.sleep(60)


# # ══════════════════════════════════════════════════════════════════════
# #  MAIN VOICE LOOP
# # ══════════════════════════════════════════════════════════════════════
# def jarvis_loop(speaker):
#     pythoncom.CoInitialize()

#     def speak(text: str):
#         print(f"\nJarvis: {text}\n")
#         speaker.Speak(text)

#     def listen_once(timeout: int = 8) -> str:
#         with sr.Microphone() as src:
#             rec.adjust_for_ambient_noise(src, duration=0.3)
#             audio = rec.listen(src, timeout=timeout, phrase_time_limit=8)
#         return rec.recognize_google(audio, language="en-IN").strip()

#     threading.Thread(target=sentinel, args=(speaker,), daemon=True).start()
#     rec = sr.Recognizer()
#     rec.dynamic_energy_threshold = True

#     llm_st = check_llm_status()
#     speak(f"Jarvis online, sir. IPL 2026 agent ready. {llm_st}. How can I assist you?")

#     while True:
#         try:
#             with sr.Microphone() as src:
#                 print("[Listening]")
#                 rec.adjust_for_ambient_noise(src, duration=0.5)
#                 audio = rec.listen(src, timeout=10, phrase_time_limit=10)
#             print("[Recognizing]")
#             cmd = rec.recognize_google(audio, language="en-IN").lower().strip()
#             print(f"You said: '{cmd}'")

#             # ── WAKE ──────────────────────────────────────────────
#             if cmd.strip() in ["jarvis", "hey jarvis"]:
#                 speak("Yes sir, ready.")

#             # ── TODAY MATCH ───────────────────────────────────────
#             elif any(w in cmd for w in ["today match","aaj ka match","kiska match",
#                                          "kaun khel","ipl today","which match","aaj kaun"]):
#                 speak("Checking today's match sir...")
#                 ans = get_today_match()
#                 speak(f"Sir, today's match: {ans}. Want the live score?" if ans
#                       else "Sir, today's match not found.")

#             # ── FULL SITUATION (ML + LLM) ─────────────────────────
#             elif any(w in cmd for w in ["situation","match situation","full update","poori update",
#                                          "full status","kya ho raha","complete update","what's happening"]):
#                 speak("Analyzing match situation sir...")
#                 speak(get_full_match_situation())

#             # ── LIVE SCORE ────────────────────────────────────────
#             elif any(w in cmd for w in ["score","kya hua","kitne run","live","status","update","kya score"]) and "highest" not in cmd:
#                 speak("Fetching fresh score sir...")
#                 d = get_live_scorecard()
#                 if d:
#                     msg = (f"Sir, {d.get('runs','?')} for {d.get('wickets','?')} "
#                            f"in {d.get('overs','?')} overs. Run rate {d.get('run_rate','?')}.")
#                     msg += f" {analyze_situation(d['runs'], d.get('wickets',0), d['overs'], d.get('target',0))}"
#                     speak(msg)
#                 else:
#                     ans = get_today_match()
#                     speak(f"Sir, live score not available. Today: {ans}." if ans
#                           else "Sir, no live match right now.")

#             # ── RUN RATE ──────────────────────────────────────────
#             elif any(w in cmd for w in ["run rate","required rate","rrr","current rate","kitna rate","crr"]):
#                 d = get_live_scorecard()
#                 if d:
#                     msg = f"Sir, current run rate {d.get('run_rate','?')}."
#                     if d.get("req_rate"):   msg += f" Required {d['req_rate']}."
#                     if d.get("balls_left"): msg += f" {d['balls_left']} balls left."
#                     speak(msg)
#                 else:
#                     speak("Sir, no live match data.")

#             # ── PLAYER ANALYSIS (ML + LLM) ────────────────────────
#             elif any(w in cmd for w in ["analyze","analysis","deep analysis","full analysis",
#                                          "ml analysis","expert analysis","poora analysis"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 bowling = any(w in cmd for w in ["bowl","wicket","bowling"])
#                 speak(f"Running ML and LLM analysis for {player} sir. One moment...")
#                 speak(get_full_player_analysis(player, bowling=bowling))

#             # ── PLAYER STATS ──────────────────────────────────────
#             elif any(w in cmd for w in ["stats","performance","kaisa khelta","batting stats","runs banaye","innings"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Fetching {player} stats sir...")
#                 speak(get_full_player_analysis(player))

#             # ── BOWLING STATS ─────────────────────────────────────
#             elif any(w in cmd for w in ["bowling stats","bowling record","kitne wicket","bowling figures","economy"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which bowler sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Fetching {player} bowling sir...")
#                 speak(get_full_player_analysis(player, bowling=True))

#             # ── PLAYER FORM ───────────────────────────────────────
#             elif any(w in cmd for w in ["form","recent form","last 5","kaise chal raha","current form","in form"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Analyzing {player} recent form sir...")
#                 speak(get_player_form(player))

#             # ── WIN PREDICTION ────────────────────────────────────
#             elif any(w in cmd for w in ["predict","kaun jeetega","win","chance","jeetne","winner",
#                                          "win probability","who will win","prediction"]):
#                 d = get_live_scorecard()
#                 if d and d.get("runs"):
#                     wp  = calculate_win_probability(d['runs'], d.get('wickets',0),
#                                                      d.get('overs',1), d.get('target',185))
#                     msg = f"Sir, win probability: {wp.get('win_percent')}% for batting team. "
#                     msg += analyze_situation(d['runs'], d.get('wickets',0),
#                                               d.get('overs',1), d.get('target',0))
#                     expert = get_match_insight(get_today_match() or "IPL 2026",
#                                                {**d, "win_percent": wp.get("win_percent", 50)})
#                     if expert: msg += f" {expert}"
#                     speak(msg)
#                 else:
#                     speak("Which player sir? Batting or bowling?")
#                     try:
#                         pc = listen_once().lower()
#                         pl = find_player(pc) or pc.strip().title()
#                         if "bowl" in pc or "wicket" in pc:
#                             r  = get_full_player_analysis(pl, bowling=True)
#                         else:
#                             r  = get_full_player_analysis(pl)
#                         speak(r)
#                     except:
#                         speak("Sir, prediction needs live match data.")

#             # ── SCHEDULE ──────────────────────────────────────────
#             elif any(w in cmd for w in ["next match","agle match","tomorrow","kal ka","upcoming"]):
#                 speak("Checking tomorrow's fixture sir...")
#                 speak(get_schedule("tomorrow"))

#             elif any(w in cmd for w in ["last match","yesterday","kal hua","pichle","previous match"]):
#                 speak("Checking yesterday's result sir...")
#                 speak(get_schedule("yesterday"))

#             elif any(w in cmd for w in ["schedule","fixture","kab hai","aaj ka schedule"]):
#                 speak("Checking today's schedule sir...")
#                 speak(get_schedule("today"))

#             # ── POINTS TABLE ──────────────────────────────────────
#             elif any(w in cmd for w in ["points table","standings","ranking","kaun upar","table","leaderboard","playoff"]):
#                 speak("Fetching IPL standings sir...")
#                 speak(get_points_table())

#             # ── ORANGE / PURPLE CAP ───────────────────────────────
#             elif any(w in cmd for w in ["orange cap","top scorer","most runs","leading batsman"]):
#                 speak("Checking orange cap sir...")
#                 speak(get_orange_cap())

#             elif any(w in cmd for w in ["purple cap","most wickets","leading bowler","top bowler"]):
#                 speak("Checking purple cap sir...")
#                 speak(get_purple_cap())

#             # ── PITCH ─────────────────────────────────────────────
#             elif any(w in cmd for w in ["pitch","pitch report","surface","ground report"]):
#                 speak("Fetching pitch report sir...")
#                 speak(get_pitch_report())

#             # ── WEATHER ───────────────────────────────────────────
#             elif any(w in cmd for w in ["weather","rain","mausam","barish","temperature","dew","forecast"]):
#                 speak("Checking weather conditions sir...")
#                 speak(get_weather())

#             # ── TOSS ANALYSIS ─────────────────────────────────────
#             elif any(w in cmd for w in ["toss","toss analysis","toss decision","why bat","why field"]):
#                 speak("Analyzing toss sir...")
#                 speak(get_toss_analysis())

#             # ── PLAYING 11 ────────────────────────────────────────
#             elif any(w in cmd for w in ["playing 11","playing eleven","squad","eleven","starting xi"]):
#                 speak("Checking playing eleven sir...")
#                 p11 = get_playing11()
#                 speak(p11 if p11 else "Sir, playing eleven not announced yet.")

#             # ── INJURY ────────────────────────────────────────────
#             elif any(w in cmd for w in ["injury","injured","fit","fitness","ruled out","unavailable","kaun fit"]):
#                 teams = find_teams(cmd)
#                 speak("Checking injury updates sir...")
#                 speak(get_injury_news(teams[0] if teams else None))

#             # ── NEWS ──────────────────────────────────────────────
#             elif any(w in cmd for w in ["news","latest","highlights","headlines","kya hua aaj","updates","breaking"]):
#                 speak("Fetching latest IPL news sir...")
#                 speak(get_ipl_news())

#             # ── FANTASY ───────────────────────────────────────────
#             elif any(w in cmd for w in ["fantasy","dream11","best 11","fantasy team","who to pick","best pick"]):
#                 speak("Analyzing fantasy picks with LLM sir...")
#                 speak(get_fantasy_team())

#             # ── AUCTION VALUE ─────────────────────────────────────
#             elif any(w in cmd for w in ["auction","price","value","crore","kitne mein","salary","worth"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(get_auction_value(player))

#             # ── TEAM STRENGTH ─────────────────────────────────────
#             elif any(w in cmd for w in ["team strength","squad analysis","team form","team analysis","kaisi team"]):
#                 teams = find_teams(cmd)
#                 if teams:
#                     speak(f"Analyzing {teams[0]} sir...")
#                     speak(get_team_strength(teams[0]))
#                 else:
#                     speak("Which team sir?")
#                     try:
#                         tc = listen_once()
#                         t  = find_teams(tc)
#                         speak(get_team_strength(t[0]) if t else "Team not found sir.")
#                     except: continue

#             # ── COMPARE ───────────────────────────────────────────
#             elif any(w in cmd for w in ["compare","versus","better","mukabla","kaun behtar"]):
#                 plist = []
#                 for k, v in IPL_PLAYERS.items():
#                     if k in cmd and v not in plist: plist.append(v)
#                 if len(plist) >= 2:
#                     p1, p2 = plist[0], plist[1]
#                 else:
#                     speak("Two players please sir, with 'and' in between.")
#                     try:
#                         said = listen_once()
#                         if " and " in said.lower():
#                             pts = said.lower().split(" and ")
#                             p1  = find_player(pts[0]) or pts[0].strip().title()
#                             p2  = find_player(pts[1]) or pts[1].strip().title()
#                         else:
#                             speak("Use 'and' between names sir."); continue
#                     except: continue
#                 speak(f"Comparing {p1} and {p2} sir...")
#                 s1 = get_full_player_analysis(p1)
#                 s2 = get_full_player_analysis(p2)
#                 speak(f"{s1} Now for {p2}: {s2}")

#             # ── HEAD TO HEAD ──────────────────────────────────────
#             elif any(w in cmd for w in ["head to head","h2h","history between"]):
#                 teams = find_teams(cmd)
#                 if len(teams) >= 2:
#                     speak(f"Checking {teams[0]} vs {teams[1]} with LLM analysis sir...")
#                     speak(get_h2h(teams[0], teams[1]))
#                 else:
#                     speak("Sir, name two teams. Example: MI vs CSK head to head.")

#             # ── BOWLERS AGAINST ───────────────────────────────────
#             elif any(w in cmd for w in ["kaun out karega","weakness","kamzori","kaun out kar",
#                                          "dismiss","out kar sakta","nemesis","bowler against"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which batsman sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Analyzing threats against {player} sir...")
#                 speak(get_bowlers_against(player))

#             # ── MILESTONE ─────────────────────────────────────────
#             elif any(w in cmd for w in ["milestone","record close","kitne runs chahiye","approaching record"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(get_player_milestone(player))

#             # ── BATTING SCORECARD ─────────────────────────────────
#             elif any(w in cmd for w in ["who is batting","batting scorecard","at crease","kaun batting"]):
#                 speak("Checking batting sir...")
#                 speak(get_batting_scorecard())

#             # ── BOWLING SCORECARD ─────────────────────────────────
#             elif any(w in cmd for w in ["who is bowling","bowling scorecard","current bowler","kaun bowling"]):
#                 speak("Checking bowling sir...")
#                 speak(get_bowling_scorecard())

#             # ── IPL RECORDS ───────────────────────────────────────
#             elif any(w in cmd for w in ["ipl records","highest score","most sixes","fastest fifty","century record","season record"]):
#                 speak("Fetching IPL 2026 records sir...")
#                 speak(get_ipl_records())

#             # ── GRAPHS (main thread via queue) ────────────────────
#             elif any(w in cmd for w in ["momentum","dashboard","analytics","match graph","full graph"]):
#                 speak("Generating ML analytics dashboard sir...")
#                 GRAPH_QUEUE.put(("momentum", None))

#             elif any(w in cmd for w in ["batting graph","run graph","batting chart"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which batsman sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Generating {player} ML batting graph sir...")
#                 GRAPH_QUEUE.put(("batting", player))

#             elif any(w in cmd for w in ["bowling graph","wicket graph","bowling chart"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which bowler sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak(f"Generating {player} ML bowling graph sir...")
#                 GRAPH_QUEUE.put(("bowling", player))

#             elif any(w in cmd for w in ["graph","chart","dikhao"]):
#                 player = find_player(cmd)
#                 if not player:
#                     speak("Which player sir?")
#                     try: player = find_player(listen_once()) or listen_once().strip().title()
#                     except: continue
#                 speak("Batting or bowling graph sir?")
#                 try:
#                     gt = listen_once().lower()
#                     GRAPH_QUEUE.put(("batting" if any(w in gt for w in ["bat","run"]) else "bowling", player))
#                 except:
#                     GRAPH_QUEUE.put(("batting", player))

#             # ── HELP ──────────────────────────────────────────────
#             elif any(w in cmd for w in ["help","kya kar sakta","features","commands","what can you do"]):
#                 speak("Sir, I am your IPL 2026 intelligence agent with ML and LLM brain. "
#                       "Commands: Score. Match situation. Run rate. Today match. Batting scorecard. "
#                       "Bowling scorecard. Toss analysis. Pitch report. Weather. "
#                       "Schedule, next match, last match. Points table. Orange cap. Purple cap. "
#                       "Virat analysis — full ML plus LLM expert insight. "
#                       "Virat form. Virat milestone. Compare Virat and Rohit. "
#                       "Win prediction. Fantasy team. Auction price. Team strength. "
#                       "MI vs CSK head to head. Virat ko kaun out kar sakta. "
#                       "Batting graph. Bowling graph. Momentum dashboard. IPL records. News. Injury.")

#             # ── EXIT ──────────────────────────────────────────────
#             elif any(w in cmd for w in ["exit","stop","bye","goodbye","band karo","shutdown","shut down"]):
#                 speak("Goodbye sir. Jarvis signing off. Enjoy the cricket.")
#                 os._exit(0)

#         except sr.WaitTimeoutError: pass
#         except sr.UnknownValueError: pass
#         except Exception as ex:
#             print(f"[Loop] {ex}")
#             time.sleep(1)


# # ══════════════════════════════════════════════════════════════════════
# #  ENTRY POINT
# # ══════════════════════════════════════════════════════════════════════
# if __name__ == "__main__":
#     pythoncom.CoInitialize()
#     speaker = win32com.client.Dispatch("SAPI.SpVoice")

#     print("=" * 74)
#     print("  JARVIS - REAL IPL 2026 INTELLIGENCE AGENT v13.0")

#     # Voice in background thread
#     vt = threading.Thread(target=jarvis_loop, args=(speaker,), daemon=True)
#     vt.start()

#     # Main thread: handle graphs (matplotlib must be on main thread)
#     while True:
#         try:
#             task, arg = GRAPH_QUEUE.get(timeout=1)
#             if task == "momentum":
#                 draw_momentum_dashboard(MATCH_STATE)
#             elif task == "batting":
#                 cache = PLAYER_CACHE.get(arg.lower(), {}) if arg else {}
#                 scores = cache.get("runs", [])
#                 ml     = cache.get("ml")
#                 if not scores:
#                     raw    = get_player_raw_data(arg)
#                     scores = raw.get("scores", [])
#                     ml     = predict_future_score(scores) if len(scores) >= 3 else None
#                 draw_batting_graph(arg, scores, ml)
#             elif task == "bowling":
#                 cache   = PLAYER_CACHE.get(arg.lower(), {}) if arg else {}
#                 wickets = cache.get("wickets", [])
#                 ecos    = cache.get("economies", [])
#                 ml      = cache.get("ml")
#                 if not wickets:
#                     raw     = get_player_raw_data(arg)
#                     wickets = raw.get("wickets", [])
#                     ecos    = raw.get("economies", [])
#                     ml      = predict_future_wickets(wickets, ecos) if len(wickets) >= 3 else None
#                 draw_bowling_graph(arg, wickets, ecos, ml)
#         except queue.Empty:
#             pass
#         except Exception as e:
#             print(f"[Graph] {e}")

import threading
import time
import requests
import win32com.client
import speech_recognition as sr
from ddgs import DDGS # Updated to new ddgs package
import pythoncom

# --- SYSTEM CONFIG ---
def jarvis_speak(text):
    """Stable Windows Voice - No Terminal Spam"""
    def speak():
        try:
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
        except:
            pass
    threading.Thread(target=speak, daemon=True).start()
    print(f"\n[JARVIS]: {text}")

# --- CORE FEATURES ---
def handle_mega_features(query):
    cmd = query.lower()

    if "jarvis" in cmd:
        jarvis_speak("Yes Sir, I am here. Tell me.")
        return True

    if any(x in cmd for x in ["exit", "goodbye", "stop"]):
        jarvis_speak("Goodbye sir, Jarvis signing off.")
        time.sleep(2)
        return False

    # Aaj/Kal/Parso ke matches
    if any(x in cmd for x in ["today", "aaj ka"]):
        jarvis_speak("Sir, today is April 8, 2026. Delhi Capitals is playing Gujarat Titans at 7:30 PM.")
    
    elif any(x in cmd for x in ["yesterday", "kal ka result"]):
        jarvis_speak("Yesterday, Rajasthan Royals played a great match. Let me check the final score for you.")

    elif any(x in cmd for x in ["tomorrow", "kal kaunsa"]):
        jarvis_speak("Tomorrow's fixture is KKR versus LSG at Eden Gardens.")

    # Live Data & Predictions
    elif any(x in cmd for x in ["score", "situation", "table", "predict", "analy"]):
        jarvis_speak("Fetching data from the live server...")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"IPL 2026 {cmd}", max_results=1))
                if results:
                    print(f"\n[INTEL]: {results[0]['body']}")
                    jarvis_speak("Analysis complete.")
        except:
            jarvis_speak("Network error sir, please check your connection.")

    return True

# --- SILENT MAIN LOOP ---
def start_jarvis():
    rec = sr.Recognizer()
    rec.dynamic_energy_threshold = True
    
    print("--- JARVIS V23.0 (SILENT MODE) ---")
    print("System is active. Speak now...")
    jarvis_speak("Jarvis online and listening silently, sir.")
    
    while True:
        try:
            with sr.Microphone() as src:
                # No print here! It listens in silence.
                audio = rec.listen(src, timeout=None, phrase_time_limit=7)
                
                # Recognize quietly
                query = rec.recognize_google(audio, language='en-in')
                print(f"\n[YOU]: {query}") # Sirf tab dikhega jab aap bologe
                
                if not handle_mega_features(query):
                    break
        except sr.UnknownValueError:
            continue # Silence is maintained if nothing is understood
        except Exception as e:
            pass

if __name__ == "__main__":
    start_jarvis()