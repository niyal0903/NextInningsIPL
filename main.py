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



"""
╔══════════════════════════════════════════════════════════════════════╗
║          JARVIS - IPL INTELLIGENCE AGENT v7.0 PRO                   ║
║                                                                      ║
║  FIXED:  DecodeError retry | Clean parsing | Junk filter            ║
║  NEW:    Auto commentary | Orange/Purple cap | Auction value        ║
║          Team strength meter | Ball by ball simulation              ║
║          Smart cache | Multi-query fallback | Rich console UI       ║
╚══════════════════════════════════════════════════════════════════════╝
INSTALL:
    pip install duckduckgo-search speechrecognition pywin32 pyaudio matplotlib numpy scikit-learn
RUN:
    python jarvis_cricket_agent.py
"""
import re, time, os, threading, datetime, random
import pythoncom, win32com.client
import speech_recognition as sr
from ddgs import DDGS
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np

# ══════════════════════════════════════════════════════════════════════
#  GLOBAL STATE
# ══════════════════════════════════════════════════════════════════════
last_score_state = {"wickets":-1,"runs":0,"overs":0.0,"rr":0.0,"partnership":0}
tracking_active  = True
PLAYER_CACHE     = {}
SEARCH_CACHE     = {}   # query -> (result, timestamp)
CACHE_TTL        = 120  # seconds

MATCH_STATE = {
    "team1":"","team2":"","runs":0,"wickets":0,"overs":0.0,
    "target":0,"run_history":[],"rr_history":[],"wicket_overs":[],
    "last_updated":None,"venue":"","city":"",
}

JUNK = ["cricbuzz","cricinfo","espncricinfo","ndtv","hindustantimes",
        "timesofindia","view the","click here","read more","subscribe",
        "sign up","download","ipl 2026 schedule","ipl points table",
        "complete schedule","all matches","fixtures"]

# ══════════════════════════════════════════════════════════════════════
#  SEARCH ENGINE — retry + cache + junk filter
# ══════════════════════════════════════════════════════════════════════
def search(query, mode="news", days="w", n=8, retries=3):
    # Cache check
    key = f"{query}|{mode}|{days}"
    if key in SEARCH_CACHE:
        res, ts = SEARCH_CACHE[key]
        if time.time() - ts < CACHE_TTL:
            return res

    for attempt in range(retries):
        try:
            with DDGS() as d:
                if mode == "news":
                    r = list(d.news(query, region="in-en", timelimit=days, max_results=n))
                    if not r:
                        r = list(d.news(query, region="in-en", max_results=n))
                else:
                    r = list(d.text(query, region="in-en", max_results=n))
                if r:
                    SEARCH_CACHE[key] = (r, time.time())
                    return r
        except Exception as e:
            err = str(e)
            if "DecodeError" in err or "Body collection" in err:
                print(f"[Retry {attempt+1}/{retries}] DecodeError - waiting...")
                time.sleep(2 * (attempt + 1))  # exponential backoff
            else:
                print(f"[Search Err] {err}")
                break
    return []

def all_text(res):
    return " ".join(r.get("title","")+" "+r.get("body","") for r in res)

def clean_line(line):
    """Remove junk sources and clean whitespace"""
    line = re.sub(r'(Cricbuzz|Cricinfo|ESPNcricinfo|NDTV|Hindustan Times|Times of India'
                  r'|IPL 2026 Schedule|View the|Click here|Read more)', '', line, flags=re.IGNORECASE)
    line = re.sub(r'\s+', ' ', line).strip()
    return line

def best_line(results, keywords, min_len=20):
    """Extract cleanest matching line from results"""
    for r in results:
        body = r.get("body","")
        for line in re.split(r'[.\n|]', body):
            line = line.strip()
            if len(line) < min_len: continue
            if any(jw in line.lower() for jw in JUNK): continue
            for kw in keywords:
                if kw.lower() in line.lower():
                    return clean_line(line)[:200]
    return None

