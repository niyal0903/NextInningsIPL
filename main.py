import re
import time
import os
import threading
import pythoncom
import win32com.client
import speech_recognition as sr
from ddgs import DDGS

# --- GLOBAL STATE FOR SENTINEL MODE ---
last_score_state = {"wickets": 0, "runs": 0, "match_name": ""}
tracking_active = True

# ══════════════════════════════════════════════════════════
#  CORE ENGINE: LIVE DATA FETCH & ANALYTICS
# ══════════════════════════════════════════════════════════
def get_live_data():
    try:
        with DDGS() as ddgs:
            # Sirf 24 ghante ka data aur India region focus
            q = "IPL 2026 live score today match scorecard"
            results = list(ddgs.news(q, region="in-en", timelimit="d", max_results=5))
            
            for r in results:
                text = r.get('title', '') + " " + r.get('body', '')
                # Score pattern search: e.g. "145/3 (16.4)"
                match = re.search(r'(\d{1,3})/(\d{1,2})', text)
                if match:
                    runs = int(match.group(1))
                    wickets = int(match.group(2))
                    return {"runs": runs, "wickets": wickets, "raw": text[:100]}
    except:
        pass
    return None

def predict_win(runs, wickets, target=200): # Target default 200 agar na mile
    chance = 100 - (wickets * 10) - ((target - runs) / 2)
    return max(5, min(95, round(chance)))

# ══════════════════════════════════════════════════════════
#  SENTINEL THREAD: BACKGROUND MONITORING
# ══════════════════════════════════════════════════════════
def sentinel_monitor(speaker):
    global last_score_state
    pythoncom.CoInitialize()
    
    while tracking_active:
        data = get_live_data()
        if data:
            # Check for Wicket
            if data['wickets'] > last_score_state['wickets']:
                msg = f"Sir, alert! A wicket has fallen. Current score is {data['runs']} for {data['wickets']}."
                print(f"\n🚨 ALERT: {msg}")
                speaker.Speak(msg)
            
            # Check for Milestone (Every 50 runs)
            if data['runs'] // 50 > last_score_state['runs'] // 50:
                msg = f"Sir, the batting team has crossed { (data['runs'] // 50) * 50 } runs."
                speaker.Speak(msg)

            last_score_state['runs'] = data['runs']
            last_score_state['wickets'] = data['wickets']
            
        time.sleep(60) # Har 1 minute mein check karega

# ══════════════════════════════════════════════════════════
#  MAIN JARVIS INTERFACE
# ══════════════════════════════════════════════════════════
def jarvis_main():
    pythoncom.CoInitialize()
    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    
    def speak(text):
        print(f"Jarvis: {text}")
        speaker.Speak(text)

    # Start Sentinel in Background
    monitor_thread = threading.Thread(target=sentinel_monitor, args=(speaker,))
    monitor_thread.daemon = True
    monitor_thread.start()

    rec = sr.Recognizer()
    speak("Jarvis is online. Sentinel monitoring and win-prediction systems are active.")

    while True:
        try:
            with sr.Microphone() as source:
                print("\n🎤 Listening...")
                rec.adjust_for_ambient_noise(source, duration=0.5)
                audio = rec.listen(source, timeout=10)

            command = rec.recognize_google(audio, language="en-IN").lower()
            print(f"User: {command}")

            # 1. LIVE SCORE COMMAND
            if any(w in command for w in ["score", "kya hua", "status"]):
                speak("Accessing live feed...")
                data = get_live_data()
                if data:
                    speak(f"Sir, current score is {data['runs']} runs for {data['wickets']} wickets.")
                else:
                    speak("Sir, live data is currently being refreshed.")

            # 2. PREDICTION COMMAND
            elif any(w in command for w in ["predict", "kaun jeetega", "prediction", "jeetne ke chance"]):
                data = get_live_data()
                if data:
                    prob = predict_win(data['runs'], data['wickets'])
                    speak(f"Sir, analyzing match dynamics. The batting team has a {prob} percent chance of winning.")
                else:
                    speak("Not enough data for a stable prediction yet, sir.")

            # 3. GUJARATI/HINDI MIXED COMMANDS
            elif "kem che" in command:
                speak("Maja ma chu sir! Match update ready che.")

            elif "exit" in command or "bye" in command:
                speak("Shutting down IPL systems. Goodbye sir.")
                os._exit(0)

        except Exception:
            pass

if __name__ == "__main__":
    jarvis_main()





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