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
JARVIS IPL 2026 - MAX LEVEL AGENT v14.0
========================================
Fresh build. Clean code. All features working.
ML + LLM + Live Data + Voice + Graphs
"""
import re, time, os, threading, queue
import pythoncom, win32com.client
import speech_recognition as sr
import numpy as np

from ml_brain   import predict_future_score, predict_future_wickets, calculate_win_probability
from llm_expert import get_expert_analysis, get_match_insight, check_llm_status
from scraper    import (search, all_text, best_sentences, is_junk, clean,
                         get_live_scorecard, get_today_match, get_schedule,
                         get_points_table, get_orange_cap, get_purple_cap,
                         get_player_raw_data, get_toss, get_playing11,
                         get_injury_news, get_ipl_news)
from graphs     import draw_batting_graph, draw_bowling_graph, draw_momentum_dashboard

# ══════════════════════════════════════════════════════
PLAYER_CACHE    = {}
GRAPH_QUEUE     = queue.Queue()
tracking_active = True
last_score      = {"wickets": -1, "runs": 0, "overs": 0.0, "rr": 0.0}
MATCH_STATE     = {
    "team1": "", "team2": "", "runs": 0, "wickets": 0, "overs": 0.0,
    "target": 0, "run_history": [], "rr_history": [], "wicket_overs": [],
}

IPL_PLAYERS = {
    "rohit":"Rohit Sharma","hardik":"Hardik Pandya","pandya":"Hardik Pandya",
    "bumrah":"Jasprit Bumrah","jasprit":"Jasprit Bumrah",
    "suryakumar":"Suryakumar Yadav","sky":"Suryakumar Yadav",
    "tilak":"Tilak Varma","dhoni":"MS Dhoni","msd":"MS Dhoni",
    "ruturaj":"Ruturaj Gaikwad","gaikwad":"Ruturaj Gaikwad",
    "jadeja":"Ravindra Jadeja","chahar":"Deepak Chahar",
    "dube":"Shivam Dube","pathirana":"Matheesha Pathirana",
    "virat":"Virat Kohli","kohli":"Virat Kohli","vk":"Virat Kohli",
    "patidar":"Rajat Patidar","salt":"Phil Salt","krunal":"Krunal Pandya",
    "shreyas":"Shreyas Iyer","iyer":"Shreyas Iyer",
    "narine":"Sunil Narine","russell":"Andre Russell","rinku":"Rinku Singh",
    "varun":"Varun Chakravarthy","starc":"Mitchell Starc",
    "pant":"Rishabh Pant","rishabh":"Rishabh Pant",
    "kuldeep":"Kuldeep Yadav","axar":"Axar Patel","mukesh":"Mukesh Kumar",
    "arshdeep":"Arshdeep Singh","maxwell":"Glenn Maxwell",
    "samson":"Sanju Samson","sanju":"Sanju Samson",
    "jaiswal":"Yashasvi Jaiswal","yashasvi":"Yashasvi Jaiswal",
    "parag":"Riyan Parag","riyan":"Riyan Parag",
    "klaasen":"Heinrich Klaasen","head":"Travis Head","travis":"Travis Head",
    "cummins":"Pat Cummins","harshal":"Harshal Patel",
    "rahul":"KL Rahul","kl":"KL Rahul","pooran":"Nicholas Pooran",
    "bishnoi":"Ravi Bishnoi","ravi":"Ravi Bishnoi",
    "miller":"David Miller","gill":"Shubman Gill","shubman":"Shubman Gill",
    "sudharsan":"Sai Sudharsan","sai":"Sai Sudharsan",
    "buttler":"Jos Buttler","rashid":"Rashid Khan",
    "siraj":"Mohammed Siraj","rabada":"Kagiso Rabada",
    "prasidh":"Prasidh Krishna","krishna":"Prasidh Krishna",
    "ishan":"Ishan Kishan","kishan":"Ishan Kishan",
    "sameer":"Sameer Rizvi","rizvi":"Sameer Rizvi",
    "unadkat":"Jaydev Unadkat","boult":"Trent Boult",
}
IPL_TEAMS = {
    "mumbai":"Mumbai Indians","mi":"Mumbai Indians",
    "chennai":"Chennai Super Kings","csk":"Chennai Super Kings",
    "rcb":"Royal Challengers Bengaluru","bangalore":"Royal Challengers Bengaluru",
    "kkr":"Kolkata Knight Riders","kolkata":"Kolkata Knight Riders",
    "delhi":"Delhi Capitals","dc":"Delhi Capitals",
    "punjab":"Punjab Kings","pbks":"Punjab Kings",
    "rajasthan":"Rajasthan Royals","rr":"Rajasthan Royals",
    "hyderabad":"Sunrisers Hyderabad","srh":"Sunrisers Hyderabad",
    "lucknow":"Lucknow Super Giants","lsg":"Lucknow Super Giants",
    "gujarat":"Gujarat Titans","gt":"Gujarat Titans",
}
VENUE_DB = {
    "wankhede":      "High-scoring. Fast outfield. Average 185+. Dew heavily impacts 2nd innings.",
    "eden gardens":  "Spin-friendly. Slower surface. Average 165. KKR home advantage.",
    "chinnaswamy":   "Highest scoring IPL venue. Thin air. Average 190+.",
    "chepauk":       "Spin-friendly. Low bounce. Average 155-165.",
    "narendra modi": "Flat pitch. Largest ground. Average 170-180.",
    "arun jaitley":  "Batting-friendly. Some swing early. Dew factor at night.",
    "rajiv gandhi":  "Good batting track. High scores. Pace gets movement initially.",
    "sawai mansingh":"Dry surface. Good for leg spinners. Average 165.",
    "ekana":         "Balanced pitch. LSG home advantage. Average 165-175.",
}
TEAM_CITY = {
    "mi":"Mumbai","csk":"Chennai","rcb":"Bengaluru","kkr":"Kolkata",
    "dc":"Delhi","pbks":"Mohali","rr":"Jaipur","srh":"Hyderabad",
    "lsg":"Lucknow","gt":"Ahmedabad","mumbai":"Mumbai","chennai":"Chennai",
    "delhi":"Delhi","punjab":"Mohali","rajasthan":"Jaipur",
    "hyderabad":"Hyderabad","lucknow":"Lucknow","gujarat":"Ahmedabad",
}

def fp(cmd):
    cmd = cmd.lower()
    for k,v in IPL_PLAYERS.items():
        if k in cmd: return v
    return None

def ft(cmd):
    cmd, found = cmd.lower(), []
    for k,v in IPL_TEAMS.items():
        if k in cmd and v not in found: found.append(v)
    return found

# ══════════════════════════════════════════════════════
#  SITUATION ANALYZER
# ══════════════════════════════════════════════════════
def analyze(runs, wickets, overs, target=0):
    if overs <= 0: return ""
    bl  = max(1, 120 - int(overs)*6 - round((overs%1)*10))
    rr  = round(runs/overs, 2)
    if target > 0:
        need = max(1, target-runs)
        req  = round(need/bl*6, 2)
        gap  = rr - req
        if gap > 1:   return f"Batting team ahead. Required rate {req} manageable."
        elif gap > -1: return f"Close contest. Required {req} vs current {rr}."
        elif gap > -3: return f"Tough chase. Required rate {req} well above {rr}."
        else:          return f"Very difficult. Need {need} from {bl} balls at {req}."
    else:
        proj = int(round(runs + rr * max(1,20-overs) * max(0.55,1-wickets*0.06)))
        if overs < 6:   return f"Powerplay. Projected {proj}."
        elif overs < 15:
            if wickets<=3: return f"Solid platform. Projected {proj}. Good position."
            elif wickets<=5: return f"Middle overs squeeze. Projected {proj}. Partnership needed."
            else:            return f"Wickets tumbling. Projected {proj}. Must rebuild."
        else:           return f"Death overs. Final push. Projected {proj}."

# ══════════════════════════════════════════════════════
#  CORE FEATURES
# ══════════════════════════════════════════════════════
def live_score():
    d = get_live_scorecard()
    if not d: return None, get_today_match()
    runs = d.get("runs",0); wkts = d.get("wickets",0)
    ovs  = d.get("overs",0.0); rr = d.get("run_rate",0.0)
    target = d.get("target",0)
    wp   = calculate_win_probability(runs, wkts, ovs, target)
    sit  = analyze(runs, wkts, ovs, target)
    # Update match state
    MATCH_STATE.update(runs=runs,wickets=wkts,overs=ovs,target=target,
        team1=d.get("team1",MATCH_STATE["team1"]),
        team2=d.get("team2",MATCH_STATE["team2"]))
    rh = MATCH_STATE["run_history"]
    if not rh or rh[-1]!=runs:
        rh.append(runs)
        if rr: MATCH_STATE["rr_history"].append(rr)
    msg = f"Sir, {runs} for {wkts} in {ovs} overs. Run rate {rr}."
    if target:
        need = d.get("runs_needed",0) or max(0,target-runs)
        balls = d.get("balls_left",0)
        msg += f" Chasing {target}. Need {need}" + (f" from {balls} balls." if balls else ".")
        msg += f" Win probability {wp.get('win_percent')}%."
    if sit: msg += f" {sit}"
    llm = get_match_insight(get_today_match() or "IPL 2026",
                            {**d,"win_percent":wp.get("win_percent",50)})
    if llm: msg += f" {llm}"
    return msg, None

def player_analysis(player, bowling=False):
    print(f"  [ML+LLM] Analyzing {player}...")
    raw = get_player_raw_data(player)
    if bowling:
        wkts = raw.get("wickets",[])
        ecos = raw.get("economies",[])
        if len(wkts) >= 3:
            ml  = predict_future_wickets(wkts, ecos)
            PLAYER_CACHE[player.lower()] = {"wickets":wkts,"economies":ecos,"ml":ml}
            exp = get_expert_analysis(player, wkts, ml.get("predicted",0), bowling=True)
            return (f"Sir, {player} bowling: Recent {wkts[:5]}. "
                    f"Avg {ml['average']} wkts. Economy {raw.get('economy','N/A')}. "
                    f"ML predicts {ml['predicted']} wkts next ({ml['trend']}, {ml['confidence']} confidence). "
                    f"{exp}")
        sents = best_sentences(search(f"{player} IPL 2026 bowling wickets economy",mode="text",n=5),
                               ["wicket","economy","bowling"])
        return f"Sir, {player}: " + ". ".join(sents) if sents else f"Sir, {player} bowling data not found."
    else:
        scores = raw.get("scores",[])
        if len(scores) >= 3:
            ml  = predict_future_score(scores)
            PLAYER_CACHE[player.lower()] = {"runs":scores,"ml":ml}
            exp = get_expert_analysis(player, scores, ml.get("predicted",0))
            career = f"Career {raw['career_runs']} runs. " if raw.get("career_runs") else ""
            return (f"Sir, {player}: {career}Recent innings {scores[:6]}. "
                    f"Avg {ml['average']}. SR {raw.get('strike_rate','N/A')}. "
                    f"Peak {ml['peak']}, Floor {ml['floor']}. "
                    f"ML predicts {ml['predicted']} next ({ml['trend']}, {ml['confidence']}). "
                    f"{exp}")
        sents = best_sentences(search(f"{player} IPL 2026 batting stats runs",mode="text",n=5),
                               ["run","score","average","strike"])
        return f"Sir, {player}: " + ". ".join(sents) if sents else f"Sir, {player} batting data not found."

def pitch_report():
    match = get_today_match() or "IPL 2026"
    ml    = match.lower()
    # Team-based venue
    for k,v in IPL_TEAMS.items():
        if k in ml:
            for vkey, vinfo in VENUE_DB.items():
                if k in vkey or vkey.split()[0] in v.lower():
                    return f"Sir, {v} home ground: {vinfo}"
    # Search
    res = search(f"{match} IPL 2026 pitch report venue surface today", mode="news", days="d", n=8)
    txt = all_text(res)
    for vkey, vinfo in VENUE_DB.items():
        if vkey in txt.lower():
            return f"Sir, {vkey.title()} pitch: {vinfo}"
    sents = best_sentences(res, ["pitch","surface","batting","spin","pace","bounce","flat"])
    return ("Sir, pitch report: " + ". ".join(sents[:2]) if sents
            else f"Sir, {match} pitch: Good batting conditions expected.")

def weather_report():
    match = get_today_match() or "IPL 2026"
    # Team-based city
    city = None
    for k,v in TEAM_CITY.items():
        if k in match.lower():
            city = v; break
    if not city:
        cities = ["Mumbai","Chennai","Kolkata","Delhi","Bengaluru","Hyderabad",
                  "Ahmedabad","Jaipur","Lucknow","Mohali","Pune","Dharamsala","Guwahati"]
        vtxt = all_text(search(f"{match} IPL 2026 venue city today",mode="news",days="d",n=5))
        city = next((c for c in cities if c.lower() in vtxt.lower()), "Mumbai")
    res   = search(f"{city} weather today IPL 2026 cricket rain dew",mode="news",days="d",n=6)
    sents = best_sentences(res,["weather","rain","temperature","dew","humid","clear","forecast"])
    valid = [s for s in sents if city.lower() in s.lower() or "today" in s.lower()]
    if valid: return f"Sir, {city} weather: " + ". ".join(valid[:2])
    if sents: return f"Sir, {city}: " + sents[0]
    return f"Sir, {city}: Clear conditions expected. Dew likely in 2nd innings."

def toss_analysis():
    toss = get_toss()
    if not toss: return "Sir, toss not announced yet."
    pitch = pitch_report()
    weather = weather_report()
    toss_l = toss.lower()
    if "bat" in toss_l:
        strategy = "Decision to bat first. Looking to set a strong total."
        if "dew" in (pitch+weather).lower():
            strategy += " Smart move given dew will assist batting later."
    elif "field" in toss_l or "bowl" in toss_l:
        strategy = "Opted to chase. Knowing the target gives an advantage."
        if "dew" in (pitch+weather).lower():
            strategy += " Dew in 2nd innings heavily favors this decision."
    else:
        strategy = "Strategic decision based on conditions."
    return f"Sir, {toss}. {strategy}"

def fantasy_team():
    match = get_today_match()
    if not match: return "Sir, today's match not found."
    res  = search(f"{match} IPL 2026 fantasy team best XI captain picks",mode="text",n=8)
    sents= best_sentences(res,["captain","must pick","differential","fantasy","key pick","vice"])
    players_found = []
    txt = all_text(res)
    for k,v in IPL_PLAYERS.items():
        if k in txt.lower() and v not in players_found: players_found.append(v)
        if len(players_found)>=8: break
    from llm_expert import get_fantasy_insight
    insight = get_fantasy_insight(match, players_found)
    if sents: return f"Sir, fantasy for {match}: " + ". ".join(sents[:2]) + f" {insight}"
    return insight or f"Sir, from {match}: Focus on in-form top-order batsmen and death bowlers."

def h2h(t1,t2):
    res   = search(f"{t1} vs {t2} IPL head to head record wins history",mode="text",n=6)
    sents = best_sentences(res,["won","win","head","record","beat","times"])
    from llm_expert import get_h2h_insight
    h2h_str = ". ".join(sents[:2]) if sents else "limited data"
    return get_h2h_insight(t1, t2, h2h_str)

def bowlers_against(batsman):
    res  = search(f"bowler dismissed {batsman} most times IPL history",mode="text",n=8)
    txt  = all_text(res)
    bowlers = []
    for b in re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has|have|holds|is)',txt):
        if b.lower() not in batsman.lower() and len(b)>5: bowlers.append(b)
    sents = best_sentences(res,["dismiss","wicket","out","bowler"])
    result = ""
    if bowlers:
        u = list(dict.fromkeys(bowlers))[:3]
        result += f"Sir, {batsman} ka kryptonite: {', '.join(u)}. "
    if sents: result += ". ".join(sents[:2])
    if result:
        exp = get_expert_analysis(batsman,[],0)
        return result + f" {exp}"
    return f"Sir, {batsman} vs bowler data not found."

def top_performers():
    match = get_today_match() or "IPL 2026"
    res   = search(f"{match} IPL 2026 top performers today runs wickets standout",mode="news",days="d",n=8)
    sents = best_sentences(res,["scored","took","wicket","fifty","century","hit","smashed"])
    kw    = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
    valid = [s for s in sents if kw in s.lower() or any(w in s.lower() for w in ["scored","wicket","took"])]
    if valid: return "Sir, top performers: " + ". ".join(valid[:3])
    return "Sir, top performer data not in live feed yet."

def match_summary():
    match = get_today_match() or "IPL 2026"
    res   = search(f"{match} IPL 2026 result summary innings highlights today",mode="news",days="d",n=8)
    sents = best_sentences(res,["won","beat","total","innings","result","chased","defended","scored"])
    kw    = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
    valid = [s for s in sents if kw in s.lower() or any(w in s.lower() for w in ["won","total","innings"])]
    if valid: return "Sir, match summary: " + ". ".join(valid[:3])
    msg, _ = live_score()
    return msg or "Sir, match summary not available yet."

def player_form(player):
    raw    = get_player_raw_data(player)
    scores = raw.get("scores",[])[:5]
    if len(scores)>=3:
        ml  = predict_future_score(scores)
        exp = get_expert_analysis(player, scores, ml.get("predicted",0))
        return (f"Sir, {player} form: Last {len(scores)} innings {scores}. "
                f"Avg {ml['average']}. Trend {ml['trend']}. ML predicts {ml['predicted']} next. {exp}")
    sents = best_sentences(
        search(f"{player} IPL 2026 form recent innings runs",mode="news",days="w",n=8),
        ["form","innings","run","scored","performing","consistent"])
    return ("Sir, "+player+" form: "+". ".join(sents[:2]) if sents
            else f"Sir, {player} recent form data not found.")

def player_milestone(player):
    res   = search(f"{player} IPL 2026 milestone record close needs runs wickets",mode="text",n=6)
    sents = best_sentences(res,["milestone","record","close","away","needs","require","century"])
    return ("Sir, " + ". ".join(sents[:2]) if sents
            else f"Sir, {player} milestone data not found.")

def ipl_records():
    res   = search("IPL 2026 records highest score most sixes fastest fifty",mode="text",n=6)
    sents = best_sentences(res,["record","highest","most","fastest","century","six","fifty"])
    return ("Sir, IPL 2026 records: " + ". ".join(sents[:3]) if sents
            else "Sir, IPL 2026 records not available.")

def auction_value(player):
    res = search(f"{player} IPL 2026 auction price crore salary",mode="text",n=6)
    txt = all_text(res)
    m   = re.search(r'(\d+(?:\.\d+)?)\s*(?:crore|cr)\b',txt,re.IGNORECASE)
    if m: return f"Sir, {player} auction value: {m.group(1)} crore."
    sents = best_sentences(res,["crore","auction","price","sold"])
    return f"Sir, {sents[0]}" if sents else f"Sir, {player} auction data not found."

def team_strength(team):
    res  = search(f"{team} IPL 2026 squad strength weakness key players",mode="text",n=6)
    t0   = team.split()[0].lower()
    parts= []
    for r in res:
        for line in re.split(r'[.\n]',r.get("body","")):
            line = line.strip()
            if is_junk(line) or not (20<len(line)<200): continue
            if t0 in line.lower() and any(w in line.lower() for w in
               ["strong","weak","key","squad","batting","bowling","form","balance"]):
                cl = clean(line)
                if cl and cl not in parts: parts.append(cl)
            if len(parts)>=3: break
        if len(parts)>=3: break
    return (f"Sir, {team}: " + ". ".join(parts[:3]) if parts
            else f"Sir, {team}: Balanced squad. Monitor injury news before picks.")

def player_vs_player(batter, bowler):
    res   = search(f"{batter} vs {bowler} IPL T20 record dismissals matchup",mode="text",n=6)
    sents = best_sentences(res,["dismiss","wicket","out","balls","runs","average"])
    if sents:
        exp = get_expert_analysis(f"{batter} vs {bowler}",[],0)
        return f"Sir, {batter} vs {bowler}: " + ". ".join(sents[:2]) + f" {exp}"
    return f"Sir, specific {batter} vs {bowler} record not found."

def batting_scorecard():
    match = get_today_match() or "IPL 2026"
    res   = search(f"{match} IPL 2026 live batting at crease runs balls",mode="news",days="d",n=8)
    sents = best_sentences(res,["batting","batsman","runs off","not out","at crease"])
    kw    = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
    valid = [s for s in sents if kw in s.lower() or "batting" in s.lower()]
    if valid: return "Sir, batting update: " + ". ".join(valid[:2])
    d = get_live_scorecard()
    return (f"Sir, {d.get('runs')}/{d.get('wickets')} in {d.get('overs')} overs." if d
            else "Sir, batting scorecard not in live feed.")

def bowling_scorecard():
    match = get_today_match() or "IPL 2026"
    res   = search(f"{match} IPL 2026 live bowling figures economy today",mode="news",days="d",n=8)
    sents = best_sentences(res,["bowling","bowler","figures","economy","spell","wickets"])
    kw    = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
    valid = [s for s in sents if kw in s.lower() or "bowl" in s.lower()]
    return ("Sir, bowling update: " + ". ".join(valid[:2]) if valid
            else "Sir, bowling scorecard not available right now.")

def match_prediction():
    match = get_today_match()
    if not match: return "Sir, today's match not found."
    res   = search(f"{match} IPL 2026 prediction winner analysis today",mode="text",n=8)
    sents = best_sentences(res,["predict","favourite","win","likely","chance","advantage","stronger"])
    if sents: return f"Sir, prediction for {match}: " + ". ".join(sents[:3])
    t = match.split(" vs ")
    if len(t)==2:
        h = h2h(t[0].strip(), t[1].strip())
        return f"Sir, {match} prediction based on H2H: {h}"
    return f"Sir, prediction for {match} not available."

def over_update():
    match = get_today_match() or "IPL 2026"
    res   = search(f"{match} IPL 2026 last over update runs wickets boundary",mode="news",days="d",n=8)
    sents = best_sentences(res,["over","six","four","wicket","boundary","dot","runs in the"])
    kw    = match.split(" vs ")[0].split()[-1].lower() if " vs " in match else "ipl"
    valid = [s for s in sents if kw in s.lower() or "over" in s.lower()]
    if valid: return "Sir, over update: " + ". ".join(valid[:2])
    msg, _ = live_score()
    return msg or "Sir, over update not available."

def match_momentum():
    d = get_live_scorecard()
    if not d: return "Sir, no live match data."
    rh = MATCH_STATE.get("run_history",[])
    if len(rh)>=3:
        recent = [rh[i]-rh[i-1] for i in range(max(0,len(rh)-3),len(rh)) if rh[i]>rh[i-1]]
        if recent:
            avg_r = sum(recent)/len(recent)
            overall = d.get("run_rate",0)
            if avg_r > overall+1:   mom = "batting team has momentum. Rate picking up."
            elif avg_r < overall-1: mom = "bowling team has momentum. Batting slowing."
            else:                   mom = "evenly poised. No clear momentum."
            return f"Sir, {mom} Recent overs avg {round(avg_r,1)} per over."
    msg,_ = live_score()
    return msg or "Sir, momentum data not enough yet."

# ══════════════════════════════════════════════════════
#  SENTINEL
# ══════════════════════════════════════════════════════
def sentinel(speaker):
    global last_score
    pythoncom.CoInitialize()
    while tracking_active:
        try:
            d = get_live_scorecard()
            if d:
                runs=d.get("runs",0); wkts=d.get("wickets",0)
                ovs=d.get("overs",0.0); rr=d.get("run_rate",0.0)
                if wkts > last_score["wickets"] >= 0:
                    ov_str = f"in {ovs} overs" if ovs>0 else ""
                    msg = f"Sir, wicket has fallen. Score {runs} for {wkts} {ov_str}. "
                    msg += analyze(runs, wkts, ovs, d.get("target",0))
                    print(f"\n*** WICKET: {msg}")
                    speaker.Speak(msg)
                    if int(ovs) not in MATCH_STATE["wicket_overs"]:
                        MATCH_STATE["wicket_overs"].append(int(ovs))
                if last_score["runs"]>0:
                    if runs//50 > last_score["runs"]//50:
                        speaker.Speak(f"Sir, {(runs//50)*50} runs up for batting team.")
                    if rr>12 and last_score["rr"]<=12:
                        speaker.Speak(f"Sir, exceptional run rate of {rr} right now.")
                last_score.update(runs=runs,wickets=wkts,overs=ovs,rr=rr)
        except Exception as e:
            pass
        time.sleep(60)

# ══════════════════════════════════════════════════════
#  VOICE LOOP
# ══════════════════════════════════════════════════════
def jarvis_loop(speaker):
    pythoncom.CoInitialize()

    def speak(text):
        if text:
            print(f"\nJarvis: {text}\n")
            speaker.Speak(str(text))

    def listen_once(t=8):
        with sr.Microphone() as src:
            rec.adjust_for_ambient_noise(src, duration=0.3)
            audio = rec.listen(src, timeout=t, phrase_time_limit=8)
        return rec.recognize_google(audio, language="en-IN").strip()

    threading.Thread(target=sentinel, args=(speaker,), daemon=True).start()
    rec = sr.Recognizer()
    rec.dynamic_energy_threshold = True
    llm = check_llm_status()
    speak(f"Jarvis online sir. IPL 2026 max agent ready. {llm}.")

    while True:
        try:
            with sr.Microphone() as src:
                print("[Listening]")
                rec.adjust_for_ambient_noise(src, duration=0.5)
                audio = rec.listen(src, timeout=10, phrase_time_limit=10)
            print("[Recognizing]")
            cmd = rec.recognize_google(audio, language="en-IN").lower().strip()
            print(f"You said: '{cmd}'")

            if cmd in ["jarvis","hey jarvis","yes jarvis"]:
                speak("Ready sir.")

            # TODAY MATCH
            elif any(w in cmd for w in ["today match","aaj ka match","kiska match","kaun khel","ipl today","which match"]):
                speak("Checking today sir...")
                ans = get_today_match()
                speak(f"Sir, today: {ans}. Want live score?" if ans else "Sir, match not found.")

            # FULL SCORECARD / SITUATION
            elif any(w in cmd for w in ["full score","scorecard","situation","match situation","full update","poori update","kya ho raha","full status"]):
                speak("Analyzing sir...")
                msg, fallback = live_score()
                speak(msg or f"Sir, no live score. Today: {fallback}")

            # QUICK SCORE
            elif any(w in cmd for w in ["score","kya hua","kitne run","live","status","update","kya score"]) and "highest" not in cmd and "auction" not in cmd:
                speak("Fetching sir...")
                msg, fallback = live_score()
                speak(msg or f"Sir, no live match. Today: {fallback}")

            # RUN RATE
            elif any(w in cmd for w in ["run rate","required rate","rrr","current rate","crr"]):
                d = get_live_scorecard()
                if d:
                    speak(f"Sir, run rate {d.get('run_rate')}." +
                          (f" Required {d['req_rate']}." if d.get("req_rate") else "") +
                          (f" {d['balls_left']} balls left." if d.get("balls_left") else ""))
                else: speak("Sir, no live match data.")

            # PLAYER ANALYSIS ML+LLM
            elif any(w in cmd for w in ["analyze","analysis","deep","ml analysis","expert","poora analysis"]):
                player = fp(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                bowl = any(w in cmd for w in ["bowl","wicket","bowling"])
                speak(f"Running ML and LLM for {player} sir...")
                speak(player_analysis(player, bowling=bowl))

            # PLAYER STATS
            elif any(w in cmd for w in ["stats","performance","kaisa khelta","batting stats","runs banaye","innings"]):
                player = fp(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Fetching {player} sir...")
                speak(player_analysis(player))

            # BOWLING STATS
            elif any(w in cmd for w in ["bowling stats","bowling record","kitne wicket","bowling figures","economy rate"]):
                player = fp(cmd)
                if not player:
                    speak("Which bowler sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Fetching {player} bowling sir...")
                speak(player_analysis(player, bowling=True))

            # PLAYER FORM
            elif any(w in cmd for w in ["form","recent form","last 5","kaise chal raha","current form","in form"]):
                player = fp(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(player_form(player))

            # WIN PREDICT
            elif any(w in cmd for w in ["predict","kaun jeetega","win","chance","jeetne","winner","win probability","who will win"]):
                d = get_live_scorecard()
                if d and d.get("runs"):
                    wp  = calculate_win_probability(d["runs"],d.get("wickets",0),d.get("overs",1),d.get("target",185))
                    msg = f"Sir, {wp.get('win_percent')}% win probability for batting team. "
                    msg += analyze(d["runs"],d.get("wickets",0),d.get("overs",1),d.get("target",0))
                    llm = get_match_insight(get_today_match() or "IPL 2026",{**d,"win_percent":wp.get("win_percent",50)})
                    if llm: msg += f" {llm}"
                    speak(msg)
                else:
                    speak("Which player sir? Batting or bowling?")
                    try:
                        pc = listen_once().lower()
                        pl = fp(pc) or pc.strip().title()
                        speak(player_analysis(pl, bowling="bowl" in pc or "wicket" in pc))
                    except: speak("Sir, need live match for win prediction.")

            # MATCH PREDICTION (pre-match)
            elif any(w in cmd for w in ["match prediction","today prediction","who will win today","aaj kaun jeetega","pre match"]):
                speak("Analyzing prediction sir...")
                speak(match_prediction())

            # SCHEDULE
            elif any(w in cmd for w in ["next match","agle match","tomorrow","kal ka","upcoming"]):
                speak("Checking tomorrow sir...")
                speak(get_schedule("tomorrow"))

            elif any(w in cmd for w in ["last match","yesterday","kal hua","pichle","previous"]):
                speak("Checking yesterday sir...")
                speak(get_schedule("yesterday"))

            elif any(w in cmd for w in ["schedule","fixture","kab hai"]):
                speak("Checking schedule sir...")
                speak(get_schedule("today"))

            # POINTS TABLE
            elif any(w in cmd for w in ["points table","standings","ranking","kaun upar","table","leaderboard","playoff"]):
                speak("Fetching standings sir...")
                speak(get_points_table())

            # CAPS
            elif any(w in cmd for w in ["orange cap","top scorer","most runs","leading batsman"]):
                speak("Checking orange cap sir...")
                speak(get_orange_cap())

            elif any(w in cmd for w in ["purple cap","most wickets","leading bowler","top bowler"]):
                speak("Checking purple cap sir...")
                speak(get_purple_cap())

            # PITCH
            elif any(w in cmd for w in ["pitch","pitch report","surface","ground report"]):
                speak("Fetching pitch report sir...")
                speak(pitch_report())

            # WEATHER
            elif any(w in cmd for w in ["weather","rain","mausam","barish","temperature","dew","forecast"]):
                speak("Checking weather sir...")
                speak(weather_report())

            # TOSS
            elif any(w in cmd for w in ["toss","toss analysis","why bat","why field","toss decision"]):
                speak("Analyzing toss sir...")
                speak(toss_analysis())

            # PLAYING 11
            elif any(w in cmd for w in ["playing 11","playing eleven","eleven","starting xi"]):
                p11 = get_playing11()
                speak(p11 if p11 else "Sir, playing eleven not announced yet.")

            # INJURY
            elif any(w in cmd for w in ["injury","injured","fit","fitness","ruled out","kaun fit"]):
                teams = ft(cmd)
                speak(get_injury_news(teams[0] if teams else None))

            # NEWS
            elif any(w in cmd for w in ["news","latest","highlights","headlines","breaking","updates"]):
                speak("Fetching news sir...")
                speak(get_ipl_news())

            # FANTASY
            elif any(w in cmd for w in ["fantasy","dream11","best 11","fantasy team","who to pick"]):
                speak("Analyzing fantasy sir...")
                speak(fantasy_team())

            # AUCTION
            elif any(w in cmd for w in ["auction","price","crore","kitne mein","salary","worth"]):
                player = fp(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(auction_value(player))

            # TEAM STRENGTH
            elif any(w in cmd for w in ["team strength","squad analysis","team form","kaisi team"]):
                teams = ft(cmd)
                if teams: speak(team_strength(teams[0]))
                else:
                    speak("Which team sir?")
                    try:
                        t = ft(listen_once())
                        speak(team_strength(t[0]) if t else "Team not found.")
                    except: continue

            # COMPARE
            elif any(w in cmd for w in ["compare","mukabla","kaun behtar","better player"]):
                plist = []
                for k,v in IPL_PLAYERS.items():
                    if k in cmd and v not in plist: plist.append(v)
                if len(plist)>=2:
                    p1,p2 = plist[0],plist[1]
                else:
                    speak("Two players with 'and' please sir.")
                    try:
                        said = listen_once()
                        if " and " in said.lower():
                            pts = said.lower().split(" and ")
                            p1  = fp(pts[0]) or pts[0].strip().title()
                            p2  = fp(pts[1]) or pts[1].strip().title()
                        else: speak("Use 'and' sir."); continue
                    except: continue
                speak(f"Comparing {p1} and {p2} sir...")
                speak(player_analysis(p1))
                speak(f"Now {p2}:")
                speak(player_analysis(p2))

            # H2H TEAMS
            elif any(w in cmd for w in ["head to head","h2h","history between"]):
                teams = ft(cmd)
                if len(teams)>=2:
                    speak(h2h(teams[0],teams[1]))
                else: speak("Name two teams sir. Example: MI vs CSK.")

            # BOWLERS AGAINST BATSMAN
            elif any(w in cmd for w in ["kaun out karega","weakness","kamzori","dismiss","out kar sakta","nemesis"]):
                player = fp(cmd)
                if not player:
                    speak("Which batsman sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(bowlers_against(player))

            # PLAYER VS PLAYER
            elif any(w in cmd for w in ["player vs","vs bowler","matchup","face off"]):
                plist = [v for k,v in IPL_PLAYERS.items() if k in cmd]
                if len(plist)>=2: speak(player_vs_player(plist[0],plist[1]))
                else: speak("Name two players sir.")

            # MILESTONE
            elif any(w in cmd for w in ["milestone","record close","approaching record","kitne runs chahiye"]):
                player = fp(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(player_milestone(player))

            # TOP PERFORMERS
            elif any(w in cmd for w in ["top performers","best today","who performed","standout","man of the match"]):
                speak(top_performers())

            # MATCH SUMMARY
            elif any(w in cmd for w in ["match summary","innings summary","what happened","full summary","kya hua aaj"]):
                speak(match_summary())

            # MOMENTUM
            elif any(w in cmd for w in ["momentum","kiska momentum","who has momentum","match flow"]):
                speak(match_momentum())

            # OVER UPDATE
            elif any(w in cmd for w in ["over update","last over","this over","over mein","kaun over"]):
                speak(over_update())

            # WHO IS BATTING
            elif any(w in cmd for w in ["who is batting","batting scorecard","at crease","kaun batting"]):
                speak(batting_scorecard())

            # WHO IS BOWLING
            elif any(w in cmd for w in ["who is bowling","bowling scorecard","kaun bowling"]):
                speak(bowling_scorecard())

            # IPL RECORDS
            elif any(w in cmd for w in ["ipl records","ipl 2026 record","most sixes","fastest fifty","season record"]) or ("highest" in cmd and "score" in cmd and "live" not in cmd):
                speak(ipl_records())

            # GRAPHS
            elif any(w in cmd for w in ["momentum graph","dashboard","analytics","match graph","full graph"]):
                speak("Generating analytics dashboard sir...")
                GRAPH_QUEUE.put(("momentum",None))

            elif any(w in cmd for w in ["batting graph","run graph","batting chart"]):
                player = fp(cmd)
                if not player:
                    speak("Which batsman sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Generating {player} batting graph sir...")
                GRAPH_QUEUE.put(("batting",player))

            elif any(w in cmd for w in ["bowling graph","wicket graph","bowling chart"]):
                player = fp(cmd)
                if not player:
                    speak("Which bowler sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak(f"Generating {player} bowling graph sir...")
                GRAPH_QUEUE.put(("bowling",player))

            elif any(w in cmd for w in ["graph","chart","dikhao"]):
                player = fp(cmd)
                if not player:
                    speak("Which player sir?")
                    try: player = fp(listen_once()) or listen_once().strip().title()
                    except: continue
                speak("Batting or bowling sir?")
                try:
                    gt = listen_once().lower()
                    GRAPH_QUEUE.put(("batting" if any(w in gt for w in ["bat","run"]) else "bowling", player))
                except: GRAPH_QUEUE.put(("batting",player))

            # HELP
            elif any(w in cmd for w in ["help","kya kar sakta","features","commands","what can you do"]):
                speak("Sir, commands: Score. Full scorecard. Match situation. Run rate. Today match. Toss analysis. Pitch. Weather. Schedule. Next match. Last match. Points table. Orange cap. Purple cap. Virat analysis ML plus LLM. Virat form. Virat milestone. Win prediction. Match prediction. Compare Virat and Rohit. Fantasy team. Auction price. Team strength. MI vs CSK head to head. Virat ko kaun out kar sakta. Top performers. Match summary. Match momentum. Over update. Batting scorecard. Bowling scorecard. IPL records. News. Injury. Batting graph. Bowling graph. Momentum dashboard. Exit.")

            # EXIT
            elif any(w in cmd for w in ["exit","stop","bye","goodbye","band karo","shutdown","shut down"]):
                speak("Goodbye sir. Jarvis signing off.")
                os._exit(0)

        except sr.WaitTimeoutError: pass
        except sr.UnknownValueError: pass
        except Exception as ex:
            print(f"[Loop] {ex}")
            time.sleep(1)

# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    print("=" * 70)
   
    print(f"  {check_llm_status()}")
    print("=" * 70)

    vt = threading.Thread(target=jarvis_loop, args=(speaker,), daemon=True)
    vt.start()

    while True:
        try:
            task, arg = GRAPH_QUEUE.get(timeout=1)
            if task == "momentum":
                draw_momentum_dashboard(MATCH_STATE)
            elif task == "batting":
                c = PLAYER_CACHE.get(arg.lower(),{}) if arg else {}
                sc = c.get("runs",[])
                ml = c.get("ml")
                if not sc:
                    raw = get_player_raw_data(arg)
                    sc  = raw.get("scores",[])
                    ml  = predict_future_score(sc) if len(sc)>=3 else None
                draw_batting_graph(arg, sc, ml)
            elif task == "bowling":
                c  = PLAYER_CACHE.get(arg.lower(),{}) if arg else {}
                wk = c.get("wickets",[])
                ec = c.get("economies",[])
                ml = c.get("ml")
                if not wk:
                    raw = get_player_raw_data(arg)
                    wk  = raw.get("wickets",[])
                    ec  = raw.get("economies",[])
                    ml  = predict_future_wickets(wk,ec) if len(wk)>=3 else None
                draw_bowling_graph(arg, wk, ec, ml)
        except queue.Empty: pass
        except Exception as e: print(f"[Graph] {e}")
    #naya code
     