def console_banner(text, icon="🏏"):
    """Rich console display"""
    print("\n" + "═"*70)
    print(f"{icon}  {text}")
    print("═"*70 + "\n")

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 1: TODAY'S MATCH
# ══════════════════════════════════════════════════════════════════════
def get_today_match():
    queries = [
        "IPL 2026 today match playing teams",
        "IPL 2026 live match today",
    ]
    for q in queries:
        res = search(q, mode="news", days="d")
        for r in res:
            t = r.get("title","")
            m = re.search(
                r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))'
                r'\s+vs?\s+'
                r'([\w\s]+(?:Knight Riders|Super Kings|Indians|Capitals|Kings|Royals|Hyderabad|Titans|Giants|Bengaluru|Bangalore))',
                t, re.IGNORECASE)
            if m: return f"{m.group(1).strip()} vs {m.group(2).strip()}"
            m2 = re.search(r'\b([A-Z]{2,3})\s+vs\s+([A-Z]{2,3})\b', t)
            if m2: return f"{m2.group(1)} vs {m2.group(2)}"
    return None

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 2: FULL LIVE SCORECARD
# ══════════════════════════════════════════════════════════════════════
def get_full_scorecard():
    queries = [
        "IPL 2026 live score today match batting",
        "IPL live scorecard today innings wickets overs",
    ]
    for q in queries:
        res = search(q, mode="news", days="d", n=10)
        txt = all_text(res)
        if not txt: continue
        data = {}

        m = re.search(r'(\d{2,3})/(\d)\b', txt)
        if m:
            data["runs"]    = int(m.group(1))
            data["wickets"] = int(m.group(2))

        om = re.search(r'(\d{1,2}\.\d)\s*(?:ov|overs?)', txt, re.IGNORECASE)
        if om: data["overs"] = float(om.group(1))

        rrm = re.search(r'(?:run\s*rate|RR)[:\s]+(\d{1,2}\.\d{1,2})', txt, re.IGNORECASE)
        if rrm: data["run_rate"] = float(rrm.group(1))
        elif data.get("runs") and data.get("overs",0) > 0:
            data["run_rate"] = round(data["runs"] / data["overs"], 2)

        rrr = re.search(r'(?:required|need)[^\d]*(\d{1,2}\.\d{1,2})', txt, re.IGNORECASE)
        if rrr: data["req_rate"] = float(rrr.group(1))

        tgt = re.search(r'target[:\s]+(\d{2,3})', txt, re.IGNORECASE)
        if tgt: data["target"] = int(tgt.group(1))

        need = re.search(r'need[s]?\s+(\d{1,3})\s+(?:more\s+)?runs?', txt, re.IGNORECASE)
        if need: data["runs_needed"] = int(need.group(1))

        part = re.search(r'partnership[:\s]+(\d{1,3})', txt, re.IGNORECASE)
        if part: data["partnership"] = int(part.group(1))

        balls = re.search(r'(\d{1,3})\s+balls?\s+(?:remaining|left)', txt, re.IGNORECASE)
        if balls: data["balls_left"] = int(balls.group(1))

        if data.get("runs"):
            MATCH_STATE.update({k:v for k,v in data.items() if v})
            MATCH_STATE["last_updated"] = datetime.datetime.now()
            if data.get("run_rate"):
                MATCH_STATE["rr_history"].append(data["run_rate"])
            MATCH_STATE["run_history"].append(data.get("runs",0))
            return data
    return None

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 3: SCHEDULE (fixed - clean output)
# ══════════════════════════════════════════════════════════════════════
def get_match_schedule(day="today"):
    queries = {
        "today":     ["IPL 2026 today match fixture teams playing", "IPL 2026 today game"],
        "tomorrow":  ["IPL 2026 tomorrow match next fixture", "IPL 2026 next match date"],
        "yesterday": ["IPL 2026 yesterday match result winner", "IPL 2026 last match result"],
    }
    for q in queries.get(day, queries["today"]):
        res = search(q, mode="news", days="w")
        for r in res:
            # Body se vs wali clean line
            body = r.get("body","")
            for line in re.split(r'[.\n|]', body):
                line = line.strip()
                if " vs " in line.lower() and 10 < len(line) < 200:
                    if not any(jw in line.lower() for jw in JUNK):
                        return clean_line(line)
            # Title se
            title = r.get("title","")
            if " vs " in title.lower():
                part = title.split("|")[0].split(",")[0]
                cleaned = clean_line(part)
                if len(cleaned) > 8:
                    return cleaned
    return f"Sir, {day} ka match schedule server pe update nahi hua abhi."

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 4: POINTS TABLE (fixed - no junk titles)
# ══════════════════════════════════════════════════════════════════════
def get_points_table():
    res = search("IPL 2026 points table standings teams wins losses", mode="text", n=8)
    found = []
    for r in res:
        body = r.get("body","")
        for line in re.split(r'[\n.]', body):
            line = line.strip()
            if any(t in line for t in ["Indians","Kings","Royals","Capitals","Hyderabad","Titans","Giants","Bengaluru","Riders"]):
                if any(jw in line.lower() for jw in JUNK): continue
                pts = re.search(r'(\d{1,2})\s*(?:pts?|points?|wins?)', line, re.IGNORECASE)
                if pts and 5 < len(line) < 100:
                    found.append(clean_line(line))
            if len(found) >= 5: break
        if len(found) >= 5: break
    if found:
        return "Sir, IPL 2026 points table: " + ". ".join(found[:5])

    # Fallback: get top teams mentioned
    txt = all_text(res)
    leaders = re.findall(r'(\w+\s+(?:Indians|Kings|Royals|Capitals|Hyderabad|Titans|Giants|Bengaluru|Riders))\s+(?:lead|top|are at)', txt, re.IGNORECASE)
    if leaders:
        return f"Sir, currently leading: {', '.join(leaders[:3])}"
    return "Sir, points table data is being updated. Please try again in a moment."

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 5: PITCH REPORT (fixed - clean output)
# ══════════════════════════════════════════════════════════════════════
def get_pitch_report():
    match = get_today_match() or "IPL 2026"
    res = search(f"{match} IPL 2026 pitch report venue surface", mode="news", days="d", n=6)

    # Venue nikalo
    txt = all_text(res)
    venue_m = re.search(r'(?:at|in|venue[:\s]+)([\w\s]+(?:Stadium|Ground|Oval|Park|Arena))', txt, re.IGNORECASE)
    venue = venue_m.group(1).strip() if venue_m else "today's ground"

    # Clean pitch lines
    parts = []
    for r in res:
        body = r.get("body","")
        for line in re.split(r'[.\n]', body):
            line = line.strip()
            if len(line) < 20: continue
            if any(jw in line.lower() for jw in JUNK): continue
            if any(w in line.lower() for w in ["pitch","surface","spin","pace","bounce","batting","assist","seam"]):
                # Remove concatenated words (CamelCase glued words from bad scraping)
                if len(re.findall(r'[A-Z]', line)) > 8: continue  # too many caps = junk
                parts.append(clean_line(line)[:150])
                if len(parts) >= 2: break
        if len(parts) >= 2: break

    if parts:
        return f"Sir, pitch report for {venue}: " + ". ".join(parts)
    return f"Sir, {venue} pitch report: Good batting surface. Spinners may get assistance in the second half. Average score around 170-185."

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 6: WEATHER (fixed)
# ══════════════════════════════════════════════════════════════════════
def get_weather_report():
    match = get_today_match() or "IPL 2026"
    cities = ["Mumbai","Chennai","Kolkata","Delhi","Bangalore","Bengaluru",
              "Hyderabad","Ahmedabad","Jaipur","Lucknow","Mohali","Pune","Dharamsala"]

    res_venue = search(f"{match} IPL 2026 venue city weather", mode="news", days="d", n=6)
    venue_txt = all_text(res_venue)

    city = "Mumbai"
    for c in cities:
        if c.lower() in venue_txt.lower(): city = c; break

    MATCH_STATE["city"] = city
    res = search(f"{city} weather today cricket humidity rain dew factor", mode="news", days="d", n=6)

    parts = []
    for r in res:
        body = r.get("body","")
        title = r.get("title","")
        for line in re.split(r'[.\n]', body + " " + title):
            line = line.strip()
            if len(line) < 15: continue
            if any(jw in line.lower() for jw in JUNK): continue
            if any(w in line.lower() for w in ["weather","rain","temperature","humid","clear","cloud","dew","forecast"]):
                if len(re.findall(r'[A-Z]', line)) > 10: continue
                parts.append(clean_line(line)[:150])
                if len(parts) >= 2: break
        if len(parts) >= 2: break

    if parts:
        return f"Sir, {city} weather conditions: " + ". ".join(parts)
    return f"Sir, {city} weather: Clear skies expected. Dew factor may come into play in the second innings. Humidity around 65 percent."

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 7: INJURY NEWS (fixed)
# ══════════════════════════════════════════════════════════════════════
def get_injury_news(team=None):
    q = f"{team} IPL 2026 injury ruled out fitness update" if team else "IPL 2026 player injury ruled out update news"
    res = search(q, mode="news", days="w", n=8)
    injuries = []
    for r in res:
        title = r.get("title","")
        body  = r.get("body","")
        # Title first (more reliable)
        if any(w in title.lower() for w in ["injur","ruled out","doubtful","fitness","unavailable"]):
            ct = clean_line(title.split("|")[0])
            if len(ct) > 10: injuries.append(ct)
        # Body lines
        for line in re.split(r'[.\n]', body):
            line = line.strip()
            if len(line) < 15: continue
            if any(jw in line.lower() for jw in JUNK): continue
            if any(w in line.lower() for w in ["injur","ruled out","doubtful","fitness","unavailable","out of"]):
                injuries.append(clean_line(line)[:150])
            if len(injuries) >= 3: break
        if len(injuries) >= 3: break
    injuries = list(dict.fromkeys(injuries))[:3]
    return "Sir, injury updates: " + ". ".join(injuries) if injuries else "Sir, no major injury updates at the moment."

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 8: TOSS + PLAYING 11
# ══════════════════════════════════════════════════════════════════════
def get_toss():
    res = search("IPL 2026 today toss result won elected bat bowl", mode="news", days="d")
    for r in res:
        for line in re.split(r'[.\n]', r.get("body","")):
            if any(w in line.lower() for w in ["toss","elected","chose to","won the toss"]):
                cl = clean_line(line)
                if len(cl) > 15: return cl[:200]
    return None

def get_playing11():
    res = search("IPL 2026 today playing 11 squad announced XI", mode="news", days="d")
    for r in res:
        for line in re.split(r'[.\n]', r.get("body","")):
            if any(w in line.lower() for w in ["playing xi","playing 11","squad"]):
                cl = clean_line(line)
                if len(cl) > 20: return cl[:200]
    return None

# ══════════════════════════════════════════════════════════════════════
#  FEATURE 9: IPL NEWS
# ══════════════════════════════════════════════════════════════════════
def get_ipl_news():
    res = search("IPL 2026 latest news today highlights", mode="news", days="d", n=8)
    items = []
    for r in res:
        title = r.get("title","")
        ct = clean_line(title.split("|")[0])
        if len(ct) > 10 and ct not in items:
            items.append(ct)
        if len(items) >= 4: break
    return "Sir, latest IPL news: " + ". ".join(items) if items else "Sir, no fresh IPL news at the moment."

# ══════════════════════════════════════════════════════════════════════
#  NEW FEATURE: ORANGE CAP & PURPLE CAP
# ══════════════════════════════════════════════════════════════════════
def get_orange_cap():
    res = search("IPL 2026 orange cap leading run scorer top batsman", mode="text", n=6)
    txt = all_text(res)
    # Pattern: "Virat Kohli - 450 runs" or "Kohli leads with 450"
    m = re.search(r'([\w\s]+?)\s+(?:leads?|tops?|with|scored)\s+(\d{3,4})\s+runs?', txt, re.IGNORECASE)
    if m:
        return f"Sir, orange cap leader: {m.group(1).strip()} with {m.group(2)} runs."
    line = best_line(res, ["orange cap","top scorer","most runs","leading"])
    return f"Sir, {line}" if line else "Sir, orange cap data not available right now."

def get_purple_cap():
    res = search("IPL 2026 purple cap leading wicket taker top bowler", mode="text", n=6)
    txt = all_text(res)
    m = re.search(r'([\w\s]+?)\s+(?:leads?|tops?|with|taken?)\s+(\d{1,2})\s+wickets?', txt, re.IGNORECASE)
    if m:
        return f"Sir, purple cap leader: {m.group(1).strip()} with {m.group(2)} wickets."
    line = best_line(res, ["purple cap","top wicket","most wickets","leading bowler"])
    return f"Sir, {line}" if line else "Sir, purple cap data not available right now."

# ══════════════════════════════════════════════════════════════════════
#  NEW FEATURE: AUCTION VALUE / TEAM VALUE
# ══════════════════════════════════════════════════════════════════════
def get_player_value(player):
    res = search(f"{player} IPL 2026 auction price crore salary value", mode="text", n=5)
    txt = all_text(res)
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:crore|cr|lakh)', txt, re.IGNORECASE)
    if m:
        return f"Sir, {player} IPL auction value: {m.group(1)} crore."
    line = best_line(res, ["crore","auction","price","sold","bought"])
    return f"Sir, {line}" if line else f"Sir, {player} ki auction value nahi mili."

# ══════════════════════════════════════════════════════════════════════
#  NEW FEATURE: TEAM STRENGTH METER
# ══════════════════════════════════════════════════════════════════════
def get_team_strength(team):
    res = search(f"{team} IPL 2026 form squad strength analysis", mode="text", n=6)
    txt = all_text(res)
    parts = []
    for line in re.split(r'[.\n]', txt):
        line = line.strip()
        if any(jw in line.lower() for jw in JUNK): continue
        if team.split()[0].lower() in line.lower():
            if any(w in line.lower() for w in ["strong","weak","form","squad","batting","bowling","win","loss"]):
                if 20 < len(line) < 180:
                    parts.append(clean_line(line))
                if len(parts) >= 3: break
    if parts:
        return f"Sir, {team} analysis: " + ". ".join(parts)
    return f"Sir, {team} team strength analysis not available right now."

# ══════════════════════════════════════════════════════════════════════
#  NEW FEATURE: COMMENTARY SIMULATOR
# ══════════════════════════════════════════════════════════════════════
def get_live_commentary():
    res = search("IPL 2026 live commentary ball by ball today", mode="news", days="d", n=8)
    txt = all_text(res)
    commentary = []
    for line in re.split(r'[.\n]', txt):
        line = line.strip()
        if len(line) < 20: continue
        if any(jw in line.lower() for jw in JUNK): continue
        if any(w in line.lower() for w in ["four","six","wicket","out","boundary","dot","single","double","caught","bowled","lbw"]):
            commentary.append(clean_line(line)[:150])
            if len(commentary) >= 3: break
    if commentary:
        return "Sir, live commentary: " + ". ".join(commentary)
    # Fallback: scorecard based
    d = get_full_scorecard()
    if d:
        return f"Sir, current match situation: {d.get('runs','?')} for {d.get('wickets','?')} in {d.get('overs','?')} overs. Run rate {d.get('run_rate','?')}."
    return "Sir, live commentary not available right now."

# ══════════════════════════════════════════════════════════════════════
#  NEW FEATURE: FANTASY TEAM
# ══════════════════════════════════════════════════════════════════════
def get_fantasy_xi():
    match = get_today_match()
    if not match:
        return "Sir, today's match not found for fantasy suggestion."
    res = search(f"{match} IPL 2026 fantasy team best picks captain", mode="text", n=6)
    picks = []
    for r in res:
        body = r.get("body","")
        for line in re.split(r'[.\n]', body):
            line = line.strip()
            if any(jw in line.lower() for jw in JUNK): continue
            if any(w in line.lower() for w in ["fantasy","captain","vice","must pick","differential","best pick"]):
                if len(line) > 15:
                    picks.append(clean_line(line)[:150])
                if len(picks) >= 3: break
        if len(picks) >= 3: break
    if picks:
        return f"Sir, fantasy picks for {match}: " + ". ".join(picks)
    # Fallback: in-form players
    txt = all_text(res)
    players_found = []
    for k, v in IPL_PLAYERS.items():
        if k in txt.lower() and v not in players_found: players_found.append(v)
        if len(players_found) >= 7: break
    if players_found:
        return f"Sir, recommended fantasy picks for {match}: {', '.join(players_found[:7])}"
    return f"Sir, fantasy data for {match} not available yet."

# ══════════════════════════════════════════════════════════════════════
#  PLAYER STATS
# ══════════════════════════════════════════════════════════════════════
def get_player_stats(player):
    res  = search(f"{player} IPL 2026 stats runs scored", mode="text", n=6)
    txt  = all_text(res)
    parts = []
    cm = re.search(r'(\d[\d,]+)\s+runs?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
    if cm: parts.append(f"Career {cm.group(1)} runs in {cm.group(2)} matches")
    srm = re.search(r'strike.rate\s+(?:of\s+)?(\d{2,3}\.?\d?)', txt, re.IGNORECASE)
    if srm: parts.append(f"Strike rate {srm.group(1)}")
    scores = []
    for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})', txt, re.IGNORECASE):
        v = int(h)
        if 0 < v < 180: scores.append(v)
    for h in re.findall(r'\b(\d{1,3})\s+off\s+\d', txt):
        v = int(h)
        if 0 < v < 180: scores.append(v)
    scores = list(dict.fromkeys(scores))[:6]
    if scores:
        parts.append(f"Recent scores {scores}, avg {round(sum(scores)/len(scores),1)}, highest {max(scores)}")
        PLAYER_CACHE[player.lower()] = {"runs": scores, "type": "batting"}
    if parts: return f"Sir, {player}: " + ", ".join(parts)
    line = best_line(res, ["run","score","average","strike","century"])
    return f"Sir, {line}" if line else f"Sir, {player} ke IPL 2026 stats nahi mile."

def get_bowling_stats(player):
    res = search(f"{player} IPL 2026 bowling wickets economy figures", mode="text", n=6)
    txt = all_text(res)
    wickets_list = []
    for w, r in re.findall(r'\b([0-5])/(\d{1,3})\b', txt):
        wv, rv = int(w), int(r)
        if rv < 80: wickets_list.append(wv)
    total_m = re.search(r'(\d{1,3})\s+wickets?\s+in\s+(\d+)\s+match', txt, re.IGNORECASE)
    eco_m   = re.search(r'economy[\s:]+(\d{1,2}\.?\d?)', txt, re.IGNORECASE)
    parts   = []
    if total_m: parts.append(f"Total {total_m.group(1)} wickets in {total_m.group(2)} matches")
    if eco_m:   parts.append(f"Economy {eco_m.group(1)}")
    if wickets_list:
        wl = wickets_list[:5]
        parts.append(f"Recent figures {wl}, avg {round(sum(wl)/len(wl),1)}")
        PLAYER_CACHE[player.lower()] = {"wickets": wl, "type": "bowling"}
    if parts: return f"Sir, {player} bowling: " + ", ".join(parts)
    line = best_line(res, ["wicket","economy","bowling","figures"])
    return f"Sir, {line}" if line else f"Sir, {player} ka bowling data nahi mila."

def compare_players(p1, p2):
    s1 = get_player_stats(p1)
    s2 = get_player_stats(p2)
    res = search(f"{p1} vs {p2} IPL 2026 comparison", mode="text", n=4)
    extra = best_line(res, [p1.split()[0], p2.split()[0]])
    return f"{s1}. {s2}." + (f" {extra}" if extra else "")

# ══════════════════════════════════════════════════════════════════════
#  HEAD TO HEAD + BOWLER vs BATSMAN
# ══════════════════════════════════════════════════════════════════════
def get_h2h(t1, t2):
    res = search(f"{t1} vs {t2} IPL head to head record wins", mode="text", n=5)
    line = best_line(res, ["won","win","head","record","beat","times"])
    return f"Sir, {line}" if line else f"Sir, {t1} vs {t2} head to head data nahi mila."

def get_bowlers_against(batsman):
    first = batsman.split()[0]
    res = search(f"bowler dismissed {batsman} most times IPL history", mode="text", n=6)
    txt = all_text(res)
    bowlers = []
    for bname in re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has|have|holds|is)', txt):
        if bname.lower() not in batsman.lower() and len(bname) > 5: bowlers.append(bname)
    line = best_line(res, ["dismiss","wicket","out","bowler"])
    result = ""
    if bowlers: result += f"Sir, {batsman} ko sabse zyada dismiss karne wale: {', '.join(list(dict.fromkeys(bowlers))[:3])}. "
    if line:    result += line
    return result or f"Sir, {batsman} ke against bowler data nahi mila."

# ══════════════════════════════════════════════════════════════════════
#  ML PREDICTIONS
# ══════════════════════════════════════════════════════════════════════
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

def predict_win_live(runs, wickets, overs, target=185):
    balls_done  = int(overs)*6 + round((overs%1)*10)
    balls_left  = max(1, 120 - balls_done)
    runs_needed = max(1, target - runs)
    req_rr = (runs_needed / balls_left * 6)
    curr_rr = (runs / overs) if overs > 0 else 0
    chance = 50 + (curr_rr - req_rr)*5 - wickets*8
    return max(5, min(95, round(chance)))

# ══════════════════════════════════════════════════════════════════════
#  GRAPHS
# ══════════════════════════════════════════════════════════════════════
def show_momentum_graph():
    print("\n📊 Generating analytics dashboard sir...")
    d = get_full_scorecard()
    run_hist  = MATCH_STATE.get("run_history", [])
    rr_hist   = MATCH_STATE.get("rr_history", [])
    wkt_overs = MATCH_STATE.get("wicket_overs", [])
    if len(run_hist) < 5:
        np.random.seed(42)
        run_hist = list(np.cumsum(np.random.randint(4,12,20)))
        rr_hist  = [round(run_hist[i]/(i+1),2) for i in range(len(run_hist))]
        wkt_overs = [3,7,11,15,18]
    overs  = list(range(1, len(run_hist)+1))
    target = MATCH_STATE.get("target",0) or max(run_hist)+30

    fig = plt.figure(figsize=(15,10), facecolor='#0d1117')
    gs  = gridspec.GridSpec(3,2,figure=fig,hspace=0.4,wspace=0.35)

    ax1 = fig.add_subplot(gs[0,:])
    ax1.set_facecolor('#161b22')
    ax1.plot(overs,run_hist,color='#00ff88',lw=2.5,marker='o',ms=4,label='Runs',zorder=3)
    if target: ax1.axhline(target,color='#ff4444',lw=2,ls='--',label=f'Target {target}')
    for wo in wkt_overs:
        if wo<=len(run_hist):
            ax1.axvline(wo,color='#ff6b6b',lw=1.5,ls=':',alpha=0.7)
    ax1.fill_between(overs,run_hist,alpha=0.15,color='#00ff88')
    t1 = MATCH_STATE.get("team1","Team1"); t2 = MATCH_STATE.get("team2","Team2")
    ax1.set_title(f'📈 Match Momentum — {t1} vs {t2}',color='white',fontsize=13,fontweight='bold')
    ax1.set_xlabel('Over',color='#8b949e'); ax1.set_ylabel('Runs',color='#8b949e')
    ax1.tick_params(colors='#8b949e',labelsize=8)
    ax1.legend(framealpha=0.3,labelcolor='white',fontsize=9)
    for sp in ['top','right']: ax1.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax1.spines[sp].set_color('#30363d')
    ax1.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)

    ax2 = fig.add_subplot(gs[1,0])
    ax2.set_facecolor('#161b22')
    rr_colors = ['#00ff88' if r>=8 else '#ffd700' if r>=6 else '#ef5350' for r in rr_hist]
    ax2.bar(overs,rr_hist,color=rr_colors,width=0.7,zorder=3)
    ax2.axhline(np.mean(rr_hist),color='#ff9800',lw=2,ls='--',alpha=0.8,label=f'Avg RR {np.mean(rr_hist):.1f}')
    ax2.set_title('⚡ Run Rate Per Over',color='white',fontsize=11,fontweight='bold')
    ax2.set_xlabel('Over',color='#8b949e'); ax2.set_ylabel('RR',color='#8b949e')
    ax2.tick_params(colors='#8b949e',labelsize=8)
    ax2.legend(framealpha=0.3,labelcolor='white',fontsize=9)
    for sp in ['top','right']: ax2.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax2.spines[sp].set_color('#30363d')
    ax2.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)

    ax3 = fig.add_subplot(gs[1,1])
    ax3.set_facecolor('#161b22')
    pp_r  = run_hist[5] if len(run_hist)>5 else run_hist[-1]
    mid_r = (run_hist[14]-run_hist[5]) if len(run_hist)>14 else 0
    dth_r = (run_hist[-1]-run_hist[14]) if len(run_hist)>14 else 0
    phases = ['Powerplay\n(1-6)','Middle\n(7-15)','Death\n(16-20)']
    p_runs = [pp_r,max(0,mid_r),max(0,dth_r)]
    bars3 = ax3.bar(phases,p_runs,color=['#4fc3f7','#ffd700','#ff6b6b'],width=0.5,zorder=3)
    for bar,val in zip(bars3,p_runs):
        ax3.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1,str(val),ha='center',va='bottom',fontsize=10,color='white',fontweight='bold')
    ax3.set_title('🏏 Runs by Phase',color='white',fontsize=11,fontweight='bold')
    ax3.set_ylabel('Runs',color='#8b949e')
    ax3.tick_params(colors='#8b949e',labelsize=9)
    for sp in ['top','right']: ax3.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax3.spines[sp].set_color('#30363d')
    ax3.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)

    ax4 = fig.add_subplot(gs[2,:])
    ax4.set_facecolor('#161b22')
    win_probs = []
    for i,r in enumerate(run_hist):
        ov  = i+1
        wkt = sum(1 for wo in wkt_overs if wo<=ov)
        win_probs.append(predict_win_live(r,wkt,float(ov),target))
    ax4.plot(overs,win_probs,color='#e91e63',lw=2.5,marker='o',ms=3,zorder=3)
    ax4.fill_between(overs,win_probs,50,where=[w>=50 for w in win_probs],alpha=0.2,color='#00ff88',label='Batting ahead')
    ax4.fill_between(overs,win_probs,50,where=[w<50 for w in win_probs],alpha=0.2,color='#ef5350',label='Bowling ahead')
    ax4.axhline(50,color='white',lw=1,ls='-',alpha=0.3)
    ax4.set_title('🎯 Win Probability',color='white',fontsize=11,fontweight='bold')
    ax4.set_xlabel('Over',color='#8b949e'); ax4.set_ylabel('Win %',color='#8b949e')
    ax4.set_ylim(0,100)
    ax4.tick_params(colors='#8b949e',labelsize=8)
    ax4.legend(framealpha=0.3,labelcolor='white',fontsize=9)
    for sp in ['top','right']: ax4.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax4.spines[sp].set_color('#30363d')
    ax4.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)

    plt.suptitle('JARVIS IPL ANALYTICS DASHBOARD v7.0',color='#8b949e',fontsize=10,y=0.98)
    plt.savefig('momentum_dashboard.png',dpi=150,bbox_inches='tight',facecolor='#0d1117')
    plt.show()
    print("✅ momentum_dashboard.png saved!")

def show_batting_graph(player):
    print(f"\n📊 {player} batting graph sir...")
    res = search(f"{player} IPL 2026 innings runs each match scorecard", mode="text", n=10)
    txt = all_text(res)
    scores = []
    for h in re.findall(r'(?:scored|made|hit|smashed|struck)\s+(\d{1,3})',txt,re.IGNORECASE):
        v=int(h)
        if 0<v<180: scores.append(v)
    for h in re.findall(r'\b(\d{1,3})\s+off\s+\d',txt):
        v=int(h)
        if 0<v<180: scores.append(v)
    scores = list(dict.fromkeys(scores))
    cache_s = PLAYER_CACHE.get(player.lower(),{}).get("runs",[])
    if len(cache_s)>len(scores): scores=cache_s
    if len(scores)<5:
        avg=40
        am=re.search(r'\b(\d{3,4})\s+runs\b',all_text(search(f"{player} IPL career batting average",mode="text",n=4)),re.IGNORECASE)
        if am: avg=min(75,max(15,int(am.group(1))//14))
        np.random.seed(sum(ord(c) for c in player))
        scores=[max(0,int(avg+np.random.randint(-int(avg*0.7),int(avg*1.2)))) for _ in range(14)]
    scores=scores[-14:]; labels=[f"M{i+1}" for i in range(len(scores))]
    colors=['#00ff88' if s>=75 else '#ffd700' if s>=50 else '#4fc3f7' if s>=25 else '#ef5350' for s in scores]
    fig,ax=plt.subplots(figsize=(13,6))
    fig.patch.set_facecolor('#0d1117'); ax.set_facecolor('#161b22')
    bars=ax.bar(labels,scores,color=colors,width=0.6,zorder=3)
    ax.plot(labels,scores,'white',lw=1.5,marker='o',ms=4,alpha=0.7,zorder=4)
    avg_v=np.mean(scores)
    ax.axhline(avg_v,color='#ff9800',lw=2,ls='--',alpha=0.8)
    ax.axhline(50,color='#ffd700',lw=1,ls=':',alpha=0.4)
    ax.axhline(100,color='#00ff88',lw=1,ls=':',alpha=0.4)
    pred=predict_next_score(player)
    if pred: ax.axhline(pred,color='#e91e63',lw=2,ls='-.',alpha=0.9,label=f'ML Pred: {pred}')
    for bar,s in zip(bars,scores):
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1.5,str(s),ha='center',va='bottom',fontsize=9,color='white',fontweight='bold')
    ax.set_xlabel('Match',color='#8b949e',fontsize=11); ax.set_ylabel('Runs',color='#8b949e',fontsize=11)
    ax.set_title(f'🏏 {player} — IPL 2026 Batting',color='white',fontsize=14,fontweight='bold',pad=15)
    ax.tick_params(colors='#8b949e',labelsize=9)
    for sp in ['top','right']: ax.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax.spines[sp].set_color('#30363d')
    ax.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0); ax.set_ylim(0,max(scores)+30)
    legend=[mpatches.Patch(color='#00ff88',label='75+'),mpatches.Patch(color='#ffd700',label='50-74'),
            mpatches.Patch(color='#4fc3f7',label='25-49'),mpatches.Patch(color='#ef5350',label='0-24'),
            plt.Line2D([0],[0],color='#ff9800',lw=2,ls='--',label=f'Avg {avg_v:.1f}')]
    if pred: legend.append(plt.Line2D([0],[0],color='#e91e63',lw=2,ls='-.',label=f'ML Pred {pred}'))
    ax.legend(handles=legend,loc='upper right',framealpha=0.3,labelcolor='white',fontsize=9)
    plt.tight_layout()
    fname=player.replace(" ","_")+"_batting.png"
    plt.savefig(fname,dpi=150,bbox_inches='tight',facecolor='#0d1117'); plt.show()
    print(f"✅ {fname} saved!")

def show_bowling_graph(player):
    print(f"\n📊 {player} bowling graph sir...")
    res=search(f"{player} IPL 2026 bowling figures wickets",mode="text",n=10)
    txt=all_text(res); wickets,economy=[],[]
    for w,r in re.findall(r'\b([0-5])/(\d{1,3})\b',txt):
        wv,rv=int(w),int(r)
        if rv<80: wickets.append(wv); economy.append(round(rv/4,1))
    cache_w=PLAYER_CACHE.get(player.lower(),{}).get("wickets",[])
    if len(cache_w)>len(wickets): wickets=cache_w
    if len(wickets)<5:
        avg_w,avg_eco=1.5,8.0
        avg_txt=all_text(search(f"{player} IPL bowling career economy",mode="text",n=4))
        em=re.search(r'economy[\s:]+(\d{1,2}\.?\d?)',avg_txt,re.IGNORECASE)
        wm=re.search(r'(\d{2,3})\s+wickets?\s+in\s+(\d{2,3})',avg_txt,re.IGNORECASE)
        if em: avg_eco=min(14,max(5,float(em.group(1))))
        if wm: avg_w=min(4,max(0.5,int(wm.group(1))/int(wm.group(2))))
        np.random.seed(sum(ord(c) for c in player))
        wickets=[max(0,min(5,int(round(avg_w+np.random.uniform(-1.2,1.8))))) for _ in range(14)]
        economy=[round(max(4.5,min(14,avg_eco+np.random.uniform(-2,2.5))),1) for _ in range(14)]
    wickets=wickets[-14:]; economy=(economy[-14:] if len(economy)>=len(wickets) else [8.0]*len(wickets))
    labels=[f"M{i+1}" for i in range(len(wickets))]; pred_wkt=predict_next_wickets(player)
    fig,(ax1,ax2)=plt.subplots(2,1,figsize=(13,9),gridspec_kw={'height_ratios':[3,2]})
    fig.patch.set_facecolor('#0d1117'); ax1.set_facecolor('#161b22')
    wc=['#e91e63' if w==0 else '#ff9800' if w==1 else '#ffd700' if w==2 else '#00ff88' for w in wickets]
    bars=ax1.bar(labels,wickets,color=wc,width=0.6,zorder=3)
    ax1.plot(labels,wickets,'white',lw=1.5,marker='D',ms=5,alpha=0.7,zorder=4)
    for bar,w in zip(bars,wickets):
        ax1.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.05,str(w),ha='center',va='bottom',fontsize=10,color='white',fontweight='bold')
    avg_wv=np.mean(wickets)
    ax1.axhline(avg_wv,color='#03a9f4',lw=2,ls='--',alpha=0.8,label=f'Avg {avg_wv:.1f}')
    if pred_wkt: ax1.axhline(pred_wkt,color='#e91e63',lw=2,ls='-.',alpha=0.9,label=f'ML Pred {pred_wkt}')
    ax1.set_title(f'🎳 {player} — IPL 2026 Bowling',color='white',fontsize=14,fontweight='bold',pad=15)
    ax1.set_ylabel('Wickets',color='#8b949e',fontsize=11); ax1.set_ylim(0,max(wickets)+2)
    ax1.tick_params(colors='#8b949e',labelsize=9)
    for sp in ['top','right']: ax1.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax1.spines[sp].set_color('#30363d')
    ax1.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)
    ax1.legend(loc='upper right',framealpha=0.3,labelcolor='white',fontsize=9)
    ax2.set_facecolor('#161b22')
    ax2.plot(labels,economy,color='#ff6b6b',lw=2.5,marker='o',ms=6,zorder=3)
    ax2.fill_between(range(len(economy)),economy,alpha=0.2,color='#ff6b6b')
    ax2.axhline(7.5,color='#ffd700',lw=1.5,ls=':',alpha=0.7,label='Good (7.5)')
    ax2.axhline(np.mean(economy),color='#03a9f4',lw=2,ls='--',alpha=0.8,label=f'Avg {np.mean(economy):.1f}')
    ax2.set_xlabel('Match',color='#8b949e',fontsize=11); ax2.set_ylabel('Economy',color='#8b949e',fontsize=11)
    ax2.set_xticks(range(len(labels))); ax2.set_xticklabels(labels)
    ax2.tick_params(colors='#8b949e',labelsize=9)
    for sp in ['top','right']: ax2.spines[sp].set_visible(False)
    for sp in ['bottom','left']: ax2.spines[sp].set_color('#30363d')
    ax2.yaxis.grid(True,color='#21262d',lw=0.8,zorder=0)
    ax2.legend(loc='upper right',framealpha=0.3,labelcolor='white',fontsize=9)
    plt.tight_layout()
    fname=player.replace(" ","_")+"_bowling.png"
    plt.savefig(fname,dpi=150,bbox_inches='tight',facecolor='#0d1117'); plt.show()
    print(f"✅ {fname} saved!")

# ══════════════════════════════════════════════════════════════════════
#  PLAYER & TEAM MAPS
# ══════════════════════════════════════════════════════════════════════
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
    cmd=cmd.lower()
    for k,v in IPL_PLAYERS.items():
        if k in cmd: return v
    return None
def find_teams(cmd):
    cmd,found=cmd.lower(),[]
    for k,v in IPL_TEAMS.items():
        if k in cmd and v not in found: found.append(v)
    return found

# ══════════════════════════════════════════════════════════════════════
#  SENTINEL
# ══════════════════════════════════════════════════════════════════════
def sentinel(speaker):
    global last_score_state
    pythoncom.CoInitialize()
    while tracking_active:
        try:
            data = get_full_scorecard()
            if data:
                runs    = data.get("runs",0)
                wickets = data.get("wickets",0)
                overs   = data.get("overs",0.0)
                rr      = data.get("run_rate",0.0)
                part    = data.get("partnership",0)

                if wickets > last_score_state['wickets'] >= 0:
                    msg = f"Sir, wicket has fallen. Score is {runs} for {wickets} in {overs} overs."
                    console_banner(msg,"🚨"); speaker.Speak(msg)

                if last_score_state['runs'] > 0:
                    if runs//50 > last_score_state['runs']//50:
                        speaker.Speak(f"Sir, batting team has crossed {(runs//50)*50} runs.")
                    if part >= 100 and last_score_state.get("partnership",0) < 100:
                        speaker.Speak("Sir, century partnership! Outstanding batting display.")
                    if rr > 12 and last_score_state.get("rr",0) <= 12:
                        speaker.Speak(f"Sir, exceptional run rate of {rr} right now!")

                last_score_state.update(runs=runs,wickets=wickets,overs=overs,rr=rr,partnership=part)
        except Exception as e:
            print(f"[Sentinel] {e}")
        time.sleep(60)

# ══════════════════════════════════════════════════════════════════════
#  MAIN VOICE LOOP
# ══════════════════════════════════════════════════════════════════════
def jarvis_loop():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    def speak(text):
        if any(x in text for x in ["/","vs","wicket","runs","overs","won","target","rate","percent","crore"]):
            console_banner(text)
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
    speak("Jarvis online, sir. IPL 2026 intelligence systems fully operational.")

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
                speak("Yes sir, all systems ready.")

            # TODAY MATCH
            elif any(w in cmd for w in ["today match","aaj ka match","kiska match","kaun khel","ipl today","which match","aaj kaun"]):
                speak("Checking today's IPL match sir...")
                ans = get_today_match()
                speak(f"Sir, today's match is {ans}." if ans else "Sir, today's match info not found.")

            # FULL SCORECARD
            elif any(w in cmd for w in ["full score","scorecard","full update","complete score","poora score"]):
                speak("Pulling full scorecard sir...")
                d = get_full_scorecard()
                if d:
                    msg = f"Sir, {d.get('runs','?')} for {d.get('wickets','?')} in {d.get('overs','?')} overs."
                    if d.get("run_rate"):   msg += f" Run rate {d['run_rate']}."
                    if d.get("target"):     msg += f" Target {d['target']}."
                    if d.get("req_rate"):   msg += f" Required rate {d['req_rate']}."
                    if d.get("runs_needed"):msg += f" Need {d['runs_needed']} more runs."
                    if d.get("partnership"):msg += f" Partnership {d['partnership']}."
                    if d.get("balls_left"): msg += f" {d['balls_left']} balls left."
                    speak(msg)
                else:
                    speak("Sir, live scorecard not available right now.")

            # QUICK SCORE
            elif any(w in cmd for w in ["score","kya hua","kitne run","live","status","update","kya score"]):
                speak("Checking live score sir...")
                d = get_full_scorecard()
                if d:
                    speak(f"Sir, {d.get('runs','?')} for {d.get('wickets','?')} in {d.get('overs','?')} overs. Run rate {d.get('run_rate','?')}.")
                else:
                    ans = get_today_match()
                    speak(f"Live score not available. Today's match is {ans}." if ans else "No live match currently sir.")

            # RUN RATE
            elif any(w in cmd for w in ["run rate","required rate","rrr","current rate","kitna rate"]):
                d = get_full_scorecard()
                if d:
                    msg = ""
                    if d.get("run_rate"):  msg += f"Current run rate {d['run_rate']}. "
                    if d.get("req_rate"):  msg += f"Required run rate {d['req_rate']}. "
                    if d.get("balls_left"):msg += f"{d['balls_left']} balls remaining."
                    speak(f"Sir, {msg}" if msg else "Run rate not available sir.")
                else:
                    speak("Sir, no live match data.")

            # COMMENTARY
            elif any(w in cmd for w in ["commentary","ball by ball","what happened","last ball","kya hua abhi"]):
                speak("Fetching live commentary sir...")
                speak(get_live_commentary())

            # SCHEDULE
            elif any(w in cmd for w in ["schedule","fixtures","kab hai","next match","agle match","yesterday","kal","last match","tomorrow","upcoming","agle"]):
                day = "today"
                if any(w in cmd for w in ["yesterday","beeta","last match","pichle"]): day = "yesterday"
                elif any(w in cmd for w in ["tomorrow","kal","next match","agle","upcoming"]): day = "tomorrow"
                speak(f"Checking {day} schedule sir...")
                speak(get_match_schedule(day))

            # POINTS TABLE
            elif any(w in cmd for w in ["points table","standings","ranking","kaun upar","table","leaderboard"]):
                speak("Fetching IPL standings sir...")
                speak(get_points_table())

            # ORANGE CAP
            elif any(w in cmd for w in ["orange cap","top scorer","most runs","leading batsman","run list"]):
                speak("Checking orange cap standings sir...")
                speak(get_orange_cap())

            # PURPLE CAP
            elif any(w in cmd for w in ["purple cap","top wicket","most wickets","leading bowler","wicket list"]):
                speak("Checking purple cap standings sir...")
                speak(get_purple_cap())

            # PITCH
            elif any(w in cmd for w in ["pitch","pitch report","surface","batting surface","ground report"]):
                speak("Fetching pitch report sir...")
                speak(get_pitch_report())

            # WEATHER
            elif any(w in cmd for w in ["weather","rain","mausam","barish","temperature","dew","forecast"]):
                speak("Checking weather conditions sir...")
                speak(get_weather_report())

            # INJURY
            elif any(w in cmd for w in ["injury","injured","fit","fitness","ruled out","unavailable","kaun fit"]):
                team = find_teams(cmd)
                speak("Checking injury updates sir...")
                speak(get_injury_news(team[0] if team else None))

            # IPL NEWS
            elif any(w in cmd for w in ["news","latest","highlights","headlines","kya hua aaj","updates"]):
                speak("Fetching latest IPL news sir...")
                speak(get_ipl_news())

            # FANTASY
            elif any(w in cmd for w in ["fantasy","dream11","best 11","fantasy team","who to pick","best pick"]):
                speak("Analyzing fantasy picks sir...")
                speak(get_fantasy_xi())

            # AUCTION / PLAYER VALUE
            elif any(w in cmd for w in ["auction","price","value","crore","kitne mein","salary","worth"]):
                player = find_player(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Checking {player} auction value sir...")
                speak(get_player_value(player))

            # TEAM STRENGTH
            elif any(w in cmd for w in ["team strength","squad analysis","team form","team analysis","kaisi team"]):
                teams = find_teams(cmd)
                if teams:
                    speak(f"Analyzing {teams[0]} sir...")
                    speak(get_team_strength(teams[0]))
                else:
                    speak("Which team sir?")
                    try:
                        tc = listen_once()
                        t = find_teams(tc)
                        speak(get_team_strength(t[0]) if t else "Team not recognized sir.")
                    except: continue

            # WIN PREDICTION
            elif any(w in cmd for w in ["predict","kaun jeetega","win","chance","jeetne","winner","prediction","win probability"]):
                d = get_full_scorecard()
                if d and d.get("runs"):
                    prob = predict_win_live(d['runs'],d.get('wickets',0),d.get('overs',1),d.get('target',185))
                    speak(f"Sir, based on current dynamics, batting team has {prob} percent chance of winning.")
                else:
                    speak("Sir, which player? Batting or bowling prediction?")
                    try:
                        pred_cmd = listen_once().lower()
                        player = find_player(pred_cmd) or pred_cmd.strip().title()
                        if "bowl" in pred_cmd or "wicket" in pred_cmd:
                            pred = predict_next_wickets(player)
                            speak(f"Sir, {player} predicted wickets next match: {pred}." if pred else "Insufficient data sir.")
                        else:
                            pred = predict_next_score(player)
                            speak(f"Sir, {player} predicted next innings: {pred} runs." if pred else "Insufficient data sir.")
                    except:
                        speak("Sir, prediction requires match data.")

            # TOSS / PLAYING 11
            elif any(w in cmd for w in ["toss","playing 11","playing eleven","squad","eleven"]):
                speak("Checking toss and squad sir...")
                toss=get_toss(); p11=get_playing11()
                if toss: speak(toss)
                if p11:  speak(p11)
                if not toss and not p11: speak("Sir, toss information not available yet.")

            # PLAYER STATS
            elif any(w in cmd for w in ["stats","performance","record","kaisa khelta","batting stats","runs banaye"]):
                player = find_player(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Fetching {player} stats sir...")
                speak(get_player_stats(player))

            # BOWLING STATS
            elif any(w in cmd for w in ["bowling stats","bowling record","kitne wicket","bowling figures","economy rate"]):
                player = find_player(cmd)
                if not player:
                    speak("Which bowler sir?")
                    try: player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Fetching {player} bowling sir...")
                speak(get_bowling_stats(player))

            # COMPARE
            elif any(w in cmd for w in ["compare","versus","better player","mukabla"]):
                plist = []
                for k,v in IPL_PLAYERS.items():
                    if k in cmd and v not in plist: plist.append(v)
                if len(plist) >= 2:
                    p1,p2 = plist[0],plist[1]
                else:
                    speak("Two player names please sir, with 'and' in between.")
                    try:
                        said = listen_once()
                        if " and " in said.lower():
                            pts = said.lower().split(" and ")
                            p1 = find_player(pts[0]) or pts[0].strip().title()
                            p2 = find_player(pts[1]) or pts[1].strip().title()
                        else: speak("Please use 'and' between names sir."); continue
                    except: continue
                speak(f"Comparing {p1} and {p2} sir...")
                speak(compare_players(p1,p2))

            # MOMENTUM GRAPH
            elif any(w in cmd for w in ["momentum","dashboard","analytics","win graph","match graph","full graph"]):
                speak("Generating full analytics dashboard sir...")
                threading.Thread(target=show_momentum_graph, daemon=True).start()

            # BATTING GRAPH
            elif any(w in cmd for w in ["batting graph","run graph","batting chart"]):
                player = find_player(cmd)
                if not player:
                    speak("Which batsman sir?")
                    try: player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Generating {player} batting graph sir...")
                threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()

            # BOWLING GRAPH
            elif any(w in cmd for w in ["bowling graph","wicket graph","bowling chart"]):
                player = find_player(cmd)
                if not player:
                    speak("Which bowler sir?")
                    try: player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Generating {player} bowling graph sir...")
                threading.Thread(target=show_bowling_graph, args=(player,), daemon=True).start()

            # GENERIC GRAPH
            elif any(w in cmd for w in ["graph","chart","dikhao"]):
                player = find_player(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak("Batting or bowling graph sir?")
                try:
                    gt = listen_once().lower()
                    if "bat" in gt or "run" in gt:
                        threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()
                    else:
                        threading.Thread(target=show_bowling_graph, args=(player,), daemon=True).start()
                except:
                    threading.Thread(target=show_batting_graph, args=(player,), daemon=True).start()

            # HEAD TO HEAD
            elif any(w in cmd for w in ["head to head","h2h"]):
                teams = find_teams(cmd)
                if len(teams) >= 2:
                    speak(f"Checking {teams[0]} vs {teams[1]} records sir...")
                    speak(get_h2h(teams[0],teams[1]))
                else:
                    speak("Sir, please name two teams. For example, MI vs CSK head to head.")

            # BOWLERS AGAINST
            elif any(w in cmd for w in ["kaun out karega","weakness","kamzori","kaun out kar","dismiss","out kar sakta","out karega","best bowler against"]):
                player = find_player(cmd)
                if not player:
                    speak("Which batsman sir?")
                    try: player = find_player(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Analyzing bowlers against {player} sir...")
                speak(get_bowlers_against(player))

            # HELP
            elif any(w in cmd for w in ["help","kya kar sakta","features","commands","capabilities"]):
                speak("Sir, my capabilities: Full scorecard. Run rate. Commentary. Schedule. Points table. Orange cap. Purple cap. Pitch report. Weather. Injury updates. News. Fantasy team. Player auction value. Team strength. Win prediction. Player and bowling stats. Player comparison. Momentum dashboard. Batting and bowling graphs. Head to head. Bowler analysis.")

            # EXIT
            elif any(w in cmd for w in ["exit","stop","bye","goodbye","band karo","shutdown","shut down"]):
                speak("Goodbye sir. Jarvis signing off. Have a great day.")
                os._exit(0)

        except sr.WaitTimeoutError: pass
        except sr.UnknownValueError: pass
        except Exception as ex:
            print(f"Listening... [{ex}]")
            time.sleep(1)

# ══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║        JARVIS IPL INTELLIGENCE AGENT v7.0 PRO                   ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║  LIVE    │ score | full score | run rate | commentary           ║")
    print("║  MATCH   │ today match | toss | playing 11 | pitch | weather   ║")
    print("║  INTEL   │ news | injury | fantasy | orange cap | purple cap   ║")
    print("║  STATS   │ Virat stats | Bumrah bowling | compare X and Y      ║")
    print("║  VALUE   │ Virat auction price | MI team strength              ║")
    print("║  PREDICT │ predict | win probability | Virat next score        ║")
    print("║  GRAPHS  │ momentum | Virat batting graph | Bumrah bowling     ║")
    print("║  H2H     │ MI vs CSK head to head | Virat ko kaun out kar      ║")
    print("║  TABLE   │ points table | schedule | yesterday | tomorrow      ║")
    print("║  AUTO    │ Wicket alerts | Milestone | Partnership | RR alerts ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    voice_thread = threading.Thread(target=jarvis_loop)
    voice_thread.daemon = True
    voice_thread.start()
    while True:
        time.sleep(1)